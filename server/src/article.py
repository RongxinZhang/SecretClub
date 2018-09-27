from tempfile import NamedTemporaryFile
from typing import Union

import requests


class Article:
    def __init__(self, title: str, orig_link: str, backup_link: Union[None, str]):
        self.title = title
        self.orig_link = orig_link
        self.backup_link = backup_link

        self.__file = None

    @property
    def filename(self) -> Union[None, str]:
        if self.__file:
            return self.__file.name
        else:
            return None

    def download(self):
        r = requests.get(self.orig_link)
        if r.ok:
            self.__file = NamedTemporaryFile(mode='w+')
            self.__file.write(r.text)

    def dispose(self):
        if self.__file:
            self.__file.close()

    def __repr__(self):
        return 'Title: {}\nLink: {}'.format(self.title, self.orig_link)
