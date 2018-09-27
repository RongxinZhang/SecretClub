from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup as bs

from article import Article


class Scraper(ABC):
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.articles = []

    @abstractmethod
    def get_num_pages(self) -> int:
        pass

    @abstractmethod
    def load_articles(self, num_pages: int):
        pass


class SixthToneScraper(Scraper):
    def __init__(self, **kwargs):
        super().__init__('http://www.sixthtone.com')

    def get_num_pages(self):
        r = requests.get('{}/search/page/0/news'.format(self.base_url))
        if r.ok:
            soup = bs(r.json()['pager'], 'html.parser')
            return int(soup.find('input', {'id': 'pagination_total'}).get('value'))
        else:
            return 0

    def load_articles(self, num_pages: int):
        for i in range(num_pages):
            url = '{}/search/page/1/news?page={}&sort=1'.format(self.base_url, i)
            r = requests.get(url)
            if not r.ok:
                continue

            soup = bs(r.json()['news'], 'html.parser')

            for group in soup.findAll('div', {'class': 'group'}):
                a = group.find('a')
                if a:
                    self.articles.append(
                        Article(title=a.text, orig_link='{}{}'.format(self.base_url, a.get('href')), backup_link=None)
                    )

    def __repr__(self):
        return 'Scraper instance for {}'.format(self.base_url)
