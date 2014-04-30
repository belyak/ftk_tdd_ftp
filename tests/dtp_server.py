from unittest import TestCase
import random
import socket
from threading import Thread


class DTPServer():
    """
    Сервер принимающий соединение и, в зависимости от настроек, принимающий или отправляющий блок данных, после чего
    закрывающий соединение.
    """
    def __init__(self, data, send_mode=True):
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

        is_bound = False
        get_port = lambda: random.randint(40000, 50000)
        port = get_port()
        while not is_bound:
            try:
                self.__socket.bind(("localhost", port))
                is_bound = True
            except socket.error as e:
                port = get_port
        self.__port = port

        self.__socket.listen(1)

        self.__process = Thread(target=self.__accept_send_and_close)

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

        data_on_server = dtp_server.get_received_data()
        dtp_server.join()

        self.assertEqual(self.__original_data, data_on_server)

    def test_data_download(self):

        dtp_server = DTPServer(data=self.__original_data, send_mode=True)
        dtp_server.start()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", dtp_server.get_port()))
        received_data = client_socket.recv(len(self.__original_data))
        client_socket.close()

        dtp_server.join()

        self.assertEqual(self.__original_data, received_data)