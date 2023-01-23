from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .channel import Channel


class Topic:
    """
    This class represents a topic of a channel.
    """
    def __init__(self):
        self._description = None
        self._channel = None
        self._keywords = []

    @property
    def keywords(self):
        """
        :type: [str]
        """
        return self._keywords

    @property
    def description(self):
        """
        :type: str
        """
        return self._description

    @property
    def channel(self):
        """
        :type: Channel
        """
        return self._channel

    @keywords.setter
    def keywords(self, keywords: [str]):
        """
        Set the keywords of the topic.

        :param keywords: The keywords of the topic
        """
        self._keywords = keywords

    @description.setter
    def description(self, description: str):
        """
        Set the description of the topic.

        :param description: The description of the topic
        """
        self._description = description

    @channel.setter
    def channel(self, channel: Channel):
        """
        Set the channel of the topic.

        :param channel: The channel of the topic
        """
        self._channel = channel

    def deserialize(self, data: dict, channel: Channel):
        """
        Deserialize a topic into a Topic object.

        :param data: The JSON topic to deserialize
        :param channel: The channel of the topic
        :return: The deserialized Topic object
        """
        self._keywords = [keyword for keyword in data['keywords']]
        self._description = data['description']
        self._channel = channel

        return self
