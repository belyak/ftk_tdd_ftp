###
### Тест, испоьзующий локальный легковесный ftp сервер pyFTPd
### и демонстрирующий отправку и получение файла на/с сервера
### с последующей проверкой корректности переданных данных по контрольной сумме..
###

from multiprocessing.context import Process
from os import unlink
import os
from unittest import TestCase
import uuid
from client import Client

from tests.ftplibd_remote_session import server
from tests.ftplibd_remote_session.tst_file import TestFile
from tests.ftplibd_remote_session import settings


class TestRemoteSession(TestCase):
    def setUp(self):
        self.test_file = TestFile(settings.test_file_size)

        self.original_data = self.test_file.get_content()

        self.ftp_root = self.test_file.path
        self.remote_filename = uuid.uuid4().hex

        tuned_server, self.port = server.get_tuned_server(self.ftp_root)

        def server_func():
            tuned_server.serve_forever()

        server_process = Process(target=server_func)
        server_process.start()

    def get_connected_client_in_binary_mode(self):
        client = Client()
        client.connect('localhost', self.port)
        client.login(settings.ftp_user, settings.ftp_pass)
        client.type('I')  # Binary mode ('I'mage)
        return client

    def tearDown(self):
        unlink(self.test_file.full_filename)

    def test_receive_file(self):
        """
        тест на получение заранее сгенерированных и сохраненных на диске данных клиентом через подключение
        к локальному серверу.
        """
        client = self.get_connected_client_in_binary_mode()
        code, rest, data = client.retr(self.test_file.filename)

        self.assertEqual(code, 226)
        self.assertTrue(self.original_data == data)

    def test_send_file(self):
        """
        Тест на отправку файла клиентом на локальный сервер и сравнение содержимого файла на диске
        с отправленными данными
        """
        client = self.get_connected_client_in_binary_mode()
        client.stor(self.remote_filename, self.original_data)

        with open(os.path.join(self.ftp_root, self.remote_filename), 'rb') as f:
            stored_file_content = f.read()

        self.assertTrue(self.original_data == stored_file_content)

