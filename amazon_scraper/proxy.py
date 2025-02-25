import requests
from stem import Signal
from stem.control import Controller


def renew_connection():
    with Controller.from_port(port = 9151) as controller:
        controller.authenticate(password="Shafay97271954!")
        controller.signal(Signal.NEWNYM)


def get_tor_session():
    session = requests.session()
    session.proxies = {
        'http': f'socks5://127.0.0.1:9150',
        'https': f'socks5://127.0.0.1:9150' 
    }
    return session


if __name__ == '__main__':
    pass
