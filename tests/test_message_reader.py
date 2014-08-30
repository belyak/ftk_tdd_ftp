from unittest import TestCase

from ftp_client.message_reader import MessageReader

SIMPLE_MSG_1 = b"150 Opening ASCII mode data connection for '/bin/ls'.\r\n"
SIMPLE_MSG_2 = b"226 Transfer complete.\r\n"
TWO_SIMPLE_MESSAGES = SIMPLE_MSG_1 + SIMPLE_MSG_2

MULTI_LINE_MESSAGE_1 = b'123-First line\r\nSecond line\r\n  234 A line beginning with numbers\r\n123 The last line\r\n'
THREE_MESSAGES = SIMPLE_MSG_1 + MULTI_LINE_MESSAGE_1 + SIMPLE_MSG_2


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
    Создает поддельный объект и, читая из него данные различными порциями, сравнивает полученные данные и данные,
    переданные поддельному объекту при инициализации.
    """
    def test_recv(self):
        original_data = TWO_SIMPLE_MESSAGES

        for portion_size in range(1, len(original_data)):

            fake_socket = FakeReceiveSocket(original_data)

            received_data = received_portion = fake_socket.recv(portion_size)

            while len(received_portion):
                received_portion = fake_socket.recv(portion_size)
                received_data += received_portion

            self.assertEqual(original_data, received_data)


class TestMessageReader(TestCase):
    def test_simple_read(self):
        fake_socket = FakeReceiveSocket(TWO_SIMPLE_MESSAGES)

        # noinspection PyTypeChecker
        message_reader = MessageReader(socket_object=fake_socket)

        message_1 = message_reader.read()
        self.assertEqual(message_1, SIMPLE_MSG_1)

        message_2 = message_reader.read()
        self.assertEqual(message_2, SIMPLE_MSG_2)

    def test_multi_line_read(self):
        fake_socket = FakeReceiveSocket(THREE_MESSAGES)

        # noinspection PyTypeChecker
        message_reader = MessageReader(socket_object=fake_socket)

        message_1 = message_reader.read()
        self.assertEqual(message_1, SIMPLE_MSG_1)

        message_2 = message_reader.read()
        self.assertEqual(message_2, MULTI_LINE_MESSAGE_1)

        message_3 = message_reader.read()
        self.assertEqual(message_3, SIMPLE_MSG_2)
