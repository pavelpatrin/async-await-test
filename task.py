import socket

from urllib.parse import urlsplit

from .sock import Socket


def request(split):
    return bytes(
        'GET %s HTTP/1.1\r\n' % split.path +
        'Host: %s\r\n' % split.hostname +
        'Connection: close\r\n' +
        '\r\n', 'utf-8'
    )


async def query(url):
    split = urlsplit(url)
    sock = Socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((split.hostname, split.port or 80))
    sent = await sock.send(request(split))
    data = await sock.recv(2 ** 20)
    return data
