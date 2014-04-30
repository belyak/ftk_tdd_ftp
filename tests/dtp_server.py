import time
from unittest import TestCase
import random
import socket
from threading import Thread


class NotBoundError(Exception):
    pass


class BoundServer():
    """
    сервер, умеющий биндиться на указанный диапазон портов.
    """
    def __init__(self, host='127.0.0.1', port_from=40000, port_to=50000, auto_bind=True):
        self._socket = socket.socket()
        self._host = host
        self._bind_ports = (port_from, port_to)

        if auto_bind:
            self._port = self._bind_socket(port_from, port_to)
        else:
            self._port = None

        self._process = Thread(target=self._accept_communicate_and_close)
        self._timeout = None

    def _accept_communicate_and_close(self):
        """
        логика выполняемая после старта сервера в отдельной нити
        """
        self._socket.listen(1)
        self._socket.settimeout(self._timeout)
        try:
            client_socket, _ = self._socket.accept()
        except socket.timeout as e:
            raise e
        self._communicate(client_socket)
        client_socket.close()

    def _communicate(self, client_socket):
        """
        Логика работы с сокетом
        :type client_socket: socket.socket
        """
        raise NotImplementedError

    def bind_socket(self):
        self._port = self._bind_socket(*self._bind_ports)

    def _bind_socket(self, port_from, port_to):
        """
        Пытается забиндить сокет self._socket в указанном диапазоне на адрес self._host
        """
        is_bound = False
        get_port = lambda: random.randint(port_from, port_to)
        port = get_port()
        while not is_bound:
            try:
                self._socket.bind((self._host, port))
                is_bound = True
            except socket.error as e:
                port = get_port
        return port

    def passive_reply(self, binary=False):
        """
        >>> class D():
        ...     def __init__(self, host, port):
        ...         self._host = host
        ...         self._port = port
        ...     def passive_reply(self, binary=False):
        ...         return BoundServer.passive_reply(self, binary)
        >>> d = D('193.162.146.4', 194*256+54)
        >>> reply = d.passive_reply()
        >>> assert reply[-2:] == chr(13)+chr(10)
        >>> reply[:-2]
        '227 Entering Passive Mode (193,162,146,4,194,54)'
        >>> reply = d.passive_reply(binary=True)
        >>> reply[:-2]
        b'227 Entering Passive Mode (193,162,146,4,194,54)'
        """
        if self._port is None:
            raise NotBoundError()
        else:
            port = self._port
            """:type: int"""

        p1, p2, p3, p4 = map(int, self._host.split('.'))
        p5, p6 = divmod(port, 256)

        reply = '227 Entering Passive Mode (%d,%d,%d,%d,%d,%d)\r\n' % (p1, p2, p3, p4, p5, p6)
        return reply.encode() if binary else reply

    def start(self, timeout=10.0):
        """
        запускает принятие соединений в новом процессе
        :param timeout; количество секунд, которые сервер ожидает входящего соединения.
        """
        self._timeout = timeout
        self._process.start()

    def join(self):
        self._process.join()

    def get_port(self):
        """
        :rtype: int or None
        """
        return self._port


class TestBoundServer(TestCase):
    def test_passive_reply_and_communicate(self):

        request_len = 10

        class SumServer(BoundServer):
            def _communicate(self, client_socket):
                data = client_socket.recv(request_len).decode()
                operands = map(int, data.split('+'))
                summary = str(sum(operands))
                client_socket.sendall(summary.encode())

        sum_server = SumServer(host='127.0.0.1')
        passive_reply = sum_server.passive_reply()
        h1, h2, h3, h4, p1, p2 = map(int, passive_reply[passive_reply.find('(') + 1:passive_reply.find(')')].split(','))

        numbers = [2, 4, 1, 0]
        expected_result = str(sum(numbers)).encode()
        request = '+'.join(map(str, numbers))
        while len(request) != request_len:
            request += ' '

        sum_server.start()
        s = socket.socket()
        s.connect((".".join(map(str, [h1, h2, h3, h4])), p1*256+p2))
        s.sendall(request.encode())
        result = s.recv(request_len)
        sum_server.join()
        s.close()

        self.assertEqual(expected_result, result)

    def test_accept_timeout(self):

        for server_timeout, client_timeout, communication_called, in ((10, 3, True), (2, 5, None    )):

            communication_result = None

            class DummyServer(BoundServer):
                def _communicate(self, client_socket):
                    nonlocal communication_result
                    communication_result = True

            host = '127.0.0.1'
            dummy_server = DummyServer('127.0.0.1')
            port = dummy_server.get_port()

            def connect_with_timeout():
                s = socket.socket()
                print("server started with timout ", server_timeout)
                dummy_server.start(server_timeout)
                print("sleeping for ", client_timeout, "sec.")
                time.sleep(client_timeout)
                print("trying to connect...")
                s.connect((host, port))
                dummy_server.join()
                s.close()

            connect_with_timeout()
            self.assertEqual(communication_result, communication_called)


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

        if self._send_mode:
            client_socket.sendall(self._data)
        else:
            in_byte = b'X'
            while len(in_byte):
                in_byte = client_socket.recv(1)
                self._received_data += in_byte

    def get_received_data(self):
        return self._received_data


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