from tempfile import NamedTemporaryFile
from typing import Union

import requests


class Article:
    """Class to represent an article

    Attributes:
        title (str): Article's headline
        orig_link (str): Article's original link
        backup_link (str): Article's backup link
        __file (file): Temporary file containing the HTML of the article
    """
    def __init__(self, title: str, orig_link: str, backup_link: Union[None, str]):
        self.title = title
        self.orig_link = orig_link
        self.backup_link = backup_link

        self.__file = None

    @property
    def filename(self) -> Union[None, str]:
        """Filepath of [__file] or None if [__file] wasn't created"""
        if self.__file:
            return self.__file.name
        else:
            return None

    def download(self):
        """Create a temporary file and write the contents of [orig_link] to it"""
        r = requests.get(self.orig_link)
        if r.ok:
            self.__file = NamedTemporaryFile(mode='w+')
            self.__file.write(r.text)

    def dispose(self):
        """Close the temporary file if it was created thereby deleting it from disk.

        Note:
            This should be called after the file has been backed up to prevent dangling temp files
        """
        if self.__file:
            self.__file.close()

    def __repr__(self):
        return 'Title: {}\nLink: {}'.format(self.title, self.orig_link)
