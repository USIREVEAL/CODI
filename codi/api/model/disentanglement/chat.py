import math
import datetime

from .feature import Feature
from ..input.message import Message


class Chat(Feature):
    """
    This class represents a feature that is chat-specific.
    """
    def __str__(self):
        return "Chat"

    @staticmethod
    def get_group_features():
        """
        Return the chat-related features

        :return: the list of features
        """
        return [Time, Speaker, CrossAuthorMention, MentionSame, MentionOther, HasMention]


class Time(Chat):
    """
    This class represents a 'time' feature.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message, bin_size: int = 50):
        """
        This method extracts the time between message1 and message2 in seconds, which is then binned logarithmically.

        :param message1: The first message
        :param message2: The second message
        :param bin_size: The number of bins
        :return: The one_hot vector of the time distance
        """
        one_hot = [0] * bin_size

        message1_timestamp = message1.timestamp
        message2_timestamp = message2.timestamp

        if isinstance(message1_timestamp, datetime.datetime):
            diff = abs(int(message2_timestamp.timestamp()) - int(message1_timestamp.timestamp()))
        else:
            diff = abs(int(message2_timestamp) - int(message1_timestamp))

        # Bin the time differences
        binning = int(math.log(diff + 1, 1.5))-1
        if binning < bin_size:
            one_hot[binning] = 1
        else:
            one_hot[bin_size - 1] = 1

        time_obj = cls()
        time_obj.val = one_hot
        time_obj.message_1 = message1
        time_obj.message_2 = message2

        return time_obj


class Speaker(Chat):
    """
    This class represents a 'speaker' feature.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if the speaker of message1 is the same as the speaker of message2.

        :param message1: The first message
        :param message2: The second message
        :return: 0 if the speaker of message1 is not the same as the speaker of message2,
                 1 otherwise
        """
        speaker_obj = cls()
        speaker_obj.val = int(message1.author.uuid == message2.author.uuid)
        speaker_obj.message_1 = message1
        speaker_obj.message_2 = message2

        return speaker_obj


class HasMention(Chat):
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if message1 has mentions or message2 has mentions.

        :param message1: The first message
        :param message2: The second message
        :return: one hot encoding of the above conditions
        """
        one_hot = [0, 0]
        message1_member_mentions = set(message1.get_member_mentions())
        message2_member_mentions = set(message2.get_member_mentions())

        if len(message1_member_mentions) > 0:
            one_hot[0] = 1
        if len(message2_member_mentions) > 0:
            one_hot[1] = 1

        mention_obj = cls()
        mention_obj.val = one_hot
        mention_obj.message_1, mention_obj.message_2 = message1, message2

        return mention_obj


class CrossAuthorMention(Chat):
    """
    This class represents a 'mention' of the author of one message in the other and vice-versa.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks cross message author mentioning features.
        message1 mentions message2 author
        message2 mentions message1 author

        :param message1: The first message
        :param message2: The second message
        :return: one hot encoding of the above conditions
        """
        one_hot = [0, 0]

        message1_member_mentions = set(message1.get_member_mentions())
        message2_member_mentions = set(message2.get_member_mentions())

        for mention in message1_member_mentions:
            if mention == message2.author.uuid:
                one_hot[0] = 1
        for mention in message2_member_mentions:
            if mention == message1.author.uuid:
                one_hot[1] = 1

        mention_obj = cls()
        mention_obj.val = one_hot
        mention_obj.message_1, mention_obj.message_2 = message1, message2

        return mention_obj


class MentionSame(Chat):
    """
    This class represents a 'same mention' feature
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if both in message1 and mention2 the same name is mentioned

        :param message1: The first message
        :param message2: The second message
        :return: 0 if the messages do not mention the same name,
                 1 otherwise
        """
        message1_member_mentions = set(message1.get_member_mentions())
        message2_member_mentions = set(message2.get_member_mentions())

        mention_obj = cls()
        mention_obj.val = 1 if len(message1_member_mentions.intersection(message2_member_mentions)) > 0 else 0
        mention_obj.message_1, mention_obj.message_2 = message1, message2

        return mention_obj


class MentionOther(Chat):
    """
    This class represents a 'different mention' feature.
    1 if message1 and message2 mention the same third member (not author1 nor author2).
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if message1 and message2 mention the same third member (not author1 nor author2).

        :param message1: The first message
        :param message2: The second message
        :return: 1 if both messages mention the same member that is not author1 nor author2
        """
        message1_member_mentions = set(message1.get_member_mentions())
        message2_member_mentions = set(message2.get_member_mentions())
        intersection = message1_member_mentions.intersection(message2_member_mentions)\
            .difference({message1.author.uuid, message2.author.uuid})

        mention_obj = cls()
        mention_obj.val = 1 if len(intersection) > 0 else 0
        mention_obj.message_1, mention_obj.message_2 = message1, message2

        return mention_obj
