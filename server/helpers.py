import ipfsapi
import json
import redis
import requests

BOT_API_BASE_URL = 'https://api.telegram.org/bot573214633:AAFSDF7L-c_qNNXQdlOwtkifDvCrgAHzAbs'
CHAT_ID = '-1001396093290'
CUSTOM_HEADERS = {
    'Content-Type': 'application/json'
}

IPFS_API = ipfsapi.connect('127.0.0.1', 5001)

REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)

def send_telegram_message(msg):
    data = json.dumps({
        'chat_id': CHAT_ID,
        'text': msg
    })
    r = requests.post('{}/sendMessage'.format(BOT_API_BASE_URL), data=data, headers=CUSTOM_HEADERS)
    if r.ok:
        print('Posted message')
    else:
        print('Could not post message')


def upload_to_ipfs(link, title):
    res = IPFS_API.add('/home/ubuntu/tmd/html/{}.html'.format(title))
    hash = res['Hash']
    IPFS_API.pin_add(hash)

    store_to_redis(link, (title, hash))

def check_if_link_downloaded(link):
    return REDIS.exists(link)

def store_to_redis(key, value):
    REDIS.set(key, value)

def get_deleted_articles():
    deleted_articles = []
    for url in REDIS.scan_iter('*'):
        r = requests.head(url)
        # if not r.ok or i < 2:
        if not r.ok:
            v = eval(REDIS.get(url))
            deleted_articles.append({
                'headline': v[0],
                'ipfs_link': v[1]
            })
            REDIS.delete(url)

    return deleted_articles
