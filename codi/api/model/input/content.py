from __future__ import annotations

import re
import emoji

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message


class Content:
    """
    This class represents the content of a message
    """
    def __init__(self):
        self._start_position = None
        self._end_position = None
        self._message = None

    def __repr__(self):
        return self.__str__()

    def __str__(self, content=None):
        return f"{self.__class__}: {content}"

    @property
    def start_position(self):
        """
        :type: int
        """
        return self._start_position

    @property
    def end_position(self):
        """
        :type: int
        """
        return self._end_position

    @property
    def message(self):
        """
        :type: str
        """
        return self._message

    @start_position.setter
    def start_position(self, start_position):
        """
        Set the start position of the content in the message.

        :param start_position: The start position of the content in the message
        """
        self._start_position = start_position

    @end_position.setter
    def end_position(self, end_position):
        """
        Set the end position of the content in the message.

        :param end_position: The end position of the content in the message
        """
        self._end_position = end_position

    @message.setter
    def message(self, message):
        """
        Set the message.

        :param message: The message
        """
        self._message = message

    def deserialize(self, start_position: int, end_position: int, message: Message = None):
        self._start_position = start_position
        self._end_position = end_position
        self._message = message


class Text(Content):
    """
    This class represents a textual content in a message.
    """
    def __init__(self):
        super().__init__()
        self._text = None

    def __str__(self, content=None):
        return super.__str__(self._text)

    @property
    def text(self):
        """
        :type: str
        """
        return self._text

    @text.setter
    def text(self, text: str):
        """
        Set the text of the content.

        :param text: The text of the content
        """
        self._text = text

    def deserialize(self, start_position: int, end_position: int, message: Message = None, text: str = None):
        """
        Deserialize the text contents of a message.

        :param start_position: The start position of the content in the message
        :param end_position: The end position of the content in the message
        :param message: The message object
        :param text: The text of the content
        :return:
        """
        super().deserialize(start_position, end_position, message)
        self._text = text

        return self

    @classmethod
    def retrieve(cls, message: str, contents: list, message_obj: Message = None):
        """
        Retrieve a list of text blocks from a message.

        :param message: The message to retrieve the text contents from
        :param message_obj: The message object
        :param contents: The list of the retrieved contents
        :return: A list of text blocks
        """
        text = []

        if len(contents) == 0 and message != '':
            text.append(Text().deserialize(0, len(message), message_obj, message))
            return text
        else:
            for i, block in enumerate(contents):
                if i == 0 and 0 < block.start_position:
                    text.append(Text().deserialize(0,
                                                   block.start_position,
                                                   message_obj,
                                                   message[:block.start_position]))

                if 0 < i < len(contents) and block.start_position > contents[i - 1].end_position:
                    previous_block = contents[i - 1]
                    text.append(Text().deserialize(previous_block.end_position,
                                                   block.start_position,
                                                   message_obj,
                                                   message[previous_block.end_position:block.start_position]))

                if i == len(contents) - 1 and block.end_position < len(message):
                    text.append(Text().deserialize(block.end_position,
                                                   len(message),
                                                   message_obj,
                                                   message[block.end_position:]))

        return text


class Link(Content):
    """
    This class represents a link in a message.
    """
    def __init__(self):
        super().__init__()
        self._url = None

    def __str__(self, content=None):
        return super.__str__(self._url)

    @property
    def url(self):
        """
        :type: str
        """
        return self._url

    @url.setter
    def url(self, url: str):
        """
        Set the URL of the link.

        :param url: The URL of the link
        """
        self._url = url

    def deserialize(self, start_position: int, end_position: int, message: Message = None, url: str = None):
        """
        Deserialize a link into a Link object.

        :param start_position: The start position of the link in the message
        :param end_position: The end position of the link in the message
        :param message: The message object
        :param url: The URL of the link
        :return: The deserialized link
        """
        super().deserialize(start_position, end_position, message)
        self._url = url

        return self

    @classmethod
    def retrieve(cls, message: str, message_obj: Message = None):
        """
        Retrieve the list of links from a message text.

        :param message: The message text
        :param message_obj: The message object
        :return: The list of links
        """
        links = []
        link_regex = re.compile(r'<?(https?://)(www\.)?([-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b)(['
                                r'-a-zA-Z0-9()@:%_+.~#?&/=]*)>?')

        for link in link_regex.finditer(message):
            link_text = ''.join([i for i in link.groups() if i])
            links.append(Link().deserialize(link.start(), link.end(), message_obj, link_text))

            pattern = f'<{link_text}>' if (f'<{link_text}>' in message) else f'{link_text}'
            message = message.replace(pattern, f'__LINK__', 1)

        return links, message


