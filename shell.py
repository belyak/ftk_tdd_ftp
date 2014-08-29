from base_client import SPIException
from client import Client

_commands = {}


def command(keyword):
    def wrapper(fn):
        _commands[keyword] = fn
        return fn
    return wrapper

client = Client()

@command("ls")
def lst():
    code, rest, data = client.list()
    print(code, rest)
    print(data.decode())

@command('login')
def login(user, password):
    code, rest = client.login(user, password)
    print(code, rest)

@command("open")
def connect(host, port=21):
    code, rest = client.connect(host, port)
    print(code, rest)

@command("close")
def disconnect():
    global client
    del client
    client = Client


def main():
    cmd = ''
    while 'quit' not in cmd:
        cmd = input("> ")
        try:
            if ' ' in cmd:
                cmd_mnemonic, *args = cmd.split(' ')
            else:
                cmd_mnemonic = cmd
                args = []

            cmd_routine = _commands[cmd_mnemonic]

            if len(args):
                cmd_routine(*args)
            else:
                cmd_routine()

        except KeyError:
            print('Unknown command: `%s`' % cmd)
        except TypeError as e:
            print("Incorrect arguments count!")
        except SPIException as e:
            print(e.code, e.rest)


if __name__ == '__main__':
    main()