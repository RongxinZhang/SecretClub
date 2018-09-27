from abc import ABC, abstractmethod

import ipfsapi
from article import Article


class BackupProvider(ABC):
    def __init__(self, **kwargs):
        self.__client = None  # initialize method should set this
        self.initialize()

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def backup_article(self, article: Article):
        pass


class IpfsProvider(BackupProvider):
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')

        assert isinstance(self.host, str)
        assert isinstance(self.port, int)

        super().__init__()

    def initialize(self):
        self.__client = ipfsapi.connect(self.host, self.port)

    def backup_article(self, article: Article):
        res = self.__client.add(article.filename)
        if isinstance(res, list):
            res = res[0]

        ipfs_hash = res['Hash']

        self.__client.pin_add(ipfs_hash)
        article.backup_link = 'ipfs.io/ipfs/{}'.format(ipfs_hash)

    def __repr__(self):
        return 'IPFS provider instance at {}:{}'.format(self.host, self.port)
