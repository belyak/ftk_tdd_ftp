
def decode_pasv_reply(raw_reply):
    """
    :type raw_reply: bytes
    """
    reply = raw_reply.decode()
    h1, h2, h3, h4, p1, p2 = reply[reply.find('(') + 1:reply.find(')')].split(',')
    host = '.'.join([h1, h2, h3, h4])
    port = int(p1)*256 + int(p2)
    return host, port


def receive_all(socket_object, *args):
    """
    Получает все данные из сокета, считывая из буфера по 1 килобайту.

    :type socket_object: socket.socket
    """
    portion_size = 1024

    all_data = data = socket_object.recv(portion_size)
    while len(data) == portion_size:
        data = socket_object.recv(portion_size)
        all_data += data
    return all_data


def send_all(socket_object, data):
    """
    :type socket_object: socket.socket
    :type data: bytes
    """

    portion = 100
    offset = 0
    try:
        while offset < len(data):
            chunk = data[offset:offset + portion]
            offset += socket_object.send(chunk)
    except ConnectionResetError as e:
        print("Sent %d from %d....[%s]" % (offset, len(data), e))