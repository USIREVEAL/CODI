from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .entity import Entity

if TYPE_CHECKING:
    from .message import Message
    from .community import Community


class Member(Entity):
    """
    This class represents a member of a community.
    """
    def __init__(self):
        super().__init__()
        self._username = None
        self._community = None

    @property
    def username(self) -> str:
        """
        :type: str
        """
        return self._username

    @property
    def cleaned_username(self) -> str:
        name = self.username
        name = re.sub(r'[^A-z]', '', name)
        return name.capitalize().encode("ascii", "ignore").decode("ascii")

    @property
    def community(self) -> Community:
        """
        :type: Community
        """
        return self._community

    @username.setter
    def username(self, username: str):
        """
        Set the username of the member.

        :param username: The username of the member
        """
        self._username = username

    @community.setter
    def community(self, community: Community):
        """
        Set the community of the member.

        :param community: The community of the member
        """
        self._community = community

    def deserialize(self, data: dict, community: Community = None):
        """
        Deserialize the data into a Member object.

        :param data: The data to deserialize
        :param community: The community object
        """
        super().deserialize(data)
        self._username = data['name']
        self._community = community

        return self


class Author(Member):
    """
    This class represents a member of a community who has written at least one message.
    """
    def __init__(self):
        super().__init__()
        self._messages = None

    @property
    def messages(self):
        """
        :type: [Message]
        """
        return self._messages

    @messages.setter
    def messages(self, messages: [Message]):
        """
        Set the messages of the author.

        :param messages: The messages of the author
        """
        self._messages = messages
