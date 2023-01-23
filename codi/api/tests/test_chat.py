import os

from codi.api.tests.framework import Framework
from codi.api.model.disentanglement.chat import *


class TestChat(Framework):
    def setUp(self, path: str = None):
        path = os.path.join(os.path.dirname(__file__), f'./fixture_data/{path}')
        data = self._read_data_from_fixtures(path)

        self._members, self._messages = self._get_community_members_and_messages(data)


class TestTime(TestChat):
    def setUp(self, path: str = None):
        super().setUp('./community_for_time_feature_extraction.json')

    def test_time_is_in_first_bin(self):
        one_hot = [0] * 50
        one_hot[2] = 1

        self.assertEqual(self._get_feature(Time.extract, self._messages['940033847800766474'],
                                           self._messages['939964765420273684']).val,
                         one_hot)

    def test_time_is_in_second_bin(self):
        one_hot = [0] * 50
        one_hot[7] = 1

        self.assertEqual(self._get_feature(Time.extract, self._messages['939541995662217246'],
                                           self._messages['938733699669848064']).val,
                         one_hot)

    def test_time_is_in_third_bin(self):
        one_hot = [0] * 50
        one_hot[14] = 1

        self.assertEqual(self._get_feature(Time.extract, self._messages['939541995662211231'],
                                           self._messages['938733699669848234']).val,
                         one_hot)

    def test_time_is_not_in_bin(self):
        one_hot = [0] * 50
        one_hot[27] = 1

        self.assertEqual(self._get_feature(Time.extract, self._messages['939541995662938471'],
                                           self._messages['938733699669038295']).val,
                         one_hot)


class TestSpeaker(TestChat):
    def setUp(self, path: str = None):
        super().setUp('./community_for_speaker_feature_extraction.json')

    def test_speaker_is_the_same(self):
        self.assertEqual(self._get_feature(Speaker.extract, self._messages['940033847800766474'],
                                           self._messages['939964765420273684']).val,
                         1)

    def test_speaker_is_not_the_same(self):
        self.assertEqual(self._get_feature(Speaker.extract, self._messages['939541995662217246'],
                                           self._messages['938733699669848064']).val,
                         0)


class TestCrossAuthorMention(TestChat):
    def setUp(self, path: str = None):
        super().setUp('./community_for_mention_feature_extraction.json')

    def test_author_is_mentioned_in_first_message(self):
        self.assertEqual(self._get_feature(CrossAuthorMention.extract, self._messages['940033847800766474'],
                                           self._messages['939964765420273684']).val,
                         [1, 0])

    def test_author_is_mentioned_in_second_message(self):
        self.assertEqual(self._get_feature(CrossAuthorMention.extract, self._messages['939541995662217246'],
                                           self._messages['938733699669848064']).val,
                         [0, 1])

    def test_both_authors_are_mentioned_in_opposite_message(self):
        self.assertEqual(self._get_feature(CrossAuthorMention.extract, self._messages['939541995662211231'],
                                           self._messages['938733699669848234']).val,
                         [1, 1])

    def test_no_mention_in_messages(self):
        self.assertEqual(self._get_feature(CrossAuthorMention.extract, self._messages['939541995662938471'],
                                           self._messages['938733699669038295']).val,
                         [0, 0])


class TestMentionSame(TestChat):
    def setUp(self, path: str = None):
        super().setUp('./community_for_mention_same_feature_extraction.json')

    def test_same_mention_in_both_messages(self):
        self.assertEqual(self._get_feature(MentionSame.extract, self._messages['940033847800766474'],
                                           self._messages['939964765420273684']).val,
                         1)

    def test_no_same_mention_in_fisrt_message(self):
        self.assertEqual(self._get_feature(MentionSame.extract, self._messages['939541995662217246'],
                                           self._messages['938733699669848064']).val,
                         0)

    def test_no_same_mention_in_second_message(self):
        self.assertEqual(self._get_feature(MentionSame.extract, self._messages['939541995662211231'],
                                           self._messages['938733699669848234']).val,
                         0)

    def test_no_mention_in_messages(self):
        self.assertEqual(self._get_feature(MentionSame.extract, self._messages['939541995662938471'],
                                           self._messages['938733699669038295']).val,
                         0)


class TestMentionOther(TestChat):
    def setUp(self, path: str = None):
        super().setUp('./community_for_mention_other_feature_extraction.json')

    def test_other_member_mention_in_first_message(self):
        self.assertEqual(self._get_feature(MentionOther.extract, self._messages['940033847800766474'],
                                           self._messages['939964765420273684']).val,
                         0)

    def test_other_member_mention_in_second_message(self):
        self.assertEqual(self._get_feature(MentionOther.extract, self._messages['939541995662217246'],
                                           self._messages['938733699669848064']).val,
                         0)

    def test_no_other_member_mention_in_both_messages(self):
        self.assertEqual(self._get_feature(MentionOther.extract, self._messages['939541995662211231'],
                                           self._messages['938733699669848234']).val,
                         1)

    def test_no_other_member_mention_is_in_one_of_the_messages(self):
        self.assertEqual(self._get_feature(MentionOther.extract, self._messages['939541995662938471'],
                                           self._messages['938733699669038295']).val,
                         0)
