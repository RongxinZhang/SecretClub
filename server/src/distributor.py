import json
import logging
from abc import ABC, abstractmethod

import requests

from article import Article

logger = logging.getLogger(__name__)


class DistributionProvider(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def share_article(self, article: Article) -> bool:
        pass


class TelegramProvider(DistributionProvider):
    def __init__(self, **kwargs):
        super().__init__()

        bot_token = kwargs.get('bot_token')
        self.chat_id = kwargs.get('chat_id')

        assert isinstance(bot_token, str)
        assert isinstance(self.chat_id, str)

        self.bot_base_url = 'https://api.telegram.org/bot{}'.format(bot_token)
        self.headers = {'Content-Type': 'application/json'}

    def share_article(self, article):
        message = '{}\n{}'.format(article.title, article.backup_link)
        data = json.dumps({
            'chat_id': self.chat_id,
            'text': message
        })

        r = requests.post('{}/sendMessage'.format(self.bot_base_url), data=data, headers=self.headers)
        if not r.ok:
            logger.error('Could not send message "{}". Response was {}'.format(message, r.text))

        return r.ok

    def __repr__(self):
        return 'Telegram messenger provider instance for chat {}'.format(self.chat_id)
