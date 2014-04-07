from unittest import TestCase
from unittest.mock import patch

from client import Client, InvalidReplyFormat


class EchoSocket():
    def __init__(self, *args, **kwargs):
        self.__buff = ''

    def sendall(self, text):
        self.__buff = text

    def recv(self, length):
        res = self.__buff
        self.__buff = ''
        return res


class TestClient(TestCase):
    def test_get_code_and_text_one_line(self):
        reply = '200 Command okay.'
        expected_code = 200
        expected_line = 'Command okay.'

        code, line = Client.get_code_and_text(reply)

        self.assertEqual(expected_code, code)
        self.assertEqual(expected_line, line)

    def test_get_code_and_text_multi_lines(self):

        reply = '\n'.join(
            [
                '123-First line',
                'Second line',
                '  234 A line beginning with numbers',
                '123 The last line'
            ]
        )

        expected_code = '123'
        expected_text = '\n'.join(
            [

                'First line',
                'Second line',
                '234 A line beginning with numbers',
                'The last line'
            ]
        )

    @patch('client.TextSocket', new=EchoSocket)
    def test_command(self):
        client = Client()
        code, rest = client._command('200 Two hundreds OK')
        self.assertEqual(code, 200)
        self.assertEqual(rest, 'Two hundreds OK')

        self.assertRaises(InvalidReplyFormat, client._command, '')
