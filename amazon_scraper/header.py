import random
import time
from proxy import get_tor_session, renew_connection

def get_ua():
    """Get a random user agent from user_agent.txt"""
    with open('user-agents.txt', 'r') as ua_file:
        user_agents = ua_file.readlines()
    return random.choice(user_agents).strip()


def generate_headers():
    """Generate a random header"""
    accept_encodings = "gzip, deflate, br, zstd"
    accept_languages = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "en;q=0.7"]
    accepted = [
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'text/html,application/xhtml+xml,image/jxr, */*',
        'text/html,application/xml;q=0.9,application/xhtml+xml,image/png,image/webp,image/jpeg,image/gif,image/x-xbitmap,*/*;q=0.1'
    ]

    user_agent = get_ua()

    headers = {
        "User-Agent": user_agent,
        "Accept-Encoding": accept_encodings,
        "Accept-Language": random.choice(accept_languages),
        "Accept": random.choice(accepted),
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1"
    }
    
    return headers

def generate_req(URL: str):
    """Generates requests from URL until accepted"""
    headers = generate_headers()
    renew_connection()
    session = get_tor_session()
    session.headers = headers
    html = session.get(URL)

    while html.status_code != 200:
        time.sleep(random.randint(1, 4))
        headers = generate_headers()
        renew_connection()
        session = get_tor_session()
        session.headers = headers
        html = session.get(URL)
    return html

if __name__ == '__main__':
    pass
