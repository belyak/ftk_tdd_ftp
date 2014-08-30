class InvalidReplyFormat(ValueError):
    """
    Исключение для неверного формата сообщения (ответа) сервера
    """
    def __init__(self, reply):
        super().__init__(reply)