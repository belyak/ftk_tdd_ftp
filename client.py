from base_client import BaseClient


def command(cmd, with_transfer=False, has_argument=False):
    def inner(fn):
        def simple_wrapper(self, *args, **kwargs):
            if has_argument:
                if len(args):
                    arg = args[0]
                elif kwargs:
                    arg = kwargs.values()[0]
                else:
                    raise AttributeError('You should call %s with argument!' % fn)
                full_cmd = '%s %s' % (cmd, arg)
            else:
                full_cmd = cmd

            if not with_transfer:
                code, rest = self._command(full_cmd)
                data = None
            else:
                code, rest, data = self._command_with_transfer(full_cmd)

            return code, rest, data
        return simple_wrapper
    return inner



class Client(BaseClient):
    """
    Реализации конкретных команд
    """

    @command('LIST', with_transfer=True)
    def list(self):
        pass

    def nlst(self):
        code, rest, data, = self._command_with_transfer('NLST')
        print(code, rest)
        print(data)

    def cwd(self, remote_dir):
        code, rest = self._command('CWD %s' % remote_dir)
        print(code, rest)

    def pwd(self):
        code, rest = self._command('PWD')
        print(code, rest)

    def quit(self):
        code, rest = self._command('QUIT')
        return code, rest

    def retr(self, filename):
        code, rest, data = self._command_with_transfer('RETR %s' % filename)
        print(code, rest)
        print(data)
        return code, rest, data

    def stor(self, filename, data):
        code, rest, _ = self._command_with_transfer('STOR %s' % filename, upload=True, data=data)
        return code, rest

if __name__ == '__main__':

    HOST = 'ftp.freebsd.org'
    PORT = 21

    c = Client()
    c.connect(HOST, PORT)
    c.login('ftp', 'aa@mm.com')
    c.pwd()
    l = c.list()
    print(l)
    print('*'*100)
    c.nlst()
    c.retr('index.html')
