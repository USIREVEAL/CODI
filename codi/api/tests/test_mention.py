import os

from codi.api.tests.framework import Framework
from codi.api.model.input.mention import MemberMention


class TestMemberMention(Framework):
    def setUp(self):
        # FIXME: Provide explicit references to messages to be tested
        path = os.path.join(os.path.dirname(__file__), 'fixture_data/messages_with_member_mentions.json')
        data = self._read_data_from_fixtures(path)

        self._blocks, self._messages = self._get_blocks_and_messages(data, MemberMention.retrieve, 'content', True)

    def test_retrieve_message_with_one_member_mention(self):
        self.assertEqual(len(self._blocks[2]), 1)
        self.assertEqual(self._messages[2], '__MEMBER_MENTION__ now it should work again')

    def test_retrieve_message_with_multiple_member_mentions(self):
        self.assertEqual(len(self._blocks[0]), 2)
        self.assertEqual(self._messages[1], '@2019284756374894 should not work as a mention')

    def test_retrieve_message_with_no_member_mentions(self):
        self.assertEqual(len(self._blocks[1]), 0)
        self.assertEqual(self._messages[0], 'I\'ve asked __MEMBER_MENTION__ and __MEMBER_MENTION__')

    def test_retrieve_message_with_mention_in_mention(self):
        self.assertEqual(len(self._blocks[3]), 1)
        self.assertEqual(self._messages[3], '<@201928475__MEMBER_MENTION__6374893> now it should work again')

    def test_retrieve_message_with_back_to_back_mentions(self):
        self.assertEqual(len(self._blocks[4]), 2)
        self.assertEqual(self._messages[4], '__MEMBER_MENTION____MEMBER_MENTION__ now it should work again')
