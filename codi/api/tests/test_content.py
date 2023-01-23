import os

from codi.api.model.input.content import *
from codi.api.tests.framework import Framework
from codi.api.model.input.attachment import Attachment


class TestContent(Framework):
    def setUp(self, path: str = None, function=None, blocks_in: str = 'content'):
        # FIXME: Provide explicit references to messages to be tested
        path = os.path.join(os.path.dirname(__file__), path)
        data = self._read_data_from_fixtures(path)

        self._blocks, self._messages = self._get_blocks_and_messages(data, function, blocks_in)


class TestLink(TestContent):
    def setUp(self, path: str = None, function=None, blocks_in=None):
        super().setUp('fixture_data/messages_with_links.json', Link.retrieve)

    def test_retrieve_message_with_one_link(self):
        self.assertEqual(len(self._blocks[0]), 1)
        self.assertEqual(self._messages[0], 'This is where you can find the icorsi page for the lecture __LINK__')

    def test_retrieve_message_with_multiple_links(self):
        self.assertEqual(len(self._blocks[1]), 2)
        self.assertEqual(self._messages[1], 'Why does it not embed __LINK__ or __LINK__')

    def test_retrieve_message_with_no_links(self):
        self.assertEqual(len(self._blocks[2]), 0)
        self.assertEqual(self._messages[2], 'I think that the link https://icorsi is broken')

    def test_retrieve_message_with_back_to_back_links(self):
        self.assertEqual(len(self._blocks[3]), 2)
        self.assertEqual(self._messages[3], '__LINK____LINK__')


class TestCode(TestContent):
    def setUp(self, path: str = None, function=None, blocks_in=None):
        super().setUp('fixture_data/messages_with_code_blocks.json', Code.retrieve)

    def test_retrieve_message_with_one_code_block(self):
        self.assertEqual(len(self._blocks[0]), 1)
        self.assertEqual(self._messages[0], 'This is a large message with a code block.\n__CODEBLOCK__end')

    def test_retrieve_message_with_multiple_code_blocks(self):
        self.assertEqual(len(self._blocks[1]), 3)
        self.assertEqual(self._messages[1], 'Inline code blocks __CODEBLOCK__, __CODEBLOCK__, and __CODEBLOCK__')

    def test_retrieve_message_with_no_code_blocks(self):
        self.assertEqual(len(self._blocks[2]), 0)
        self.assertEqual(self._messages[2], 'There are no code blocks here! `ciao')

    def test_retrieve_message_with_code_block_in_code_block(self):
        self.assertEqual(len(self._blocks[3]), 1)
        self.assertEqual(self._messages[3], 'Does it recognize inline blocks inside of code blocks? __CODEBLOCK__')


class TestAttachment(TestContent):
    def setUp(self, path: str = None, function=None, blocks_in: str = 'attachments'):
        super().setUp('fixture_data/messages_with_attachments.json', Attachment.retrieve_attachments, blocks_in)

    def test_retrieve_message_with_one_attachment(self):
        self.assertEqual(len(self._blocks[0]), 1)

    def test_retrieve_message_with_multiple_attachments(self):
        self.assertEqual(len(self._blocks[1]), 4)

    def test_retrieve_message_with_no_attachments(self):
        self.assertEqual(len(self._blocks[2]), 0)


class TestMultimedia(TestContent):
    def setUp(self, path: str = None, function=None, blocks_in=None):
        super().setUp('fixture_data/messages_with_multimedia_blocks.json', Multimedia.retrieve)

    def test_retrieve_message_with_one_video(self):
        self.assertEqual(len(self._blocks[0]), 1)
        self.assertEqual(self._messages[0], 'This is where you can find the video for the lecture __VIDEO__')

    def test_retrieve_message_with_one_multimedia_block(self):
        self.assertEqual(len(self._blocks[1]), 1)
        self.assertEqual(self._messages[1], 'This is where you can find it __MULTIMEDIA__')

    def test_retrieve_message_with_multiple_multimedia_blocks(self):
        self.assertEqual(len(self._blocks[2]), 2)
        self.assertEqual(self._messages[2], 'Found it also on vimeo __VIDEO__, __MULTIMEDIA__')

    def test_retrieve_message_with_no_multimedia_blocks(self):
        self.assertEqual(len(self._blocks[3]), 0)
        self.assertEqual(self._messages[3], 'I think that the link https://vimeo.com/ is broken')

    def test_retrieve_message_with_back_to_back_multimedia_blocks(self):
        self.assertEqual(len(self._blocks[4]), 2)
        self.assertEqual(self._messages[4], '__VIDEO____MULTIMEDIA__')


class TestEmoji(TestContent):
    def setUp(self, path: str = None, function=None, blocks_in=None):
        super().setUp('fixture_data/messages_with_emojis.json', Emoji.retrieve)

    def test_retrieve_message_with_one_emoji(self):
        self.assertEqual(len(self._blocks[0]), 1)
        self.assertEqual(self._messages[0], 'Hi __EMOJI__')

    def test_retrieve_message_with_multiple_emojis(self):
        self.assertEqual(len(self._blocks[1]), 2)
        self.assertEqual(self._messages[1], 'Hi __EMOJI__ __EMOJI__')

    def test_retrieve_message_with_no_emojis(self):
        self.assertEqual(len(self._blocks[2]), 0)
        self.assertEqual(self._messages[2], 'Hi')

    def test_retrieve_message_with_back_to_back_emojis(self):
        self.assertEqual(len(self._blocks[3]), 2)
        self.assertEqual(self._messages[3], 'Hi__EMOJI____EMOJI__')

    def test_retrieve_message_with_emoji_between_colons(self):
        self.assertEqual(len(self._blocks[4]), 1)
        self.assertEqual(self._messages[4], 'Hi __EMOJI__')

    def test_retrieve_message_with_back_to_back_emojis_between_colons(self):
        self.assertEqual(len(self._blocks[5]), 2)
        self.assertEqual(self._messages[5], 'Hi __EMOJI____EMOJI__')

    def test_retrieve_message_with_colon_before_emoji_between_colons(self):
        self.assertEqual(len(self._blocks[6]), 1)
        self.assertEqual(self._messages[6], 'This: is an emoji __EMOJI__')
