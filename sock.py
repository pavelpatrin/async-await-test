import socket

from .poll import ACTION_READ, ACTION_WRITE


class Socket(socket.socket):
    await_action = None
    await_method = None
    await_params = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setblocking(0)

    def __await__(self):
        action = vars(self).pop('await_action')
        method = vars(self).pop('await_method')
        params = vars(self).pop('await_params')

        yield self, action
        return method(*params)

    def connect(self, *args, **kwargs):
        try:
            super().connect(*args, **kwargs)
        except BlockingIOError:
            pass  # This is ok.

    def send(self, data):
        self.await_action = ACTION_WRITE
        self.await_method = super().send
        self.await_params = [data]
        return self

    def recv(self, size):
        self.await_action = ACTION_READ
        self.await_method = super().recv
        self.await_params = [size]
        return self
