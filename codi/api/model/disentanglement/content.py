from __future__ import annotations

import re
import math

from decimal import Decimal
from typing import TYPE_CHECKING

from .feature import Feature

if TYPE_CHECKING:
    from ..input.message import Message


class Content(Feature):
    """
    This class represents a feature that is content-related.
    """
    def __str__(self):
        return "Content"

    @staticmethod
    def get_group_features():
        """
        Return the content-related features

        :return: the list of features
        """
        return [Repeat, Tech, ContainsCode, ContainsLink]


class Repeat(Content):
    """
    This class represents the 'repeat' feature.
    """
    @staticmethod
    def _get_common_words(message1: Message, message2: Message, unigram_probabilities: {str: float}):
        """
        Find which words are in common between the two messages.

        :param message1: The first message
        :param message2: The second message
        :return: The list of words in common between the two messages
        """
        message1_text = re.sub(r'_{2}([A-Z]*_?)*_{2}|_|\?', ' ', message1.processable_text).lower()
        message2_text = re.sub(r'_{2}([A-Z]*_?)*_{2}|_|\?', ' ', message2.processable_text).lower()

        message1_words = set([word for word in message1_text.split() if word not in ['', ' ']])
        message2_words = set([word for word in message2_text.split() if word not in ['', ' ']])

        return list(message1_words & message2_words & unigram_probabilities.keys())

    @classmethod
    def extract(cls, message1: Message, message2: Message, unigram_probabilities: {str: float}):
        """
        Given a set of all the community messages, compute the unigram probabilities. After which, find how many
        words are in common between the two messages, and bin them logarithmically. This feature has 10 bits.

        :param message1: The first message
        :param message2: The second message
        :param unigram_probabilities: The unigram probabilities
        :return: The one-hot vector of the repeated words
        """
        bin_size = 5
        one_hot = [0] * bin_size
        common_words = cls()._get_common_words(message1, message2, unigram_probabilities)

        # Bin the common words
        for word in common_words:
            word_dec = Decimal(unigram_probabilities[word])

            if word_dec > 0:
                binning = -int(math.log(word_dec, 10))
                one_hot[binning] += 1
            else:
                one_hot[0] += 1

        repeat_obj = cls()
        repeat_obj.val = one_hot
        repeat_obj.message_1 = message1
        repeat_obj.message_2 = message2

        return repeat_obj


class Tech(Content):
    """
    This class represents the 'tech' feature.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        Given two messages, check if both messages contain technical jargon, only one does, or neither do. This feature
        has 3 bits.

        :param message1: The first message
        :param message2: The second message
        :return: The one-hot vector of the tech feature
        """
        # message1 has tech, message2 has tech, neither has tech
        one_hot = [0, 0, 0]
        ip_regex = re.compile(r'\b((?:[0-9]{1,3}\.){3}[0-9]{1,3})\b')
        tech_words = set(cls._get_collection_from_file('tech_words'))
        words_message_1 = set(message1.words)
        words_message_2 = set(message2.words)

        if words_message_1 & tech_words or ip_regex.search(message1.text):
            one_hot[0] = 1

        if words_message_2 & tech_words or ip_regex.search(message2.text):
            one_hot[1] = 1

        if one_hot[0] == one_hot[1] == 0:
            one_hot[2] = 1

        tech_obj = cls()
        tech_obj.val = one_hot
        tech_obj.message_1 = message1
        tech_obj.message_2 = message2

        return tech_obj


class ContainsCode(Content):
    """
    This class represents a 'contains_code' feature.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if either message contains a code block. This feature has 2 bits.

        :param message1: The first message
        :param message2: The second message
        :return: one hot encoding. The first element is 1 if the first message has a code block
                                                        0 otherwise
                                   Same thing goes of the second message -- with the second message.
        """
        one_hot = [0, 0]
        one_hot[0] = 1 if message1.has_code_blocks() else 0
        one_hot[1] = 1 if message2.has_code_blocks() else 0

        long_obj = cls()
        long_obj.val = one_hot
        long_obj.message_1, long_obj.message_2 = message1, message2

        return long_obj


class ContainsLink(Content):
    """
    This class represents a 'contains_link' feature.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if either message contains a link (URL). This feature has 2 bits.

        :param message1: The first message
        :param message2: The second message
        :return: one hot encoding. The first element is 1 if the first message has a link
                                                        0 otherwise
                                   Same thing goes of the second message -- with the second message.
        """
        one_hot = [0, 0]
        one_hot[0] = 1 if message1.has_links() else 0
        one_hot[1] = 1 if message2.has_links() else 0

        long_obj = cls()
        long_obj.val = one_hot
        long_obj.message_1, long_obj.message_2 = message1, message2

        return long_obj
