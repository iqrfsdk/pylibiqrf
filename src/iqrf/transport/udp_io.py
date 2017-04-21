import socket

BUFFER_SIZE = 1024 * 1024

__all__ = [
    "RawUdpIo",
    "open"
]


class RawUdpIo:

    def __init__(self, host, port):
        self.remote_address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", port))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def send(self, message):
        self.socket.sendto(message, self.remote_address)

    def receive(self, timeout=None):
        self.socket.settimeout(timeout)

        data, _ = self.socket.recvfrom(BUFFER_SIZE)

        return data

    def close(self):
        self.socket.close()


def open(host, port):
    return RawUdpIo(host, port)
