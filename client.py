import socket

HOST = 'ftp.freebsd.org'
PORT = 21

CODE_INVALID_REPLY_FORMAT = -1


class Socket(socket.socket):
    pass


class InvalidReplyFormat(ValueError):
    def __init__(self, reply):
        super().__init__(reply)


class Client():
    def __init__(self):
        self.__s = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sp = None
        """:type: socket.socket"""
        self.__server_host, self.__server_port = None, None
        self.__passive_host = self.__passive_port = self.__passive_mode = False

    def connect(self, host, port):
        self.__s.connect((HOST, PORT))
        code, data = self._command('')
        self.__server_host, self.__server_port = host, port
        print(code, data)

    @staticmethod
    def get_code_and_text(reply):
        """
        Разделяет ответ сервера на числовой код и текст (который может состоять как из одной строки, так и из нескольких
        :type reply: bytes
        """

        try:
            text_reply = reply.decode()
            lines = text_reply.split('\n\r')
            del lines[-1]
        except UnicodeDecodeError:
            raise InvalidReplyFormat(reply)

        if len(lines) == 1:
            # однострочный ответ
            try:
                code = int(reply[:3])
                rest = reply[4:].decode().strip('\n\r')
            except ValueError:
                msg = 'Invalid reply format: `%s`' % reply
                raise InvalidReplyFormat(msg)
            return code, rest
        elif len(lines) > 1:
            # многострочный ответ
            try:
                code_one = int(lines[0][:3])
                code_two = int(lines[-1][:3])
                if code_one != code_two:
                    raise InvalidReplyFormat('Code %d != code %d' % (code_one, code_two))
            except ValueError:
                raise InvalidReplyFormat(reply)

            lines[0] = lines[0][4:]
            lines[-1] = lines[-1][4:]

            rest = '\n\r'.join(lines)
            return code_one, rest
        else:
            raise InvalidReplyFormat('Incorrect reply `%s`' % text_reply)

    def _command(self, text):
        """
        Runs command which does not require data connection (only control one is used)
        :param text: command' text without trailing new line symbol
        :returns: tuple of two elements: code and text
        :rtype: (int, str,)
        """
        if len(text):
            self.__s.sendall(text.encode() + b'\n\r')
        reply = self.__receive_all(self.__s)
        return self.get_code_and_text(reply)
    
    def _command_with_transfer(self, text, upload=False):
        """
        Выполняет команду, предусматривающую передачу данных по каналу данных
        :type text: str
        :param text: текст команды
        :type upload: bool
        :param upload: направление передачи, True - на сервер, False - на клиент.
        """
        self.passive_mode()
        self.__s.sendall('%s\n' % text)       
        data = self.__receive_data()
        line = self.__s.recv(1024)
        code, rest = self.get_code_and_text(line)
        return code, rest, data

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
        code, rest = self._command('PASV')
        print(code, rest)
        address_str = rest.split(' ')[-1]
        print('DEBUG: adr str: `%s`' % address_str)
        h1, h2, h3, h4, p1, p2 = address_str.strip('()').split(',')
        self.__passive_host = '.'.join([h1, h2, h3, h4])
        self.__passive_port = int(p1)*256 + int(p2)
        print('telnet %s %s' % (self.__passive_host, self.__passive_port))
        
    def cwd(self, remote_dir):
        code, rest = self._command('CWD %s' % remote_dir)
        print(code, rest)
        
    def pwd(self):
        code, rest = self._command('PWD')
        print(code, rest)
    
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
            self.__sp.connect((self.__passive_host, self.__passive_port))
            print('connected data link')        
        except socket.error as e:
            print('got error:', e)
            pass

    def __send_data(self):
        pass

    @staticmethod
    def __receive_all(socket_object):
        """
        Получает все данные из сокета, считывая из буфера по 1 килобайту.

        :type socket_object: socket.socket
        """
        all_data = b''
        data = socket_object.recv(1024)
        while len(data):
            all_data += data
            data = socket_object.recv(1024)
        return all_data

    def __receive_data(self):
        self._sp_connect()
        data = self.__receive_all(self.__sp)
        self._sp_disconnect()
        return data
        
    def lst(self):
        code, rest, data = self._command_with_transfer('LIST')
        if code == 200:
            print(data)
        else:
            print(code, rest)
            print(data)

if __name__ == '__main__':        

    c = Client()
    c.connect(HOST, PORT)
    c.login('ftp', 'aa@mm.com')
    c.pwd()
    c.passive_mode()
    c.lst()
    c.lst()
    c.lst()
