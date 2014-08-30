from client import Client

_commands = {}


class MnemonicNotFound(LookupError):
    pass


def get_routine(cmd_mnemonic):
    try:
        return _commands[cmd_mnemonic]
    except KeyError as e:
        return MnemonicNotFound(e)


def command(keyword, synonyms=None):
    def wrapper(fn):
        _commands[keyword] = fn
        if synonyms is not None:
            for synonym in synonyms:
                _commands[synonym] = fn
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

@command('open')
def connect(host, port=21):
    code, rest = client.connect(host, int(port))
    print(code, rest)

@command(keyword='help', synonyms=['?'])
def print_help(*args, **kwargs):
    print("Available commands: ", ', '.join(sorted(_commands.keys())))


@command("close")
def disconnect():
    global client
    del client
    client = Client()