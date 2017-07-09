import select
import socket

ACTION_READ = 'read'
ACTION_WRITE = 'write'


class Epoll:
    EVENTS = {
        ACTION_READ: select.POLLIN,
        ACTION_WRITE: select.POLLOUT,
    }

    ACTIONS = {
        value: key for key, value
        in EVENTS.items()
    }

    def __init__(self):
        self.poll = select.epoll()
        self.state = {}
        self.socks = {}

    def watch(self, sock, action):
        fileno = sock.fileno()
        evmask = self.EVENTS[action]
        evmask |= self.state.get(fileno, 0)

        if not self.state.get(fileno, 0):
            # Current state is zero: register.
            self.poll.register(fileno, evmask)
            self.state[fileno] = evmask
            self.socks[fileno] = sock
        else:
            # Current state is not zero: modify.
            self.poll.modify(fileno, evmask)
            self.state[fileno] = evmask
            self.socks[fileno] = sock

    def unwatch(self, sock, action):
        fileno = sock.fileno()
        evmask = self.EVENTS[action]
        evmask &= ~self.state[fileno]

        if evmask:
            # New state is not zero: modify.
            self.poll.modify(fileno, evmask)
            self.state[fileno] = evmask
            self.socks[fileno] = sock
        else:
            # New state is zero: unregister.
            self.poll.unregister(fileno)
            del self.state[fileno]
            del self.socks[fileno]

    def events(self):
        while True:
            for fileno, event in self.poll.poll(1):
                try:
                    sock = self.socks[fileno]
                    action = self.ACTIONS[event]
                except KeyError:
                    continue
                else:
                    yield sock, action
