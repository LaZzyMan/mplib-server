import requests
import datetime


def update():
    _ = requests.get('http://127.0.0.1:2019/api/libuser/update_session/')
    print(str(datetime.datetime.now()) + ': Update Session.')
    return


if __name__ == '__main__':
    update()
