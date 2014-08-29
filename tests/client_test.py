from unittest import TestCase
from unittest.mock import patch

from base_client import BaseClient
from message_reader import IncorrectIncomingFtpControlConnectionData
from tests.ccp_server_and_test import CCPServer


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

    @patch('base_client.Socket', new=EchoSocket)
    def test_command(self):
        client = BaseClient()
        # noinspection PyProtectedMember
        code, rest = client._command('200 Two hundreds OK')
        self.assertEqual(code, 200)
        self.assertEqual(rest, 'Two hundreds OK')
        # noinspection PyProtectedMember
        self.assertRaises(IncorrectIncomingFtpControlConnectionData, client._command, 'XXX')

    def test_data_command_download_operation(self):
        original_data = b'The red green blue and gray goes here right now!'

        ccp_server = CCPServer(original_data, True, with_banner=True)
        host, port = ccp_server.get_host_and_port()
        ccp_server.start()

        client = BaseClient()
        client.connect(host, port)
        # noinspection PyProtectedMember
        code, rest, data = client._command_with_transfer('DOWNLOAD')
        print(code, rest)

        ccp_server.get_received_data()
        ccp_server.join()
        self.assertEqual(original_data, data)

    def test_data_command_upload_operation(self):
        original_data = b'And my planet rocks!!!'

        ccp_server = CCPServer(original_data, send_mode=False, with_banner=True)
        host, port = ccp_server.get_host_and_port()
        ccp_server.start()

        client = BaseClient()
        client.connect(host, port)
        # noinspection PyProtectedMember
        code, rest, _ = client._command_with_transfer('UPLOAD', upload=True, data=original_data)
        print(code, rest)

        received_data = ccp_server.get_received_data()
        ccp_server.join()
        self.assertEqual(original_data, received_data)