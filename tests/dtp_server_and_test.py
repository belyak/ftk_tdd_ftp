from unittest import TestCase
import socket
import time

from tests.bound_server_and_test import BoundServer
from tests.common import receive_all, send_all


class DTPServer(BoundServer):
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
        super().__init__(host)

        self._data = data

        self._received_data = b''

        self._send_mode = send_mode

    def _communicate(self, client_socket):
        """
        логика работы с сокетом входящего клиентского подключения

        :type client_socket: socket.socket
        """

        print('DEBUG: client_socket: ', client_socket.fileno())

        if self._send_mode:
            send_all(client_socket, self._data)
        else:
            self._received_data = receive_all(client_socket, len(self._data))

        self.ipc_queue.put(self._received_data if len(self._received_data) else self._data)

    def get_received_data(self):
        return self.ipc_queue.get()

    def join(self, timeout=None):
        self.ipc_queue.cancel_join_thread()
        super().join(timeout)


class DTPServerTestCase(TestCase):

    def setUp(self):
        self.__original_data = b'Warning: Some of this package"s functionality requires a functioning shared semaphore'
        # implementation on the host operating system. Without one, the multiprocessing.synchronize module will be
        # disabled, and attempts to import it will result in an ImportError. See issue 3770 for additional information.'

    def test_data_upload(self):

        dtp_server = DTPServer(data=self.__original_data, send_mode=False)
        dtp_server.start()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((dtp_server.get_host(), dtp_server.get_port()))
        send_all(client_socket, self.__original_data)
        client_socket.close()

        data_on_server = dtp_server.get_received_data()
        dtp_server.join()

        self.assertEqual(self.__original_data, data_on_server)

    def test_data_download(self):

        dtp_server = DTPServer(data=self.__original_data, send_mode=True)
        dtp_server.start()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                client_socket.connect((dtp_server.get_host(), dtp_server.get_port()))
                break
            except ConnectionRefusedError:
                time.sleep(1)
                continue
        received_data = client_socket.recv(len(self.__original_data))

        dtp_server.join()

        client_socket.close()

        self.assertEqual(self.__original_data, received_data)