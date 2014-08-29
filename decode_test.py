from unittest import TestCase
from decode_reply import decode
from line_separator import LINES_SEPARATOR_STR, LINES_SEPARATOR


class DecodeTest(TestCase):
    def test_get_code_and_text_one_line(self):
        reply = b'220 beastie.tdk.net FTP server (Version 6.00LS) ready.' + LINES_SEPARATOR
        expected_code = 220
        expected_line = 'beastie.tdk.net FTP server (Version 6.00LS) ready.'

        code, line = decode(reply)

        self.assertEqual(expected_code, code)
        self.assertEqual(expected_line, line)

    def test_get_code_and_text_multi_lines(self):

        reply = LINES_SEPARATOR_STR.join(
            [
                '123-First line',
                'Second line',
                '234 A line beginning with numbers',
                '123 The last line' + LINES_SEPARATOR_STR
            ]
        ).encode()

        expected_code = 123
        expected_text = LINES_SEPARATOR_STR.join(
            [
                'First line',
                'Second line',
                '234 A line beginning with numbers',
                'The last line'
            ]
        )

        code, text = decode(reply)

        self.assertEqual(expected_code, code)
        self.assertEqual(expected_text, text)