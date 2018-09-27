from abc import ABC, abstractmethod
from typing import List

import redis

from article import Article

PREV_NUM_PAGES_CHECKED_KEY = 'PREV_NUM_PAGES_CHECKED'


class DataStorageProvider(ABC):
    """Abstract class representing a data storage provider

    A data storage provider handles tracking all the found articles.
    This can be extended to support any data store such as a MySQL, MongoDB, Firestore, etc.

    Attributes:
        __client (any): Reference to the provider's client object
    """

    def __init__(self, **kwargs):
        self.__client = None  # initialize method should set this
        self.initialize()

    @abstractmethod
    def initialize(self):
        """Handle initialization of the provider's client object and any other necessary initialization"""
        pass

    @abstractmethod
    def get_prev_num_pages_checked(self) -> int:
        """Load number of pages checked on previous run from provider

        Returns:
            number of pages checked on previous run
        """
        pass

    @abstractmethod
    def set_num_pages_checked(self, num_pages: int):
        """Store number of pages checked this run in provider

        Args:
            num_pages (int): number of pages checked this run
        """
        pass

    @abstractmethod
    def exists(self, link: str) -> bool:
        """Check if link exists in store

        This would be used to check if an article was backed up previously

        Args:
            link (str): link to check for

        Returns:
            True if link was found in store else False
        """
        pass

    @abstractmethod
    def save_article(self, article: Article):
        """Save an article in store

        The headline, original link, and backup link all need to be stored. The structure is data store dependent.
            An RDS might store this in an Article table with columns for each property
            A NoSQL data store might store this as a JSON object
            etc.

        Args:
            article (Article): Article to store
        """
        pass

    @abstractmethod
    def delete_article(self, article: Article):
        """Remove an article from store

        Args:
            article (Article): Article to remove
        """
        pass

    @abstractmethod
    def get_all_articles(self) -> List[Article]:
        """Retrieve all articles from store and parse them to Article objects

        Returns:
            List of articles from store
        """
        pass


class RedisProvider(DataStorageProvider):
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

    def delete_article(self, article: Article):
        self.__client.delete(article.orig_link)

    def get_all_articles(self):
        articles = []
        for url in self.__client.scan_iter('http*'):
            v = eval(self.__client.get(url))
            articles.append(
                Article(title=v[0], orig_link=url, backup_link=v[1])
            )

        return articles

    def __repr__(self):
        return 'Redis provider instance at {}:{}'.format(self.host, self.port)
