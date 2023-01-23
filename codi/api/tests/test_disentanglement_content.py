import os

from codi.api.tests.framework import Framework
from codi.api.model.disentanglement.content import *
from codi.api.model.disentanglement.model import Model


class TestContent(Framework):
    def setUp(self, path: str = None):
        path = os.path.join(os.path.dirname(__file__), f'./fixture_data/{path}')
        data = self._read_data_from_fixtures(path)

        self._community = self._get_community_object(data)
        self._members, self._messages = self._get_community_members_and_messages(data)


class TestRepeat(TestContent):
    def setUp(self, path: str = None):
        super().setUp('./community_for_repeat_feature_extraction.json')
        self._unigram_probabilities = Model().get_unigram_probabilities(self._community, 5)
        self._unigram_probabilities_with_frequent = Model().get_unigram_probabilities(self._community, 0)

    def test_one_repeated_word(self):
        self.assertEqual(self._get_feature(Repeat.extract,
                                           self._messages['940033847800766474'],
                                           self._messages['939964765420273684'],
                                           self._unigram_probabilities).val,
                         [0, 1, 0, 0, 0])

    def test_repeat_with_multiple_words(self):
        self.assertEqual(self._get_feature(Repeat.extract,
                                           self._messages['939541995662211231'],
                                           self._messages['938733699669848234'],
                                           self._unigram_probabilities).val,
                         [0, 4, 0, 0, 0])

    def test_no_repeated_words(self):
        self.assertEqual(self._get_feature(Repeat.extract,
                                           self._messages['939541995662217246'],
                                           self._messages['938733699669848064'],
                                           self._unigram_probabilities).val,
                         [0, 0, 0, 0, 0])

    def test_repeated_words_no_exclusion(self):
        self.assertEqual(self._get_feature(Repeat.extract,
                                           self._messages['940033847800766474'],
                                           self._messages['939964765420273684'],
                                           self._unigram_probabilities_with_frequent).val,
                         [0, 4, 0, 0, 0])

    def test_repeated_words_no_exclusion_2(self):
        self.assertEqual(self._get_feature(Repeat.extract,
                                           self._messages['939541995662211231'],
                                           self._messages['938733699669848234'],
                                           self._unigram_probabilities_with_frequent).val,
                         [0, 6, 0, 0, 0])


class TestTech(TestContent):
    def setUp(self, path: str = None):
        super().setUp('./community_for_tech_feature_extraction.json')

    def test_both_messages_have_tech_words(self):
        self.assertEqual(self._get_feature(Tech.extract,
                                           self._messages['940033847800766474'],
                                           self._messages['939964765420273684'],
                                           self._community).val,
                         [1, 1, 0])

    def test_first_message_has_tech_words(self):
        self.assertEqual(self._get_feature(Tech.extract,
                                           self._messages['940033847800766474'],
                                           self._messages['938733699669848234'],
                                           self._community).val,
                         [1, 0, 0])

    def test_second_message_has_tech_words(self):
        self.assertEqual(self._get_feature(Tech.extract,
                                           self._messages['939541995662217246'],
                                           self._messages['938733699669848064'],
                                           self._community).val,
                         [0, 1, 0])

    def test_neither_message_has_tech_words(self):
        self.assertEqual(self._get_feature(Tech.extract,
                                           self._messages['939541995667483231'],
                                           self._messages['938733699104648234'],
                                           self._community).val,
                         [0, 0, 1])
