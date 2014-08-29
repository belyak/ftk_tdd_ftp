from multiprocessing.context import Process
import socket

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from tests.ftplibd_remote_session.settings import ftp_user, ftp_pass, test_file_size, debug

from tests.ftplibd_remote_session.tst_file import TestFile

test_file = TestFile(size=test_file_size, debug=debug)
test_file.print_info()


def get_bound_socket(host='localhost', minimal_port=1024, debug=False):
    """

    :param str host: host
    :param int minimal_port: minimal port value to bind socket to
    :return: socket and port
    :rtype: (socket.socket, int)
    """
    server_socket = socket.socket()

    port = minimal_port
    bound = False

    while not bound:
        try:
            server_socket.bind((host, port))
            bound = True
        except PermissionError as e:
            if debug:
                print('Port %d is not permitted' % port)
            port += 1
        except OSError as e:
            if e.strerror == 'Address already in use':
                if debug:
                    print("Port %d is already in use" % port)
                port += 1
            else:
                raise e
    if debug:
        print('Bound at port ', port)

    return server_socket, port


def get_tuned_server(path_to_serve):
    """
    :param str path_to_serve: home directory
    :rtype: FTPServer, port,
    """
    authorizer = DummyAuthorizer()
    authorizer.add_user(ftp_user, ftp_pass, path_to_serve, perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer

    server_socket, server_port = get_bound_socket()

    server = FTPServer(server_socket, handler)
    return server, server_port
