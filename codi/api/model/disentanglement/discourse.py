import re

from .feature import Feature
from ..input.message import Message


class Discourse(Feature):
    """
    This class represents a feature that is discourse-related.
    """
    def __str__(self):
        return "Discourse"

    @staticmethod
    def get_group_features():
        """
        Return the discourse-related features

        :return: the list of features
        """
        return [CueWords, Question, Long, Greet, Thanks]


class CueWords(Discourse):
    """
    This class represents a 'cue words' feature.
    """
    def __init__(self):
        super().__init__()
        self._thanks_answer = self._get_collection_from_file('cue_words_thanks_answer')
        self._thanks = self._get_collection_from_file('cue_words_thanks')
        self._answer = self._get_collection_from_file('cue_words_answer')

        self._sub_features = [self._answer, self._thanks, self._thanks_answer]

    @staticmethod
    def _get_sub_features(sub_feature: [str], message1: str, message2: str):
        one_hot = [0, 0]

        for cue_word in sub_feature:
            if re.search(rf'\b{cue_word}\b', message1.strip().lower()):
                one_hot[0] = 1

            if re.search(rf'\b{cue_word}\b', message2.strip().lower()):
                one_hot[1] = 1

        return one_hot

    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if either message has a cue word in it. This feature has 6 bits.

        :param message1: The first message
        :param message2: The second message
        :return: one hot encoding. The first element is 1 if the first message contains a cue word
                                                        0 otherwise
                                   Same thing goes of the second message -- with the second message.
        """
        one_hot = []
        message1_text, message2_text = message1.processable_text, message2.processable_text

        cue_words_obj = cls()

        for sub_feature in cue_words_obj._sub_features:
            one_hot.extend(cue_words_obj._get_sub_features(sub_feature, message1_text, message2_text))

        cue_words_obj.val = one_hot
        cue_words_obj.message_1, cue_words_obj.message_2 = message1, message2

        return cue_words_obj


class Question(Discourse):
    """
    This class represents a 'question' feature.
    """
    def __init__(self):
        super().__init__()
        self._question_words = self._get_collection_from_file('question_words')

    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if either message is a question. This feature has 2 bits.

        :param message1: The first message
        :param message2: The second message
        :return: one hot encoding. The first element is 1 if the first message contains a question
                                                        0 otherwise
                                   Same thing goes for the second message -- with the second message.
        """
        one_hot = [0, 0, 0, 0]

        question_obj = cls()

        one_hot[0] = 1 if '?' in message1.text else 0
        one_hot[1] = 1 if '?' in message2.text else 0

        for question_word in question_obj._question_words:
            if re.search(rf'^{question_word}\b', message1.processable_text.strip().lower()):
                one_hot[2] = 1

            if re.search(rf'^{question_word}\b', message2.processable_text.strip().lower()):
                one_hot[3] = 1

        question_obj.val = one_hot
        question_obj.message_1, question_obj.message_2 = message1, message2

        return question_obj


class Long(Discourse):
    """
    This class represents a 'long' feature.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message, words_n: int = 10):
        """
        This method checks if either message is longer than 'words_n' words. This feature has 2 bits.

        :param message1: The first message
        :param message2: The second message
        :param words_n: The number of words
        :return: one hot encoding. The first element is 1 if the first message is long
                                                        0 otherwise
                                   Same thing goes of the second message -- with the second message.
        """
        one_hot = [0, 0]

        one_hot[0] = 1 if len(message1.words) > words_n else 0
        one_hot[1] = 1 if len(message2.words) > words_n else 0

        long_obj = cls()
        long_obj.val = one_hot
        long_obj.message_1, long_obj.message_2 = message1, message2

        return long_obj


class Greet(Discourse):
    """
    This class represents a 'greeting' feature.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if either message contains a greeting expression. This feature has 2 bits.

        :param message1: The first message
        :param message2: The second message
        :return: one hot encoding. The first element is 1 if the first message has a greeting
                                                        0 otherwise
                                   Same thing goes of the second message -- with the second message.
        """
        one_hot = [0, 0]
        for greet in ["hey", "hi", "hello"]:
            if greet in message1.words:
                one_hot[0] = 1
            if greet in message2.words:
                one_hot[1] = 1

        long_obj = cls()
        long_obj.val = one_hot
        long_obj.message_1, long_obj.message_2 = message1, message2

        return long_obj


class Thanks(Discourse):
    """
    This class represents a 'thank you' feature.
    """
    @classmethod
    def extract(cls, message1: Message, message2: Message):
        """
        This method checks if either message contains a 'thank you' expression. This feature has 2 bits.

        :param message1: The first message
        :param message2: The second message
        :return: one hot encoding. The first element is 1 if the first message has a thank you
                                                        0 otherwise
                                   Same thing goes of the second message -- with the second message.
        """
        one_hot = [0, 0]
        for thanks in ["thank", "thanks", "thx", "ty", "grateful"]:
            if thanks in message1.words:
                one_hot[0] = 1
            if thanks in message2.words:
                one_hot[1] = 1

        long_obj = cls()
        long_obj.val = one_hot
        long_obj.message_1, long_obj.message_2 = message1, message2

        return long_obj
