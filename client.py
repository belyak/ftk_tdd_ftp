import socket

HOST = 'ftp.freebsd.org'
PORT = 21

CODE_INVALID_REPLY_FORMAT = -1

class TextSocket(socket.socket):
    def sendall(self, text):
        return super().sendall(text.encode('utf-8'))
    
    def recv(self, length):
        data = super().recv(length)
        return data.decode('utf-8')
    
class DataSocket(socket.socket):
    pass

class InvalidReplyFormat(ValueError):
    def __init__(self, reply):
        super().__init__(reply)

class Client():
    def __init__(self):
        self.__s = TextSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sp = None
        self.__server_host, self.__server_port = None, None
        self.__passive_host = self.__passive_post = self.__passive_mode = False

    def connect(self, host, port):
        self.__s.connect((HOST, PORT))
        code, data = self._command('')
        self.__server_host, self.__server_port = host, port
        print(code, data)

    @staticmethod
    def _get_code_and_rest(line):
        """
        >>> c = Client()
        >>> Client._get_code_and_rest('200 Status is OK')
        (200, 'Status is OK')
        """
        try:
            code = int(line[:3])
            rest = line[4:].strip('\n\r')
        except ValueError:
            msg = 'Invalid reply format: `%s`' % line
            raise InvalidReplyFormat(msg)
        return code, rest  
        

    def _command(self, text):
        """
        Runs command which does not require data connection (only control one is used)
        :param text: command's text without trailing new line symbol
        :returns: tuple of two elements: code and text
        :rtype: (int, str,)
        """
        if len(text):
            self.__s.sendall('%s\n' % text)
        reply = self.__s.recv(1024*1024)
        return self._get_code_and_rest(reply)
    
    def _command_with_transfer(self, text, upload=False):
        self.passive_mode()
        self.__s.sendall('%s\n' % text)       
        data = self.__recv_data()
        print(data)
        line = self.__s.recv(1024)
        code, rest = self._get_code_amd_rest(line)
        print(code,  rest)        
        return data    
    

    def login(self, user, password):
        code, rest = self._command('USER %s' % user)
        print(code, rest)
        code, rest = self._command('PASS %s' % password)
        print(code, rest)
        
    def passive_mode(self):
        code, rest = self._command('PASV')
        print(code, rest)
        addr_str = rest.split(' ')[-1]
        print('DEBUG: adr str: `%s`' % addr_str)
        h1, h2, h3, h4, p1, p2 = addr_str.strip('()').split(',')
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
            prinit('got error:', e)
    
    def _sp_connect(self):
        try:
            self.__sp = DataSocket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sp.connect((self.__passive_host, self.__passive_port))
            print('connected data link')        
        except socket.error as e:
            print('got error:', e)
            pass

    def __send_data():
        pass
    
    def __recv_data(self):
        self._sp_connect()
        data = self.__sp.recv(1024*1024)
        self._sp_disconnect()
        return data
        
    def lst(self):
        self.passive_mode()
        self.__s.sendall('LIST\n')       
        data = self.__recv_data()
        print(data)
        line = self.__s.recv(1024)
        code, rest = self._get_code_and_rest(line)
        print(code,  rest)        
        return data

if __name__ == '__main__':        
    #ftp = ftplib.FTP(host=HOST, user='ftp', passwd='aa@mm.com', acct='')
    #result = ftp.dir()
    #print(result)


    c = Client()
    c.connect(HOST, PORT)
    c.login('ftp', 'aa@mm.com')
    c.pwd()
    c.passive_mode()
    c.lst()
    c.lst()
    c.lst()
