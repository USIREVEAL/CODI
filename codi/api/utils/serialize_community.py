from __future__ import annotations

import datetime

from ..model.input.content import *
from ..model.input.mention import *
from ..model.input.channel import Channel
from ..model.input.message import Message
from ..model.disentanglement.conversation import Conversation

if TYPE_CHECKING:
    from ..model.input.community import Community


def serialize_community(community: Community):
    out = {
        'platform': community.platform,
        'id': community.uuid,
        'name': community.name,
        'members': [],
        'authors': [],
        'channels': []
    }

    serialize_members(community, out)
    serialize_authors(community, out)
    serialize_channels(community, out)

    return out


def serialize_members(community: Community, out: dict):
    for member in community.members:
        out['members'].append({
            'id': community.members[member].uuid,
            'name': community.members[member].username
        })


def serialize_authors(community: Community, out: dict):
    for author in community.authors:
        out['authors'].append({
            'id': community.authors[author].uuid,
            'name': community.authors[author].username,
            'messagesIds': [message.uuid for message in community.members[author].messages]
        })


def serialize_channels(community: Community, out: dict):
    for channel in community.channels:
        out['channels'].append({
            'id': community.channels[channel].uuid,
            'path': community.channels[channel].path,
            'topics': serialize_topics(community.channels[channel]),
            'messages': serialize_messages(community.channels[channel])
        })


def serialize_topics(channel: Channel):
    topics = []

    for i, topic in enumerate(channel.topics):
        topics.append({
            'description': channel.topics[i].description,
            'keywords': channel.topics[i].keywords
        })

    return topics


# def serialize_conversations(channel: Channel):
#     conversations = []
#
#     for conversation in channel.messages:
#         conversations.append({
#             'id': channel.messages[conversation].uuid,
#             'messages': serialize_messages(channel.messages[conversation])
#         })
#
#     return conversations


def serialize_messages(conversation: Conversation):
    messages = []

    for message in conversation.messages:
        if not isinstance(conversation.messages[message].timestamp, int):
            timestamp = datetime.datetime.timestamp(conversation.messages[message].timestamp)
        else:
            timestamp = conversation.messages[message].timestamp

        messages.append({
            'id': conversation.messages[message].uuid,
            'authorId': conversation.messages[message].author.uuid,
            'author_username': conversation.messages[message].author.username,
            'timestamp': timestamp,
            'conversationId': conversation.messages[message].conversation,
            'processable_text': conversation.messages[message].processable_text,
            'text': conversation.messages[message].text,
            'attachments': serialize_attachments(conversation.messages[message]),
            'content': serialize_contents(conversation.messages[message])
        })

    return messages


def serialize_attachments(message: Message):
    attachments = []

    for i, attachment in enumerate(message.attachments):
        attachments.append({
            'urls': message.attachments[i].url,
        })

    return attachments


def serialize_contents(message: Message):
    contents = []

    for i, content in enumerate(message.contents):
        contents.append({
            'type': str(message.contents[i].__class__.__name__).lower(),
            'start_position': message.contents[i].start_position,
            'end_position': message.contents[i].end_position,
        })

        if isinstance(message.contents[i], Text):
            contents[i]['text'] = message.contents[i].text
        elif isinstance(message.contents[i], Link) or isinstance(content, Multimedia):
            contents[i]['urls'] = message.contents[i].url
        elif isinstance(message.contents[i], Emoji):
            contents[i]['unicode'] = message.contents[i].unicode
        elif isinstance(message.contents[i], Code):
            contents[i]['code'] = message.contents[i].code
        elif isinstance(message.contents[i], MemberMention):
            contents[i]['memberId'] = message.contents[i].member.uuid
            message.text = message.text.replace('__MEMBER_MENTION__',
                                                f'{message.contents[i].member.username}:',
                                                1)
        elif isinstance(message.contents[i], ChannelMention):
            contents[i]['channelId'] = message.contents[i].channel.uuid
            message.text = message.text.replace('__CHANNEL_MENTION__',
                                                f'{message.contents[i].channel.path}:',
                                                1)

    return contents
