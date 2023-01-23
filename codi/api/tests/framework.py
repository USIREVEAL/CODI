import json

from unittest import TestCase

from codi.api.model.input.member import Member
from codi.api.model.input.message import Message
from codi.api.model.input.community import Community


class Framework(TestCase):
    @staticmethod
    def _read_data_from_fixtures(file_path: str):
        with open(file_path) as f:
            return json.load(f)

    @staticmethod
    def _get_community_object(data: dict):
        """
        Get the community object from the given data.

        :param data: The data to use
        :return: The community object
        """
        return Community().deserialize(data)

    @staticmethod
    def _get_community_members_and_messages(data: dict):
        """
        Get the users and messages from the given data.

        :param data: The JSON data to use
        :return: The users and messages
        """
        community = Community().deserialize(data)

        return community.members, community.channels['575214823022002177'].messages

    @staticmethod
    def _get_blocks_and_messages(data: dict, function, blocks_in: str, members: bool = False):
        """
        Get the content blocks from the given message text.

        :param data: The data to use
        :param function: The function to call
        :param blocks_in: The field to read from. This can either be 'content' or 'attachments'.
        :param members: Whether we are testing member mentions or not
        :return: The blocks and modified messages
        """
        blocks = []
        messages = []

        messages_data = data['messages']

        for message in messages_data:
            links = []

            if members:
                members = {}
                member_data = data['members']

                for member in member_data:
                    member_instance = Member().deserialize(member)
                    members[member_instance.uuid] = member_instance

                links, modified_message = function(members, message[blocks_in])
                messages.append(modified_message)
            elif blocks_in == 'content':
                links, modified_message = function(message[blocks_in])
                messages.append(modified_message)
            else:
                try:
                    links = function(message[blocks_in], None)
                except KeyError:
                    pass

            blocks.append(links)

        return blocks, messages if blocks_in == 'content' else blocks

    @staticmethod
    def _get_feature(function, message1: Message, message2: Message, community: Community = None):
        """
        Get the users and messages from the given data.

        :param function: The function to call
        :param message1: The first message
        :param message2: The second message
        :param community: The community to use
        :return: The users and messages
        """
        from codi.api.model.disentanglement.content import Repeat

        return function(message1, message2) if function != Repeat.extract else function(message1, message2, community)
