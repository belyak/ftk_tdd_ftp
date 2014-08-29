import socket
import re

from decode_reply import decode
from line_separator import LINES_SEPARATOR
from message_reader import MessageReader


CODE_INVALID_REPLY_FORMAT = -1


class Socket(socket.socket):
    pass


class BaseClient():
    def __init__(self, passive_connection_timeout=10):
        """
        :param int passive_connection_timeout: таймаут на соединение канала данных, сек
        """
        self.__s = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sp = None
        """:type: socket.socket"""
        self.__reader = MessageReader(socket_object=self.__s)
        self.__server_host, self.__server_port = None, None
        self.__passive_host = self.__passive_port = self.__passive_mode = False
        self.__sp_timeout = passive_connection_timeout

        self.__pasv_addr_regex = re.compile(r'\(([0-9]+),([0-9]+),([0-9]+),([0-9]+),([0-9]+),([0-9]+)\)')


    def __read_code_and_text(self):
        raw_message = self.__reader.read()
        return decode(raw_message)

    def connect(self, host, port):
        self.__s.connect((host, port))
        code, data = self._command('')
        self.__server_host, self.__server_port = host, port
        print(code, data)

    def _command(self, text):
        """
        Runs command which does not require data connection (only control one is used)
        :param text: command' text without trailing new line symbol
        :returns: tuple of two elements: code and text
        :rtype: (int, str,)
        """
        if len(text):
            self.__s.sendall(text.encode() + LINES_SEPARATOR)
        reply = self.__reader.read()
        return decode(reply)
    
    def _command_with_transfer(self, text, upload=False, data=None):
        """
        Выполняет команду, предусматривающую передачу данных по каналу данных.

        :type text: str
        :param text: текст команды
        :type upload: bool
        :param upload: направление передачи, True - на сервер, False - на клиент.
        """
        self.passive_mode()
        # transfer service command:
        self.__s.sendall(text.encode() + LINES_SEPARATOR)
        self._sp_connect()
        # positive preliminary reply:
        c1, l1 = self.__read_code_and_text()

        if upload:
            received_data = None
            self.__send_data(data)
        else:
            received_data = self.__receive_data()

        self._sp_disconnect()
        # positive completion reply;
        code, rest = self.__read_code_and_text()
        return code, rest, received_data

    def login(self, user, password):
        """
        Авторизация пользователя на сервере
        :type user: str
        :param user: имя пользователя
        :type password: str
        :param password: пароль
        """
        code, rest = self._command('USER %s' % user)
        print(code, rest)
        code, rest = self._command('PASS %s' % password)
        print(code, rest)
        
    def passive_mode(self):
        """
        Выполняет команду PASV и сохраняет полученные в ответе адрес хоста и порт
        """
        code, rest = self._command('PASV')
        print(code, rest)
        address_str = rest.split(' ')[-1]
        print('DEBUG: adr str: `%s`' % address_str)
        (h1, h2, h3, h4, p1, p2), = self.__pasv_addr_regex.findall(address_str)
        self.__passive_host = '.'.join([h1, h2, h3, h4])
        self.__passive_port = int(p1)*256 + int(p2)
        print('telnet %s %s' % (self.__passive_host, self.__passive_port))

    def _sp_disconnect(self):
        if self.__sp is None:
            return
        
        try:
            self.__sp.close()
            print('data link closed')
        except socket.error as e:
            print('got error:', e)
    
    def _sp_connect(self):

        try:
            self.__sp = Socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sp.settimeout(self.__sp_timeout)
            self.__sp.connect((self.__passive_host, self.__passive_port))
            print('connected data link')        
        except socket.error as e:
            print('got error:', e)
            pass

    def __send_data(self, data):
        """
        :param bytes data: Данные для передачи по каналу данных
        """
        self.__sp.send(data)

    @staticmethod
    def receive_all(socket_object):
        """
        Получает все данные из сокета, считывая из буфера по 1 килобайту.

        :type socket_object: socket.socket
        """
        portion_size = 1024
        all_data = data = socket_object.recv(portion_size)
        while len(data) == portion_size:
            all_data += data
            data = socket_object.recv(portion_size)
        return all_data

    def __receive_data(self):
        data = self.receive_all(self.__sp)
        return data

