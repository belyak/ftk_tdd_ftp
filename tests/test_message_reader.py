from unittest import TestCase


class FakeReceiveSocket():
    """
    Класс, подменяющий сокет, из которого будет производиться чтение.
    Реализует только вызов recv, данные для буфера получает при инициализации.
    """
    def __init__(self, data):
        """
        :param data: данные, которые предполагается читать из сокета
        :type data: bytes
        """
        self.__data = data
        self.__pointer = 0

    def recv(self, size):
        result = self.__data[self.__pointer:self.__pointer + size]
        self.__pointer += size
        return result


class FakeReceiveSocketTest(TestCase):
    """
    Элементарный тест для поддельного объекта.
    Создает поддельный объект и, читая из него данные различными порциями, сравнивает полученные данные и ланные,
    переданные поддельному объекту при инициализации.
    """
    def test_recv(self):
        original_data = b"150 Opening ASCII mode data connection for '/bin/ls'.\r\n226 Transfer complete.\r\n"

        for portion_size in range(1, len(original_data)):

            fake_socket = FakeReceiveSocket(original_data)

            received_data = received_portion = fake_socket.recv(portion_size)

            while len(received_portion):
                received_portion = fake_socket.recv(portion_size)
                received_data += received_portion

            self.assertEqual(original_data, received_data)

#
# class TestMessageReader(TestCase):
#     def test_read(self):
#         self.fail()