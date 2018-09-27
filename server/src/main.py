import logging
from datetime import datetime

import requests

from backup import BackupProvider
from config import *
from distributor import DistributionProvider
from scraper import Scraper
from storage import StorageProvider

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')

fh = logging.FileHandler(
    os.path.realpath('{}/../../runs.log'.format(os.path.realpath(__file__)))
)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def main(
        backup_provider: BackupProvider,
        dist_provider: DistributionProvider,
        site_scraper: Scraper,
        storage_provider: StorageProvider
):
    logger.info('-' * 100)
    logger.info('Run at {}\n'.format(datetime.now()))

    logger.info('Retrieving articles...')
    prev_num_pages_checked = storage_provider.get_prev_num_pages_checked()
    total_pages = site_scraper.get_num_pages()
    # An example to clarify the following line:
    #
    # Let's say that at 12pm we scan the site for the first time and find 14 pages.
    # We want to scrape pages 1-14 (the latest 14 pages).
    # Since this is the first time, prev_num_pages_checked == 0. So we are scanning 14 - max(0, 1) + 1 = 14 pages.
    # Now let's say at 4pm we scan it again and we find 15 pages.
    # Now we want to scrape pages 14-15 (the latest 2 pages) since page 14 may not have been full last time we checked.
    # So prev_num_pages_checked == 14 and we are scanning 15 - max(14, 1) + 1 = 2 pages
    site_scraper.load_articles(total_pages - max(prev_num_pages_checked, 1) + 1)

    logger.info('Checking for new articles...')
    new_articles = list(filter(
        lambda a: not storage_provider.exists(a.orig_link),
        site_scraper.articles
    ))

    logger.info('Found {} new articles\n'.format(len(new_articles)))

    logger.info('Downloading and backing up new articles...')
    # TODO: these can be done in parallel asynchronously
    for article in new_articles:
        article.download()
        backup_provider.backup_article(article)
        storage_provider.save_article(article)
        article.dispose()
    storage_provider.set_num_pages_checked(total_pages)

    # TODO: this should be done before storing the new articles since there's no need to check the articles just added.
    logger.info('Searching for deleted articles and sharing them...')
    all_articles = storage_provider.get_all_articles()

    # TODO: these can be done in parallel asynchronously
    for article in all_articles:
        r = requests.head(article.orig_link)
        if r.status_code == 404:
            logger.info('{} was deleted. Sharing with group.\n\tOriginal link: {}\n\tBackup link: {}'.format(
                article.title,
                article.orig_link,
                article.backup_link
            ))

            success = dist_provider.share_article(article)
            if success:
                storage_provider.delete_article(article)

    logger.info('Done\n\n')


if __name__ == '__main__':
    backup = BACKUP_PROVIDER(**BACKUP_CONFIG)
    distribution = DISTRIBUTION_PROVIDER(**DISTRIBUTION_CONFIG)
    scraper = SCRAPER(**SCRAPER_CONFIG)
    storage = STORAGE_PROVIDER(**STORAGE_CONFIG)

    main(backup, distribution, scraper, storage)
