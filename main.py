#!/usr/bin/python

from bs4 import BeautifulSoup
from queue import Queue
from urllib.parse import urljoin
import getopt
import requests
import sys
import socket
from requests.models import HTTPError
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pages_queue = Queue(maxsize=0)
pages_history = []
debug = False


def request_page(url):
    try:
        page = requests.get(url, verify=False)
        return page
    except socket.gaierror:
        return None


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

    try:
        return re.match(regex, url) is not None
    except TypeError:
        print("[ERROR] Problem validating url", url)
        raise


def is_external_link(url, link):
    # this should be improved...
    return not link.startswith(url)


def is_link_available(link):
    try:
        response = request_page(link)
        if response == None:
            return False
        else:
            if response.status_code == 401:
                return True
            else:
                return response.ok

    except Exception as ex:
        # print(ex)
        return False


def process_page_content(url, links):
    for link in links:

        if link.get('href') == None:
            continue

        if is_valid_url(link.get('href')):
            link = link.get('href')
            if (is_external_link(url, link)):
                is_valid = is_link_available(link)
                if debug:
                    print("EXTERNAL LINK:", link, is_valid)
                if not is_valid:
                    print("[ERROR] EXTERNAL LINK:", link)
            else:
                if debug:
                    print("INTERNAL FULL LINK:", link)
        else:
            full_url = urljoin(url, link.get('href'))
            if debug:
                print(full_url)
            if is_link_available(full_url):
                # print()
                pages_queue.put(full_url)
            else:
                print("[ERROR] Page", url, "has a broken link pointing to",
                      link.get('href'))


def get_page_hash(page_content):
    import hashlib
    hash_object = hashlib.md5(page_content)
    hash = hash_object.hexdigest()
    # print(hash)
    return (hash)


def process_page_queue(root_url):
    url = pages_queue.get()

    if debug:
        print("Processing page:", url)

    response = request_page(url)

    page_content = get_page_content(response.content)

    page_hash = get_page_hash(response.content)

    if page_hash not in pages_history:
        pages_history.append(page_hash)
        process_page_content(url, page_content)


def main(argv):
    url = None
    opts, args = getopt.getopt(argv, "u:", ["url=", "url2="])
    for opt, arg in opts:
        if opt == '-h':
            print('main.py --url <rootURL>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg

    if(url):
        root_url = url
        pages_queue.put(root_url)
        pages_queue.put(urljoin(root_url, "/fr/toc.html"))
        pages_queue.put(urljoin(root_url, "/en/toc.html"))
        while (not pages_queue.empty()):
            process_page_queue(root_url)
        print("Process completed!")


if __name__ == "__main__":
    main(sys.argv[1:])
