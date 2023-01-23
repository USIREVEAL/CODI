from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message


class Attachment:
    """
    This class represents an attachment in a message.
    """
    def __init__(self):
        self._url = None
        self._message = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.__class__}: {self._url}"

    @property
    def url(self):
        """
        :type: str
        """
        return self._url

    @property
    def message(self):
        """
        :type: Message
        """
        return self._message

    @url.setter
    def url(self, url: str):
        """
        Set the URL of the attachment.

        :param url: The URL of the attachment
        """
        self._url = url

    @message.setter
    def message(self, message: Message):
        """
        Set the message of the attachment.

        :param message: The message of the attachment
        """
        self._message = message

    def deserialize(self, url: str = None, message: Message = None):
        """
        Deserialize an attachment into an Attachment object.

        :param url: The URL of the attachment
        :param message: The message of the attachment
        :return: The deserialized attachment
        """

        self._url = url
        self._message = message

        return self

    @classmethod
    def retrieve_attachments(cls, attachments: dict, message: Message):
        """
        Retrieve a list of attachments from a dictionary.

        :param attachments: The dictionary containing the attachments
        :param message: The message of the attachments
        :return: The list of attachments
        """
        return [Attachment().deserialize(attachment['url'], message) for attachment in attachments]
