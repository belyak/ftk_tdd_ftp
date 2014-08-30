from ftp_client.invalid_reply import InvalidReplyFormat
from ftp_client.line_separator import LINES_SEPARATOR_STR


def decode(reply):
    """
    Разделяет ответ сервера на числовой код и текст (который может состоять как из одной строки, так и из нескольких
    :type reply: bytes
    """

    try:
        text_reply = reply.decode()
        lines = text_reply.split(LINES_SEPARATOR_STR)
        del lines[-1]
    except UnicodeDecodeError:
        raise InvalidReplyFormat(reply)

    if len(lines) == 1:
        # однострочный ответ
        try:
            code = int(reply[:3])
            rest = reply[4:].decode().strip(LINES_SEPARATOR_STR)
        except ValueError:
            msg = 'Invalid reply format: `%s`' % reply
            raise InvalidReplyFormat(msg)
        return code, rest
    elif len(lines) > 1:
        # многострочный ответ
        try:
            code_one = int(lines[0][:3])
            code_two = int(lines[-1][:3])
            if code_one != code_two:
                raise InvalidReplyFormat('Code %d != code %d' % (code_one, code_two))
        except ValueError:
            raise InvalidReplyFormat(reply)

        lines[0] = lines[0][4:]
        lines[-1] = lines[-1][4:]

        rest = LINES_SEPARATOR_STR.join(lines)
        return code_one, rest
    else:
        raise InvalidReplyFormat('Incorrect reply `%s`' % text_reply)
