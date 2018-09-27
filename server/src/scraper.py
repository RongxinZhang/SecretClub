from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup as bs

from article import Article


class Scraper(ABC):
    """Abstract class representing a site scraper

    A site scraper handles scraping a news site and parsing out articles.
    This can be extended to support any news site or blog.

    Attributes:
        base_url (str): The base url of the site
        articles (list): List of all articles found
    """
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.articles = []

    @abstractmethod
    def get_num_pages(self) -> int:
        """Get the total number of pages of articles

        Returns:
            Number of pages of articles
        """
        pass

    @abstractmethod
    def load_articles(self, num_pages: int):
        """Load the articles from the site into [articles]

        Note:
            This should not download the articles yet, this should just be parsing and getting headlines and links.

        Args:
            num_pages (int): The number of pages of articles to load
        """
        pass


class SixthToneScraper(Scraper):
    """Scraper for http://www.sixthtone.com"""
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
