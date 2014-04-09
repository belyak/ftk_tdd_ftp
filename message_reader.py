class MessageReader():
    def __init__(self, socket_object):
        """
        :type socket_object: socket.socket
        """
        self.__s = socket_object

    def read(self):
        """
        Читает одно сообщение из сокета.
        """
        pass