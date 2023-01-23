import os
import json
import pickle
import configparser
from typing import Dict

from .entity import Entity
from .channel import Channel
from .message import Message
from .member import Member, Author
from ...utils.serialize_community import serialize_community


class Community(Entity):
    """
    This class represents a community.
    """
    def __init__(self):
        super().__init__()
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), '../../../../config.ini'))

        self._platform = None
        self._name = None
        self._members = {}
        self._channels = {}
        self._authors = {}
        self._constants = config['constants']

    @property
    def platform(self):
        """
        :type: str
        """
        return self._platform

    @property
    def name(self):
        """
        :type: str
        """
        return self._name

    @property
    def members(self):
        """
        :type: [Member]
        """
        return self._members

    @property
    def channels(self):
        """
        :type: [Channel]
        """
        return self._channels

    @property
    def authors(self) -> Dict[str, Author]:
        """
        :type: Dict[str, Author]
        """
        return self._authors

    @platform.setter
    def platform(self, platform: str):
        """
        Set the members of the community.

        :param platform: The name of the platform
        """
        self._platform = platform

    @name.setter
    def name(self, name: str):
        """
        Set the name of the community.

        :param name: The name of the community
        """
        name = name.lower().replace(' ', '-')
        self._name = name

    @members.setter
    def members(self, members: [Member]):
        """
        Set the members of the community.

        :param members: The members of the community
        """
        self._members = members

    @channels.setter
    def channels(self, channels: [Channel]):
        """
        Set the channels of the community.

        :param channels: The channels of the community
        """
        self._channels = channels

    @authors.setter
    def authors(self, authors: [Author]):
        """
        Set the authors of the community.

        :param authors: The authors of the community
        """
        self._authors = authors

    def _save(self):
        """
        Save the community to the data/ directory. If the community is new, it will be created. If the community
        already exists, it will be overwritten. A maximum of "_max_communities" different communities can be kept in
        the data/ directory at once.
        """
        path = os.path.join(os.path.dirname(__file__), '../../../../data')

        # Check if the `data/` directory exists
        if not os.path.exists(path):
            os.makedirs(path)

        _, _, files = next(os.walk(path))

        # Remove the old community file if it exists
        if f"{self._name}.pickle" in files:
            os.remove(os.path.join(path, f"{self._name}.pickle"))
        elif len(files) >= int(self._constants['max saved communities']):
            raise Exception('Maximum number of pickled communities reached')

        # Save the newly created community
        with open(os.path.join(path, f'./{self._name}.pickle'), 'wb') as f:
            pickle.dump(self, f)

    def save_json(self, op_type: int, statistics: dict = None, gold=None):
        """
        Save the community into a JSON file.

        :param op_type: Indicates the operation
                        0 for training
                        1 for validation
                        2 for prediction
        :param statistics: The statistics of the prediction or validation
        :param gold: It is the gold set of conversations used in validation
        """
        community_mod = serialize_community(self)
        path = os.path.join(os.path.dirname(__file__), '../../training/tmp/json')

        if gold:
            community_mod['gold'] = gold

        if op_type == 1 or op_type == 2:
            community_mod['statistics'] = statistics

        match op_type:
            case 0:
                community_mod['type'] = 'training'
            case 1:
                community_mod['type'] = 'validation'
            case 2:
                community_mod['type'] = 'prediction'

        # Check if the `tmp/` directory exists
        if not os.path.exists(path):
            os.makedirs(path)

        _, _, files = next(os.walk(path))

        # Remove the old community file if it exists
        if f'latest-{community_mod["type"]}.json' in files:
            os.remove(os.path.join(path, f'latest-{community_mod["type"]}.json'))

        # Save the newly created community
        with open(os.path.join(path, f'latest-{community_mod["type"]}.json'), 'w') as f:
            json.dump(community_mod, f)

        return community_mod

    def get_messages(self):
        """
        Get all messages of the community.

        :return: The messages of the community
        """
        messages = []

        for channel in self._channels:
            for message in self._channels[channel].messages:
                messages.append(self._channels[channel].messages[message])

        return messages

    def deserialize(self, request: dict):
        """
        Deserialize a request into a Community object.

        :param request: The JSON community to be deserialized
        :return: The deserialized community
        """
        authors = {}
        uninitialized_channels = {}
        self._platform = request['platform'].lower()
        self._uuid = request['id']
        self._name = request['name'].lower().replace(' ', '-')

        # Deserialize Members
        for member in request['members']:
            member_instance = Member().deserialize(member, self)
            self._members[member_instance.uuid] = member_instance

        # Deserialize Channels
        for channel in request['channels']:
            channel_instance = Channel().deserialize(channel, self._members, self)
            self._channels[channel_instance.uuid] = channel_instance

        # Deserialize Messages
        for i, channel in enumerate(self._channels):
            for message in request['channels'][i]['messages']:
                message_instance = Message()
                message_instance.channel = self._channels[channel]
                message_instance.deserialize(message,
                                             self._members,
                                             self._channels,
                                             uninitialized_channels,
                                             authors,
                                             self._platform)

                self._channels[channel].messages[message_instance.uuid] = message_instance

        # Merge authors and uninitialized channels into the community authors and channels respectively
        self._authors |= authors
        self._channels |= uninitialized_channels

        self._save()

        return self

    def from_json(self, filename):
        """Initialize this community with the content of the json file.

        :filename: name of the input json file."""
        with open(filename, 'r') as file:
            community = json.load(file)
            self.deserialize(community)
