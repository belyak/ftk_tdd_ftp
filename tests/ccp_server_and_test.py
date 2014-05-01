from unittest import TestCase
import socket
from message_reader import MessageReader
from tests.bound_server_and_test import BoundServer
from tests.common import decode_pasv_reply
from tests.dtp_server_and_test import DTPServer
from tests.common import receive_all


class CCPServer(DTPServer):
    """
    Сервер ожидающий полученя команды PASV и отправляющий (либо принимающий) данные по каналу данных
    """
    def __init__(self, data, send_mode=True, host='127.0.0.1'):
        """
        :type data: bytes
        :param send_mode: истина, если сервер отправляет данные и ложь если принимает.
        :type send_mode: bool
        """
        super().__init__(data, send_mode, host)

    def _communicate(self, client_socket):
        """
        :type client_socket: socket.socket
        """
        message_reader = MessageReader(client_socket)
        # noinspection PyProtectedMember
        message = message_reader._read_line()
        if message.decode() != 'PASV\r\n':
            raise ValueError('Incorrect incoming message (`%s` instead of `PASV<cr><lf>`' % message)

        data_server = DTPServer(data=self._data, send_mode=self._send_mode, host=self._host)
        passive_reply = data_server.passive_reply(binary=True)

        data_server.start()
        client_socket.sendall(passive_reply)

        # noinspection PyProtectedMember
        message = message_reader._read_line()
        if not self._send_mode:
            expected_message = 'UPLOAD\r\n'.encode()
        else:
            expected_message = 'DOWNLOAD\r\n'.encode()
        if message != expected_message:
            raise ValueError('Incorrect incoming message (`%s` instead of `%s<cr><lf>`' % (message,
                                                                                           expected_message[:-2]))
        self._received_data = data_server.get_received_data()
        data_server.join()
        self.ipc_queue.put(self._received_data)
        client_socket.sendall('200 OK.\r\n'.encode())


class CPPServerTestCase(TestCase):

    def setUp(self):
        self.__original_data = b'This means that whenever you use a queue you need to make sure that all items which !'

    def test_data_upload(self):

        ccp_server = CCPServer(data=self.__original_data, send_mode=False)
        ccp_server.start()

        control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_socket.connect(ccp_server.get_host_and_port())
        control_socket.sendall('PASV\r\n'.encode())

        message_reader = MessageReader(control_socket)

        passv_reply = message_reader.read()
        data_host, data_port = decode_pasv_reply(passv_reply)
        control_socket.sendall("UPLOAD\r\n".encode())

        data_socket = socket.socket()
        data_socket.connect((data_host, data_port))
        data_socket.sendall(self.__original_data)

        upload_reply = message_reader.read()

        ccp_server.join()

        data_socket.close()
        control_socket.close()

        self.assertEqual(upload_reply.decode(), '200 OK.\r\n')

        self.assertEqual(self.__original_data, ccp_server.get_received_data())

    def test_data_download(self):
        ccp_server = CCPServer(data=self.__original_data, send_mode=True)
        ccp_server.start()

        control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_socket.connect(ccp_server.get_host_and_port())
        control_socket.sendall('PASV\r\n'.encode())

        message_reader = MessageReader(control_socket)

        passv_reply = message_reader.read()
        data_host, data_port = decode_pasv_reply(passv_reply)
        control_socket.sendall("DOWNLOAD\r\n".encode())

        data_socket = socket.socket()
        data_socket.connect((data_host, data_port))
        received_data = receive_all(data_socket)

        upload_reply = message_reader.read()

        ccp_server.get_received_data()  # освободим очередь, чтобы не получить дедлок процесса
        ccp_server.join()

        data_socket.close()
        control_socket.close()

        self.assertEqual(upload_reply.decode(), '200 OK.\r\n')

        self.assertEqual(self.__original_data, received_data)