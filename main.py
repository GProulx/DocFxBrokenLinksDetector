#!/usr/bin/python

import sys
import getopt
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_page(url):
    page = requests.get(url, verify=False)
    # for header in page.headers:
    #     print(header, ":", page.headers[header])

    # # for header in page.headers:
    # #     print(header, ":", page.headers[header])

    # print("Page.History: ", len(page.history))

    # print("Page.links: ", page.links)

    # print("Page.next: ", page.next)

    # print(page.request)
    return page


def get_page_content(page_content):
    soup = BeautifulSoup(page_content, "lxml")
    return soup.find_all('a')


def is_valid_url(url):
    import re

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None


def process_page_content(url, links):
    # urljoin('/media/path/', 'js/foo.js')

    print("process_page_content")

    for link in links:
        if is_valid_url(link.get('href')):
            print("VALID:", link.get('href'))
        else:
            print(urljoin(url, link.get('href')))


def get_root_page(url):
    root_page=get_page(url)

    page_content=get_page_content(root_page.content)

    process_page_content(url, page_content)


def main(argv):
    opts, args=getopt.getopt(argv, "u:", ["url="])
    for opt, arg in opts:
        if opt == '-h':
            print('main.py --url <rootURL>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url=arg

    if(url):
        get_root_page(url)


if __name__ == "__main__":
    main(sys.argv[1:])
