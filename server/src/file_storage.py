from abc import ABC, abstractmethod

import ipfsapi
from article import Article


class FileStorageProvider(ABC):
    """Abstract class representing a file storage provider

    A file storage provider handles storage and hosting of article backups.
    This can be extended to support any provider such as s3, Dropbox, etc. as long as it satisfies the following requirements:
        1) Must be censorship resistant and not contain any backdoors
        2) Must hold files indefinitely
        3) Ideally should not be censored in target countries (although this is permissible if it can be accessed via VPN)

    Attributes:
        __client (any): Reference to the provider's client object
    """
    def __init__(self, **kwargs):
        self.__client = None  # initialize method should set this
        self._initialize()

    @abstractmethod
    def _initialize(self):
        """Handle initialization of the provider's client object and any other necessary initialization"""
        pass

    @abstractmethod
    def backup_article(self, article: Article):
        """Back up [article] and update it with the [backup_link]

        Args:
            article (Article): The article to backup
        """
        pass


class IpfsProvider(FileStorageProvider):
    """Default backup provider

    This uses IPFS to store backups of articles.
    IPFS is a p2p encrypted and distributed storage solution. Check out https://ipfs.io for more info.

    Attributes:
        host (str): The host on which the IPFS server is running
        port (int): The port on which the IPFS server's local API is running
        __client (ipfsapi): ipfsapi instance
    """
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')

        assert isinstance(self.host, str)
        assert isinstance(self.port, int)

        super().__init__()

    def _initialize(self):
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
