from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .member import Member
from .content import Content

if TYPE_CHECKING:
    from .message import Message
    from .channel import Channel


class Mention(Content):
    """
    This class represents a mention in a channel.
    """
    pass


class MemberMention(Mention):
    """
    This class represents a member mention in a channel.
    """
    def __init__(self):
        super().__init__()
        self._member = None

    def __str__(self, content=None):
        return super.__str__(self._member.username)

    @property
    def member(self):
        """
        :type: Member
        """
        return self._member

    @member.setter
    def member(self, member: Member):
        """
        Set the member of this mention.

        :param member: The member of this mention
        """
        self._member = member

    def deserialize(self,
                    start_index: int,
                    end_index: int,
                    message: Message = None,
                    members: dict = None,
                    member_id: str = None,
                    member_name: str = None):
        """
        Deserialize a mention into a MemberMention object.

        :param start_index: The start index of the mention
        :param end_index: The end index of the mention
        :param message: The message object
        :param members: The members of the community
        :param member_id: The id of the member of this mention
        :param member_name: The name of the member of this mention
        :return: The MemberMention object
        """
        super().deserialize(start_index, end_index, message)

        try:
            self._member = members[member_id]
        except KeyError:
            mention = Member()
            mention.uuid = member_id
            mention.username = member_name
            mention.community = message.channel.community

            members[member_id] = mention
            self._member = members[member_id]

        return self

    @classmethod
    def retrieve(cls, members: dict, message: str, message_obj: Message = None):
        """
        Retrieve the list of member mentions in a message.

        :param members: The members of the community
        :param message: The message to retrieve the mentions from
        :param message_obj: The message object
        :return: The list of mentions of a member in a channel
        """
        mentions = []
        user_mention_regex = re.compile(r'<@!?(\d*)>')

        for user_mention in user_mention_regex.finditer(message):
            user_mention_id = user_mention.group(1)
            mentions.append(MemberMention().deserialize(user_mention.start(),
                                                        user_mention.end(),
                                                        message_obj,
                                                        members,
                                                        user_mention_id))

            pattern = f'<@!{user_mention_id}>' if (f'<@!{user_mention_id}>' in message) else f'<@{user_mention_id}>'
            message = message.replace(pattern, f'__MEMBER_MENTION__', 1)

        return mentions, message


class SlackMemberMention(MemberMention):
    """
    This class represents a member mention in a Slack message.
    """
    def deserialize(self,
                    start_index: int,
                    end_index: int,
                    message: Message = None,
                    members: dict = None,
                    member_id: str = None,
                    member_name: str = None):
        """
        Deserialize a mention into a SlackMemberMention object.

        :param start_index: The start index of the mention
        :param end_index: The end index of the mention
        :param message: The message object
        :param members: The members of the community
        :param member_id: The id of the member of this mention
        :param member_name: The name of the member of this mention
        :return: The SlackMemberMention object
        """
        return super().deserialize(start_index, end_index, message, members, member_id, member_name)

    @classmethod
    def retrieve(cls, members: dict, message: str, message_obj: Message = None):
        """
        Retrieve the list of Slack member mentions in a message.

        :param members: The members of the community
        :param message: The message to retrieve the mentions from
        :param message_obj: The message object
        :return: The list of Slack member mentions
        """
        mentions = []
        slack_user_mention_regex = re.compile(r'<@U([^\s]*)\|([^\s]*)>')

        for slack_user_mention in slack_user_mention_regex.finditer(message):
            slack_user_mention_id = slack_user_mention.group(1)
            slack_user_mention_name = slack_user_mention.group(2)
            mentions.append(SlackMemberMention().deserialize(slack_user_mention.start(),
                                                             slack_user_mention.end(),
                                                             message_obj,
                                                             members,
                                                             slack_user_mention_id,
                                                             slack_user_mention_name))

            pattern = f'<@U{slack_user_mention_id}|{slack_user_mention_name}>'
            message = message.replace(pattern, f'__MEMBER_MENTION__', 1)

        return mentions, message


