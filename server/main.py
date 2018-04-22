from datetime import datetime
from helpers import check_if_link_downloaded, get_deleted_articles, send_telegram_message, upload_to_ipfs
from scraper import getTotalPages, getAllLinks, download_save_pages

def main():
    print()
    print()
    print('-' * 100)
    print('Scheduled run at {}'.format(datetime.now()))

    print('Running scraper')
    links, titles = getAllLinks(getTotalPages())

    print('Checking for new articles')
    new_links = []
    new_titles = []
    for i, link in enumerate(links):
        if not check_if_link_downloaded(link):
            new_links.append(link)
            new_titles.append(titles[i])

    print()
    print('Found {} new articles'.format(len(new_links)))

    print('Downloading new articles')
    download_save_pages(new_links, new_titles)

    print('Uploading new articles to IPFS')
    for link, title in zip(new_links, new_titles):
        upload_to_ipfs(link, title)

    print()
    print('Searching for deleted articles')
    deleted_articles = get_deleted_articles()

    print('Found {} deleted articles'.format(len(deleted_articles)))

    print('Sending deleted articles to telegram group and clearing them from Redis store')
    for article in deleted_articles:
        send_telegram_message('{}\nipfs.io/ipfs/{}'.format(article['headline'], article['ipfs_link']))

    print()
    print('Done')

main()
