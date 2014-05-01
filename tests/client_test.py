from unittest import TestCase
from unittest.mock import patch

from client import Client, InvalidReplyFormat
from line_separator import LINES_SEPARATOR, LINES_SEPARATOR_STR

from tests.dtp_server_and_test import DTPServer


class EchoSocket():
    def __init__(self, *args, **kwargs):
        self.__buff = b''

    def sendall(self, text):
        self.__buff = text

    def recv(self, length):
        res = self.__buff
        self.__buff = b''
        return res


class TestClient(TestCase):
    def setUp(self):
        self.__original_binary_data = b'ABC123UIO*()()*)(KJHJHhjhdsj'*100

    def test_get_code_and_text_one_line(self):
        reply = b'220 beastie.tdk.net FTP server (Version 6.00LS) ready.' + LINES_SEPARATOR
        expected_code = 220
        expected_line = 'beastie.tdk.net FTP server (Version 6.00LS) ready.'

        code, line = Client.get_code_and_text(reply)

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

        code, text = Client.get_code_and_text(reply)

        self.assertEqual(expected_code, code)
        self.assertEqual(expected_text, text)

    @patch('client.Socket', new=EchoSocket)
    def test_command(self):
        client = Client()
        # noinspection PyProtectedMember
        code, rest = client._command('200 Two hundreds OK')
        self.assertEqual(code, 200)
        self.assertEqual(rest, 'Two hundreds OK')
        # noinspection PyProtectedMember
        self.assertRaises(InvalidReplyFormat, client._command, '')

    def test_data_command_download_variation(self):

        #dpt_server = DTPServer()

        client = Client()
        # noinspection PyProtectedMember
        # client._command_with_transfer()
