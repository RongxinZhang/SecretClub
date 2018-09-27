"""Configuration file defining which providers to use and their configuration details"""

import os

from data_storage import RedisProvider
from distributor import TelegramProvider
from file_storage import IpfsProvider
from scraper import SixthToneScraper

FILE_STORAGE_PROVIDER = IpfsProvider
FILE_STORAGE_CONFIG = {
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

DATA_STORAGE_PROVIDER = RedisProvider
DATA_STORAGE_CONFIG = {
    'host': 'redis',
    'port': 6379,
    'db': 0
}
