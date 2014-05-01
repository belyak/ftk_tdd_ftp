from multiprocessing import Process, Value
import random
import socket
import time
from unittest import TestCase


from tests.common import decode_pasv_reply


class NotBoundError(Exception):
    pass


class BoundServer():
    """
    сервер, умеющий биндиться на указанный диапазон портов.
    """

    def __init__(self, host=None, port_from=32000, port_to=39000):
        self._socket = socket.socket()

        if host is not None:
            self._host = host
        else:
            self._host = socket.gethostbyname(socket.gethostname())

        self._bind_ports = (port_from, port_to)

        self._port = self._bind_socket(port_from, port_to)

        print('Server %s' % self.__class__.__name__, ' bound at %s:%s' % (self._host, self._port))

        self._process = None
        self._timeout = None

    def _accept_communicate_and_close(self, *args, **kwargs):
        """
        логика выполняемая после старта сервера в отдельной нити
        """
        self._socket.listen(1)
        self._socket.settimeout(self._timeout)
        try:
            client_socket, _ = self._socket.accept()
            print(self.__class__.__name__, 'accepted connection', client_socket, _, '( at %s:%s)' % (self._socket.getsockname()))
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

    def start(self, timeout=None):
        """
        запускает принятие соединений в новом процессе
        :param timeout; количество секунд, которые сервер ожидает входящего соединения.
        """
        self._timeout = timeout
        p = Process(target=self._accept_communicate_and_close, kwargs=self.__dict__)
        self._process = p
        self._process.start()
        time.sleep(2)

    def join(self):
        self._process.join()
        self._socket.close()

    def get_port(self):
        """
        :rtype: int or None
        """
        return self._port

    def get_host(self):
        """
        :rtype:
        """
        return self._host


class TestBoundServer(TestCase):
    def test_passive_reply_and_communicate(self):

        request_len = 10

        class SumServer(BoundServer):
            def _communicate(self, client_socket):
                data = client_socket.recv(request_len).decode()
                operands = map(int, data.split('+'))
                summary = str(sum(operands))
                client_socket.sendall(summary.encode())

        sum_server = SumServer()
        passive_reply = sum_server.passive_reply(binary=True)
        host, port = decode_pasv_reply(passive_reply)

        numbers = [2, 4, 1, 0]
        expected_result = str(sum(numbers)).encode()
        request = '+'.join(map(str, numbers))
        while len(request) != request_len:
            request += ' '

        sum_server.start()

        s = socket.socket()
        s.connect((host, port))
        s.sendall(request.encode())
        result = s.recv(request_len)
        sum_server.join()
        s.close()

        self.assertEqual(expected_result, result)

    def test_accept_timeout(self):
        state_initial, state_changed = 10, 50
        for server_timeout, client_timeout, communication_called, in ((10, 3, state_changed), (2, 5, state_initial)):

            communication_result = Value('i', state_initial)

            class DummyServer(BoundServer):
                def _communicate(self, client_socket):
                    nonlocal communication_result
                    communication_result.value = state_changed

            host = '127.0.0.1'
            dummy_server = DummyServer('127.0.0.1')
            port = dummy_server.get_port()

            def connect_with_timeout():
                s = socket.socket()
                print("server started with timeout ", server_timeout)
                dummy_server.start(server_timeout)
                print("sleeping for ", client_timeout, "sec.")
                time.sleep(client_timeout)
                print("trying to connect...")
                s.connect((host, port))
                dummy_server.join()
                s.close()

            connect_with_timeout()
            self.assertEqual(communication_result.value, communication_called)