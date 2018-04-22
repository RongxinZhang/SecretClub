import re
import requests

from bs4 import BeautifulSoup


URL_ROOT = "http://www.sixthtone.com/"

def getTotalPages():
    first_page = requests.get(URL_ROOT + "search/page/1/news?page=0&sort=1")

    soup = BeautifulSoup(first_page.content, "html.parser")
    page_string = str(soup)

    first_page_string = page_string.replace("\\u0022", "").replace("\\u003c", "").replace("\\u003e", "")
    total_pages = re.findall(r'pagination_total.*=(\d+)o', first_page_string, re.MULTILINE)[0]

    return int(total_pages)

def getAllLinks(total_pages):
    links = []
    titles = []
    # for i in range(1, int(total_pages)):
    # total_pages = min(total_pages, 3)
    print("Looking through {} pages".format(total_pages))

    for i in range(1, int(total_pages)):
        url = URL_ROOT + "search/page/1/news?page=" + str(i) + "&sort=1"
        print("GETING", url)
        search_page = requests.get(url)

        page_string = str(BeautifulSoup(search_page.content, "html.parser"))

        matches = re.findall(r'href=\\u0022\\/(news.*?)\\u0022', page_string, re.MULTILINE)

        for i, _ in enumerate(matches):
            if i % 2 == 0:
                link = matches[i].replace("\\", "")
                a = re.findall(r'news/[\d]+/([\w-]+)', link)
                if len(a) == 0:
                    continue
                title = a[0]
                links.append('{}{}'.format(URL_ROOT, link))
                titles.append(title)
    return links, titles

def download_save_pages(links, titles):
    for i, url in enumerate(links):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        f = open("/home/ubuntu/tmd/html/"+ titles[i] + ".html", "w+")
        f.write(str(soup))
        f.close()
