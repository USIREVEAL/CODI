from __future__ import annotations

import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..input.message import Message
    from ..input.community import Community


class Feature:
    """
    This class represents a feature of a pair of messages.
    """
    def __init__(self):
        self._val = None
        self._message_1 = None
        self._message_2 = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.__class__.__name__}: {self._val}'

    @property
    def message_1(self):
        """
        :type: Message
        """
        return self._message_1

    @property
    def message_2(self):
        """
        :type: Message
        """
        return self._message_2

    @property
    def val(self):
        """
        :type: Any
        """
        return self._val

    @message_1.setter
    def message_1(self, message_1):
        """
        Set the first message of the pair.

        :param message_1: The first message of the pair
        """
        self._message_1 = message_1

    @message_2.setter
    def message_2(self, message_2):
        """
        Set the second message of the pair.

        :param message_2: The second message of the pair
        """
        self._message_2 = message_2

    @val.setter
    def val(self, val):
        """
        Set the value of the feature.

        :param val: The value of the feature
        """
        self._val = val

    @staticmethod
    def _get_collection_from_file(file_name: str):
        """
        Get a collection of words or phrases from the input file.

        :param file_name: The name of the file
        :return: The collection of words
        """
        file_path = os.path.join(os.path.dirname(__file__), f'../../collections/{file_name}')

        with open(file_path, 'r') as file:
            collection = [line.strip() for line in file.readlines()]

        return collection

    @staticmethod
    def get_default_features():
        """
        Get the default features to be extracted from the message.

        :return: The default features list
        """
        from ..disentanglement.content import Repeat, Tech, ContainsCode, ContainsLink
        from ..disentanglement.discourse import CueWords, Question, Long, Greet, Thanks
        from ..disentanglement.chat import Time, Speaker, CrossAuthorMention, MentionSame, MentionOther, HasMention

        return [Repeat, Tech, ContainsCode, ContainsLink,
                CueWords, Question, Long, Greet, Thanks,
                Time, Speaker, CrossAuthorMention, MentionSame, MentionOther, HasMention]

    @classmethod
    def get_features(cls,
                     message_1: Message,
                     message_2: Message,
                     features_type_list: [Feature],
                     hyper_params,
                     unigram_probabilities: {str: float}):
        """
        Extract the features -- given by feature_type_list -- of a pair of messages.

        :param message_1: The first message of the pair
        :param message_2: The second message of the pair
        :param features_type_list: The list of types of features to extract
        :param hyper_params: The hyperparameters' dictionary
        :param unigram_probabilities: The unigram probabilities of the words in the community
        :return: The feature vector of the pair of messages
        """
        from .chat import Time
        from .content import Repeat
        from .discourse import Long

        features = []

        for feature_type in features_type_list:
            if feature_type == Time:
                features.append(feature_type.extract(message_1, message_2, int(hyper_params['chat bins'])))
            elif feature_type == Long:
                features.append(feature_type.extract(message_1, message_2, int(hyper_params['discourse max words'])))
            elif feature_type == Repeat:
                features.append(feature_type.extract(message_1, message_2, unigram_probabilities))
            else:
                features.append(feature_type.extract(message_1, message_2))

        return features
