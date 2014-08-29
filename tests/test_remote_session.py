###
### Тест, испоьзующий локальный легковесный ftp сервер pyFTPd
### и демонстрирующий отправку и получение файла на/с сервера
### с последующей проверкой корректности переданных данных по контрольной сумме..
###

from multiprocessing.context import Process
from os import unlink
from unittest import TestCase
from client import Client

from tests.ftplibd_remote_session import server
from tests.ftplibd_remote_session.tst_file import TestFile
from tests.ftplibd_remote_session import settings


class TestRemoteSession(TestCase):
    def setUp(self):
        self.test_file = TestFile(settings.test_file_size)

        self.original_data = self.test_file.get_content()

        tuned_server, self.port = server.get_tuned_server(self.test_file.path)

        def server_func():
            tuned_server.serve_forever()

        server_process = Process(target=server_func)
        server_process.start()

    def tearDown(self):
        unlink(self.test_file.full_filename)

    def test_receive_file(self):
        print('HEHE')
        a = 21
        client = Client()
        client.connect('localhost', self.port)
        client.login(settings.ftp_user, settings.ftp_pass)
        code, rest, data = client.retr(self.test_file.filename)

        self.assertEqual(code, 226)
        self.assertEqual(self.original_data, data)