class Code(Content):
    """
    This class represents a code block in a message.
    """
    def __init__(self):
        super().__init__()
        self._code = None

    def __str__(self, content=None):
        return super.__str__(self._code)

    @property
    def code(self):
        """
        :type: str
        """
        return self._code

    @code.setter
    def code(self, code: str):
        """
        Set the code of the content.

        :param code: The code of the content
        """
        self._code = code

    def deserialize(self, start_position: int, end_position: int, message: Message = None, code: str = None):
        """
        Deserialize a code block into a Code object.

        :param start_position: The start position of the code block in the message
        :param end_position: The end position of the code block in the message
        :param message: The message object
        :param code: The code of the code block
        :return: The deserialized code block
        """
        super().deserialize(start_position, end_position, message)
        self._code = code

        return self

    @classmethod
    def retrieve(cls, message: str, message_obj: Message = None):
        """
        Retrieve the list of code blocks in a message.

        :param message: The message to retrieve the code blocks from
        :param message_obj: The message object
        :return: The list of code blocks in the message
        """
        code_block_list = []
        code_regex = re.compile(r'(`{3}[\s\S]*?`{3})|(`[\s\S]*?`)')

        for code in code_regex.finditer(message):
            code_text = ''.join([i for i in code.groups() if i])
            code_block_list.append(Code().deserialize(code.start(), code.end(), message_obj, code_text))
            message = message.replace(code_text, f'__CODEBLOCK__', 1)

        return code_block_list, message


class Multimedia(Content):
    """
    This class represents a multimedia element in a message.
    """
    def __init__(self):
        super().__init__()
        self._url = None

    def __str__(self, content=None):
        return super.__str__(self._url)

    @property
    def url(self):
        """
        :type: str
        """
        return self._url

    @url.setter
    def url(self, url: str):
        """
        Set the urls of the multimedia element.

        :param url: The urls of the multimedia element
        """
        self._url = url

    def deserialize(self, start_position: int, end_position: int, message: Message = None, url: str = None):
        """
        Deserialize a multimedia urls into a Multimedia object.

        :param start_position: The start position of the multimedia urls in the message
        :param end_position: The end position of the multimedia urls in the message
        :param message: The message object
        :param url: The urls of the multimedia element
        :return: The Multimedia object
        """
        super().deserialize(start_position, end_position, message)
        self._url = url

        return self

    @classmethod
    def retrieve(cls, message: str, message_obj: Message = None):
        """
        Retrieve the list of multimedia elements in a message.

        :param message: The message to retrieve the multimedia elements from
        :param message_obj: The message object
        :return: The list of multimedia elements in the message
        """
        multimedia_list = []
        video_regex = re.compile(r'<?(https?://)(player.|www.)?(vimeo\.com|youtu('
                                 r'?:be\.com|\.be|be\.googleapis\.com))(/)(video/|embed/|watch\?v=|v/)?(['
                                 r'A-Za-z0-9._%-]+)(&\S+)?>?')

        for video in video_regex.finditer(message):
            video_url = ''.join([i for i in video.groups() if i])
            multimedia_list.append(Multimedia().deserialize(video.start(), video.end(), message_obj, video_url))

            pattern = f'<{video_url}>' if (f'<{video_url}>' in message) else f'{video_url}'
            message = message.replace(pattern, f'__VIDEO__', 1)

        multimedia_regex = re.compile(r'<?(https?://)([-a-zA-Z0-9()@:%_+.~#?&/=]*)(\.)('
                                      r'jpg|jpeg|JPG|JPEG|gif|gifv|png|PNG|webm|mp4|mp3|wav|ogg)>?')

        for multimedia in multimedia_regex.finditer(message):
            multimedia_url = ''.join([i for i in multimedia.groups() if i])
            multimedia_list.append(Multimedia().deserialize(multimedia.start(),
                                                            multimedia.end(),
                                                            message_obj,
                                                            multimedia_url))

            pattern = f'<{multimedia_url}>' if (f'<{multimedia_url}>' in message) else f'{multimedia_url}'
            message = message.replace(pattern, f'__MULTIMEDIA__', 1)

        return multimedia_list, message


class Emoji(Content):
    """
    This class represents an emoji in a message.
    """
    def __init__(self):
        super().__init__()
        self._unicode = None

    def __str__(self, content=None):
        return super.__str__(self._unicode)

    @property
    def unicode(self):
        """
        :type: str
        """
        return self._unicode

    @unicode.setter
    def unicode(self, unicode: str):
        """
        Set the unicode of the emoji.

        :param unicode: The unicode of the emoji
        """
        self._unicode = unicode

    def deserialize(self, start_position: int, end_position: int, message: Message = None, unicode: str = None):
        """
        Deserialize a unicode string into an Emoji object.

        :param start_position: The start position of the unicode in the message
        :param end_position: The end position of the unicode in the message
        :param message: The message object
        :param unicode: The unicode of the emoji
        :return: The Emoji object
        """
        super().deserialize(start_position, end_position, message)
        self._unicode = unicode

        return self

    @classmethod
    def retrieve(cls, message: str, message_obj: Message = None):
        """
        Retrieve the list of unicode strings in a message.

        :param message: The message to retrieve the unicode strings from
        :param message_obj: The message object
        :return: The list of Emoji objects in the message
        """
        emoji_list = []
        emoji_regex = emoji.get_emoji_regexp()

        for emoji_char in emoji_regex.finditer(message):
            emoji_unicode = ''.join([i for i in emoji_char.groups() if i])
            emoji_list.append(Emoji().deserialize(emoji_char.start(), emoji_char.end(), message_obj, emoji_unicode))

            message = message.replace(emoji_unicode, f'__EMOJI__', 1)

        for emoji_char in re.finditer(r':([^\s:]+):', message):
            emoji_unicode = emoji_char.group(0)
            emoji_list.append(Emoji().deserialize(emoji_char.start(), emoji_char.end(), message_obj, emoji_unicode))

            message = message.replace(emoji_char.group(0), f'__EMOJI__', 1)

        return emoji_list, message
