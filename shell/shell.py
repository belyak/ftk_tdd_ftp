from base_client import SPIException
from shell.commands import get_routine, MnemonicNotFound


def shell_loop():
    cmd = ''
    while 'quit' not in cmd:
        cmd = input("> ")
        try:
            if ' ' in cmd:
                cmd_mnemonic, *cmd_args = cmd.split(' ')
            else:
                cmd_mnemonic = cmd
                cmd_args = []

            cmd_routine = get_routine(cmd_mnemonic)

            if len(cmd_args):
                cmd_routine(*cmd_args)
            else:
                cmd_routine()

        except MnemonicNotFound:
            print('Unknown command: `%s`' % cmd)
        except TypeError as e:
            print("Incorrect arguments count!")
        except SPIException as e:
            print(e.code, e.rest)