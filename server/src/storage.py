from abc import ABC, abstractmethod
from typing import List

import redis
import requests

from article import Article

PREV_NUM_PAGES_CHECKED_KEY = 'PREV_NUM_PAGES_CHECKED'


class StorageProvider(ABC):
    def __init__(self, **kwargs):
        self.__client = None  # initialize method should set this
        self.__prev_num_pages_checked = 0
        self.initialize()

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_prev_num_pages_checked(self) -> int:
        pass

    @abstractmethod
    def set_num_pages_checked(self, num_pages: int):
        pass

    @abstractmethod
    def exists(self, link: str) -> bool:
        pass

    @abstractmethod
    def save_article(self, article: Article):
        pass

    @abstractmethod
    def get_deleted_articles(self):
        pass


class RedisProvider(StorageProvider):
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.db = kwargs.get('db')

        assert isinstance(self.host, str)
        assert isinstance(self.port, int)
        assert isinstance(self.db, int)

        super().__init__()

    def initialize(self):
        self.__client = redis.StrictRedis(host=self.host, port=self.port, db=self.db)

    def get_prev_num_pages_checked(self):
        return int(self.__client.get(PREV_NUM_PAGES_CHECKED_KEY) or 0)

    def set_num_pages_checked(self, num_pages: int):
        self.__client.set(PREV_NUM_PAGES_CHECKED_KEY, num_pages)

    def exists(self, link: str):
        return self.__client.exists(link)

    def save_article(self, article: Article):
        self.__client.set(article.orig_link, (article.title, article.backup_link))

    def get_deleted_articles(self) -> List[Article]:
        # TODO: these should be done in parallel asynchronously
        deleted_articles = []
        for url in self.__client.scan_iter('*'):
            try:
                r = requests.head(url)
                # TODO: this should actually just check for 404 status code.
                #  Currently this will mistakenly consider lack of internet, etc. as a deleted article.
                if not r.ok:
                    v = eval(self.__client.get(url))
                    deleted_articles.append(
                        Article(title=v[0], orig_link=url, backup_link=v[1])
                    )
                    self.__client.delete(url)
            except:
                pass

        return deleted_articles

    def __repr__(self):
        return 'Redis provider instance at {}:{}'.format(self.host, self.port)
