import os

from codi.api.tests.framework import Framework
from codi.api.model.disentanglement.discourse import *


class TestDiscourse(Framework):
    def setUp(self, path: str = None):
        path = os.path.join(os.path.dirname(__file__), f'./fixture_data/{path}')
        data = self._read_data_from_fixtures(path)

        self._members, self._messages = self._get_community_members_and_messages(data)


class TestCueWords(TestDiscourse):
    def setUp(self, path: str = None):
        super().setUp('./community_for_cue_words_feature_extraction.json')

    def test_no_cue_words(self):
        self.assertEqual(self._get_feature(CueWords.extract, self._messages['940033847800766474'],
                                           self._messages['939964765420273684']).val,
                         [0, 0, 0, 0, 0, 0])

    def test_thanks_answer_in_first_message(self):
        self.assertEqual(self._get_feature(CueWords.extract, self._messages['939541995662217246'],
                                           self._messages['938733699669848064']).val,
                         [0, 0, 0, 0, 1, 0])

    def test_answer_in_second_message(self):
        self.assertEqual(self._get_feature(CueWords.extract, self._messages['939541995662211231'],
                                           self._messages['938733699669848234']).val,
                         [0, 1, 0, 0, 0, 0])

    def test_thanks_in_first_message(self):
        self.assertEqual(self._get_feature(CueWords.extract, self._messages['939541995662213984'],
                                           self._messages['9387336996698405948']).val,
                         [0, 0, 1, 0, 0, 0])

    def test_mixed_cue_words(self):
        self.assertEqual(self._get_feature(CueWords.extract, self._messages['9395419956622102938'],
                                           self._messages['9387336903928844231']).val,
                         [0, 1, 1, 0, 1, 0])

    def test_all_cue_words(self):
        self.assertEqual(self._get_feature(CueWords.extract, self._messages['939541995662215167'],
                                           self._messages['938733699669844231']).val,
                         [1, 1, 1, 1, 1, 1])


class TestQuestion(TestDiscourse):
    def setUp(self, path: str = None):
        super().setUp('./community_for_question_feature_extraction.json')

    def test_question_in_first_message(self):
        self.assertEqual(self._get_feature(Question.extract, self._messages['940033847800766474'],
                                           self._messages['939964765420273684']).val,
                         [1, 0, 1, 0])

    def test_question_in_second_message(self):
        self.assertEqual(self._get_feature(Question.extract, self._messages['9395419956622150493'],
                                           self._messages['9387336996698401922']).val,
                         [0, 0, 0, 1])

    def test_question_in_both_messages(self):
        self.assertEqual(self._get_feature(Question.extract, self._messages['939541995662217246'],
                                           self._messages['938733699669848064']).val,
                         [1, 0, 0, 1])

    def test_question_in_none_of_the_messages(self):
        self.assertEqual(self._get_feature(Question.extract, self._messages['939541995662211231'],
                                           self._messages['938733699669848234']).val,
                         [0, 0, 0, 0])


class TestLong(TestDiscourse):
    def setUp(self, path: str = None):
        super().setUp('./community_for_long_feature_extraction.json')

    def test_long_in_both_message(self):
        self.assertEqual(self._get_feature(Long.extract, self._messages['940033847800766474'],
                                           self._messages['939964765420273684']).val,
                         [1, 1])

    def test_long_in_first_message(self):
        self.assertEqual(self._get_feature(Long.extract, self._messages['939541995662217246'],
                                           self._messages['938733699669848064']).val,
                         [1, 0])

    def test_long_in_second_message(self):
        self.assertEqual(self._get_feature(Long.extract, self._messages['939541995662211231'],
                                           self._messages['938733699669848234']).val,
                         [0, 1])

    def test_long_in_none_of_the_messages(self):
        self.assertEqual(self._get_feature(Long.extract, self._messages['939541995662239281'],
                                           self._messages['938733638291848234']).val,
                         [0, 0])