class ChannelMention(Mention):
    """
    This class represents a channel mention in a message.
    """
    def __init__(self):
        super().__init__()
        self._channel = None

    def __str__(self, content=None):
        return super.__str__(self._channel.path)

    @property
    def channel(self):
        """
        :type: Channel
        """
        return self._channel

    @channel.setter
    def channel(self, channel: Channel):
        """
        Set the channel of this mention.

        :param channel: The channel of this mention
        """
        self._channel = channel

    def deserialize(self,
                    start_index: int,
                    end_index: int,
                    message: Message = None,
                    channels: dict = None,
                    channel_id: str = None,
                    channel_name: str = None,
                    uninitialized_channels: dict = None):
        """
        Deserialize a mention into a ChannelMention object.

        :param start_index: The start index of the mention
        :param end_index: The end index of the mention
        :param message: The message object
        :param channels: The channels of the community
        :param channel_id: The channel of this mention
        :param channel_name: The name of the channel of this mention
        :param uninitialized_channels: The uninitialized channels of the community
        :return: The ChannelMention object
        """
        super().deserialize(start_index, end_index, message)

        try:
            self._channel = channels[channel_id]
        except KeyError:
            from .channel import Channel

            new_channel = Channel()
            new_channel.uuid = channel_id
            new_channel.path = channel_name
            new_channel.community = message.channel.community

            uninitialized_channels[channel_id] = new_channel
            self._channel = new_channel

        return self

    @classmethod
    def retrieve(cls, channels: dict, message: str, uninitialized_channels: dict, message_obj: Message = None):
        """
        Retrieve the list of channel mentions from a message.

        :param channels: The channels of the community
        :param message: The message to retrieve the mentions from
        :param uninitialized_channels: The uninitialized channels of the community
        :param message_obj: The message object
        :return: The list of mentions of a member in a channel
        """
        mentions = []
        channel_mention_regex = re.compile(r'<#(\d*)>')

        for channel_mention in channel_mention_regex.finditer(message):
            channel_mention_id = channel_mention.group(1)
            mentions.append(ChannelMention().deserialize(channel_mention.start(),
                                                         channel_mention.end(),
                                                         message_obj,
                                                         channels,
                                                         channel_mention_id,
                                                         uninitialized_channels=uninitialized_channels))

            pattern = f'<#{channel_mention_id}>'
            message = message.replace(pattern, f'__CHANNEL_MENTION__', 1)

        return mentions, message


class SlackChannelMention(ChannelMention):
    """
    This class represents a Slack channel mention.
    """
    def deserialize(self,
                    start_index: int,
                    end_index: int,
                    message: Message = None,
                    channels: dict = None,
                    channel_id: str = None,
                    channel_name: str = None,
                    uninitialized_channels: dict = None):
        """
        Deserialize a mention into a ChannelMention object.

        :param start_index: The start index of the mention
        :param end_index: The end index of the mention
        :param message: The message object
        :param channels: The channels of the community
        :param channel_id: The channel of this mention
        :param channel_name: The name of the channel of this mention
        :param uninitialized_channels: The uninitialized channels of the community
        :return: The ChannelMention object
        """
        return super().deserialize(start_index,
                                   end_index,
                                   message,
                                   channels,
                                   channel_id,
                                   channel_name,
                                   uninitialized_channels)

    @classmethod
    def retrieve(cls, channels: dict, message: str, uninitialized_channels: dict, message_obj: Message = None):
        """
        Retrieve the list of channel mentions from a message.

        :param channels: The channels of the community
        :param message: The message to retrieve the mentions from
        :param uninitialized_channels: The uninitialized channels of the community
        :param message_obj: The message object
        :return: The list of mentions of a member in a channel
        """
        mentions = []
        slack_channel_mention_regex = re.compile(r'<#C([^\s]*)\|([^\s]*)>')

        for slack_channel_mention in slack_channel_mention_regex.finditer(message):
            slack_channel_id = slack_channel_mention.group(1)
            slack_channel_name = slack_channel_mention.group(2)
            mentions.append(SlackChannelMention().deserialize(slack_channel_mention.start(),
                                                              slack_channel_mention.end(),
                                                              message_obj,
                                                              channels,
                                                              slack_channel_id,
                                                              slack_channel_name,
                                                              uninitialized_channels))

            pattern = f'<#C{slack_channel_id}|{slack_channel_name}>'
            message = message.replace(pattern, f'__CHANNEL_MENTION__', 1)

        return mentions, message


# TODO: Add model for roles mentions
# TODO: Add model for special mentions
