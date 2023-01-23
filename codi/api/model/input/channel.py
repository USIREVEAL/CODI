from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

from .topic import Topic
from .entity import Entity
from .message import Message

if TYPE_CHECKING:
    from .community import Community


class Channel(Entity):
    """
    This class represents a channel in a community.
    """
    def __init__(self):
        super().__init__()
        self._path = None
        self._community = None
        self._topics = []
        self._messages = {}

    @property
    def path(self):
        """
        :type: str
        """
        return self._path

    @property
    def community(self) -> Community:
        """
        :type: Community
        """
        return self._community

    @property
    def topics(self):
        """
        :type: [Topic]
        """
        return self._topics

    @property
    def messages(self):
        """
        :type: [Message]
        """
        return self._messages

    @path.setter
    def path(self, path: str):
        """
        Set the path of the channel.

        :param path: The path of the channel
        """
        self._path = path

    @community.setter
    def community(self, community: Community):
        """
        Set the community of the channel.

        :param community: The community of the channel
        """
        self._community = community

    @topics.setter
    def topics(self, topics: [Topic]):
        """
        Set the topics of the channel.

        :param topics: The topics of the channel
        """
        self._topics = topics

    @messages.setter
    def messages(self, messages: [Message]):
        """
        Set the messages of the channel.

        :param messages: The messages of the channel
        """
        self._messages = messages

    def deserialize(self, data: dict, members: dict = None, community: Community = None):
        """
        Deserialize a channel into a Channel object.

        :param data: The JSON channel to be deserialized
        :param members: A dictionary of the community members
        :param community: The community of the channel
        :return: The deserialized Channel object
        """
        super().deserialize(data)

        self._path = data['path']
        self._community = community

        try:
            self._topics = [Topic().deserialize(topic, self) for topic in data['topics']]
        except KeyError:
            self._topics = []

        return self

    def time_sorted_messages(self) -> List[Message]:
        return sorted(self.messages.values(), key=lambda message: message.timestamp)

    def as_annot(self, filename):
        """Export this channel messages in .annot format.
        Useful for compatibility with Elsner-Charniak modified algorithm and files.

        :filename: name of the file to save. Should include .annot extension."""
        with open(filename, 'w') as file:
            first_message = True
            for message in self.time_sorted_messages():
                # FIXME Marco fix for timestamps other than datetime.datetime
                if first_message:
                    base_time = message.timestamp
                    first_message = False

                clean_text = message.original_text.replace('\n', ' ')
                clean_text = clean_text.replace('\r', ' ')
                # FIXME use facilities provided by the Mention class
                author_mentions = re.findall(r'<@!?(\d*)>', clean_text)
                if author_mentions is not None:
                    for author in author_mentions:
                        try:
                            new_name = self.community.authors[author].cleaned_username
                        except KeyError:
                            new_name = 'Author_' + author
                        clean_text = re.sub('<@!?' + author + '>',
                                            '' + new_name + ':',
                                            clean_text)
                clean_name = message.author.cleaned_username
                # TODO add replies
                file.write(f"{message.conversation if message.conversation is not None else 'T1234'} "
                           f"{int((message.timestamp - base_time).total_seconds())} {clean_name} :  "
                           f"{clean_text}\n")

