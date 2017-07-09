from .loop import Loop
from .poll import Epoll
from .task import query


if __name__ == '__main__':
    url = 'http://target.my.com/api/v2/user.json'
    tasks = [query(url) for num in range(10)]

    loop = Loop(Epoll(), tasks)
    print('Ready tasks: ', len(loop.run()))
