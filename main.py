#!/usr/bin/python

import sys, getopt
import requests

def get_page(url):
    page = requests.get(url, verify=False)
    return page

def get_root_page(url):
    root_page = get_page(url)
    print(root_page.content)

def main(argv):
    opts, args = getopt.getopt(argv,"u:",["url="])
    for opt, arg in opts:
        if opt == '-h':
            print('main.py --url <rootURL>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg

    if(url):
        get_root_page(url)

if __name__ == "__main__":
   main(sys.argv[1:])