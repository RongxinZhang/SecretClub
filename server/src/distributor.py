import json
import logging
from abc import ABC, abstractmethod

import requests

from article import Article

logger = logging.getLogger(__name__)


class DistributionProvider(ABC):
    """Abstract class representing a distribution provider

    A distribution provider handles sharing backup links with interested parties
    This can be extended to support any messaging platform such as Signal, WhatsApp, etc. as long as it satisfies the following requirements:
        1) Must be censorship resistant and not contain any backdoors
        2) Must allow for anonymous groups

    Note:
        Because of requirement 1, we can't use WeChat for example since the Chinese government has access to all users, chats, etc.
        This is extremely important as we don't want our users to be in any danger.
    """
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def share_article(self, article: Article) -> bool:
        """Share [article]'s backup with the group

        Note:
            Implementations should format the messages in the way that makes sense to that platform.

        Args:
            article (Article): The article to share

        Returns:
            True if message sent successfully, otherwise False
        """
        pass


class TelegramProvider(DistributionProvider):
    def __init__(self, **kwargs):
        """Default distribution provider

        This uses Telegram to share backups of articles with a secret group.
        Telegram is a heavily encrypted messaging platform. Although it is blocked in China, it can be accessed via VPN
            and prides itself as being a censorship resistant messenger. Check out https://telegram.org for more info.

        Attributes:
            bot_base_url (str): The base url for the telegram bot
            chat_id (str): The ID of the telegram chat we are sharing messages to
            headers (dict): HTTP headers to send along with requests
        """
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
