import os

from backup import IpfsProvider
from distributor import TelegramProvider
from scraper import SixthToneScraper
from storage import RedisProvider


BACKUP_PROVIDER = IpfsProvider
BACKUP_CONFIG = {
    'host': 'ipfs',
    'port': 5001
}

DISTRIBUTION_PROVIDER = TelegramProvider
DISTRIBUTION_CONFIG = {
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'chat_id': os.getenv('TELEGRAM_SECRET_CLUB_CHAT_ID')
}

SCRAPER = SixthToneScraper
SCRAPER_CONFIG = {}

STORAGE_PROVIDER = RedisProvider
STORAGE_CONFIG = {
    'host': 'redis',
    'port': 6379,
    'db': 0
}
