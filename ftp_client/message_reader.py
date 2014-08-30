from ftp_client.line_separator import LINES_SEPARATOR


class IncorrectIncomingFtpControlConnectionData(ValueError):
    def __init__(self, reply):
        super().__init__(reply)


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
        first_line = self.__read_line()

        if first_line[3:4] == b' ':
            # однострочный ответ
            return first_line
        elif first_line[3:4] == b'-':
            code = int(first_line[:3])
            result = first_line
            last_line_met = False
            while not last_line_met:
                line = self.__read_line()
                result += line

                if line[3:4] == b' ':
                    try:
                        ending_code = int(line[:3])
                        if ending_code == code:
                            last_line_met = True
                    except ValueError:
                        pass
            return result
        else:
            raise IncorrectIncomingFtpControlConnectionData('Incorrect incoming ftp data!\n%s\n\n' % first_line)

    def read_line(self, debug=False):
        if not debug:
            return self.__read_line()
        else:
            result = self.__read_line()
            print("MSG RL>>> %s" % result)
            return result

    def __read_line(self):
        line = self.__s.recv(1)
        while line[-2:] != LINES_SEPARATOR:
            line += self.__s.recv(1)
        return line
