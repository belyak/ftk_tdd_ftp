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

class ClientTestCase(TestCase):
    
    @patch('client.TextSocket', new=EchoSocket)
    def test_command(self):
        client = Client()
        code, rest = client._command('200 Two hundreds OK')
        self.assertEqual(code, 200)
        self.assertEqual(rest, 'Two hundreds OK')
        
        self.assertRaises(InvalidReplyFormat, client._command, '')
        