import codecs

from django.conf import settings
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser


class PlainParser(BaseParser):
    media_type = "text/plain"

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as Plain Text and returns the resulting data.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            decoded_stream = codecs.getreader(encoding)(stream)
            text_content = decoded_stream.read()
            return text_content
        except ValueError as exc:
            raise ParseError('Plain text parse error - %s' % str(exc))
