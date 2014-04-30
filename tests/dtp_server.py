from unittest import TestCase
import random
import socket
from threading import Thread


class DTPServer():
    """
    Сервер принимающий соединение и, в зависимости от настроек, принимающий или отправляющий блок данных, после чего
    закрывающий соединение.
    """
    def __init__(self, data, send_mode=True, host='127.0.0.1'):
        """
        :type data: bytes
        :param send_mode: истина, если сервер отправляет данные и ложь если принимает.
        :type send_mode: bool
        """
        if send_mode:
            self.__data = data
        else:
            self.__data = data

        self.__received_data = b''

        self.__send_mode = send_mode
        self.__socket = socket.socket()

        self.__host = host

        is_bound = False
        get_port = lambda: random.randint(40000, 50000)
        port = get_port()
        while not is_bound:
            try:
                self.__socket.bind((self.__host, port))
                is_bound = True
            except socket.error as e:
                port = get_port
        self.__port = port

        self.__socket.listen(1)

        self.__process = Thread(target=self.__accept_send_and_close)

    def passive_reply(self):
        """
        >>> class D():
        ...     def __init__(self, host, port):
        ...         self._DTPServer__host = host
        ...         self._DTPServer__port = port
        ...     def passive_reply(self):
        ...         return DTPServer.passive_reply(self)
        >>> d = D('193.162.146.4', 194*256+54)
        >>> reply = d.passive_reply()
        >>> assert reply[-2:] == chr(13)+chr(10)
        >>> reply[:-2]
        '227 Entering Passive Mode (193,162,146,4,194,54)'
        """
        p1, p2, p3, p4 = map(int, self.__host.split('.'))

        p5, p6 = divmod(self.__port, 256)

        reply = '227 Entering Passive Mode (%d,%d,%d,%d,%d,%d)\r\n' % (p1, p2, p3, p4, p5, p6)
        return reply

    def __accept_send_and_close(self):
        client_socket, _ = self.__socket.accept()

        if self.__send_mode:
            client_socket.sendall(self.__data)
        else:
            in_byte = b'X'
            while len(in_byte):
                in_byte = client_socket.recv(1)
                self.__received_data += in_byte
        client_socket.close()

    def get_port(self):
        return self.__port

    def get_received_data(self):
        return self.__received_data

    def start(self):
        """
        запускает принятие соединений в новом процессе
        """
        self.__process.start()

    def join(self):
        self.__process.join()


class DTPServerTestCase(TestCase):

    def setUp(self):
        self.__original_data = b'abcdefghijklmnopqrtuvwxyz!!'*200

    def test_data_upload(self):

        dtp_server = DTPServer(data=self.__original_data, send_mode=False)
        dtp_server.start()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", dtp_server.get_port()))
        client_socket.sendall(self.__original_data)
        client_socket.close()
        dtp_server.join()

        data_on_server = dtp_server.get_received_data()

        self.assertEqual(self.__original_data, data_on_server)

    def test_data_download(self):

        dtp_server = DTPServer(data=self.__original_data, send_mode=True)
        dtp_server.start()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", dtp_server.get_port()))
        received_data = client_socket.recv(len(self.__original_data))

        dtp_server.join()

        client_socket.close()

        self.assertEqual(self.__original_data, received_data)