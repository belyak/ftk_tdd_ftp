###
### Тест, испоьзующий локальный легковесный ftp сервер pyFTPd
### и демонстрирующий отправку и получение файла на/с сервера
### с последующей проверкой корректности переданных данных по контрольной сумме..
###
from multiprocessing.context import Process
from unittest import TestCase
from client import Client

from tests.ftplibd_remote_session import server
from tests.ftplibd_remote_session.tst_file import TestFile
from tests.ftplibd_remote_session import settings




class TestRemoteSession(TestCase):
    def setUp(self):
        self.original_test_file = TestFile()
        tuned_server, self.port = server.get_tuned_server(self.original_test_file.path)

        def server_func():
            tuned_server.serve_forever()

        server_process = Process(target=server_func)
        server_process.start()

    def test_receive_file(self):
        print('HEHE')
        a = 21
        client = Client()
        client.connect('localhost', self.port)
        client.login(settings.ftp_user, settings.ftp_pass)
        client.pwd()
