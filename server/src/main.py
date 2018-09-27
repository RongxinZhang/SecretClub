import logging
from datetime import datetime

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
    site_scraper.load_articles(total_pages - max(prev_num_pages_checked, 1) + 1)

    logger.info('Checking for new articles...')
    new_articles = list(filter(
        lambda a: not storage_provider.exists(a.orig_link),
        site_scraper.articles
    ))

    logger.info('Found {} new articles\n'.format(len(new_articles)))

    logger.info('Downloading and backing up new articles...')
    # TODO: these should be done in parallel asynchronously
    for article in new_articles:
        article.download()
        backup_provider.backup_article(article)
        storage_provider.save_article(article)
        article.dispose()
    storage_provider.set_num_pages_checked(total_pages)

    logger.info('Searching for deleted articles...')
    deleted_articles = storage_provider.get_deleted_articles()

    logger.info('Found {} deleted articles\n'.format(len(deleted_articles)))

    if deleted_articles:
        logger.info('Sharing deleted articles and clearing them from storage...')
        for article in deleted_articles:
            dist_provider.share_article(article)

    logger.info('Done\n\n')


if __name__ == '__main__':
    backup = BACKUP_PROVIDER(**BACKUP_CONFIG)
    distribution = DISTRIBUTION_PROVIDER(**DISTRIBUTION_CONFIG)
    scraper = SCRAPER(**SCRAPER_CONFIG)
    storage = STORAGE_PROVIDER(**STORAGE_CONFIG)

    main(backup, distribution, scraper, storage)
