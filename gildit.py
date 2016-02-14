#! /usr/bin/env python
import cPickle as pickle
from bs4 import BeautifulSoup
import requests
import datetime


def get_content(url):
    r = requests.get(url, headers={'User-Agent': 'a user agent'})
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.find('h1', {'class': 'hero-title'}).get_text(' ', strip=True)
    text = soup.find("div", { "class" : "rte" }).get_text(' ', strip=True)
    slop = u'Gild drops\xa0the smartest talent acquisition stories in your inbox every week.\xa0Don\u2019t miss the good stuff. Sign up here'
    text = text.replace(slop, '')
    text = title + '. ' + text
    return text


def write_dict(_dict={}):
    with open('content.pkl', 'wb') as f:
        pickle.dump(_dict, f)


def insert_new_link():
    message = raw_input('Message: ')
    link = raw_input('Link: ')
    text = get_content(link)
    row = {
        str(datetime.datetime.now()): {
            'message': message,
            'link': link,
            'text': text
        }
    }
    with open('content.pkl') as f:
        content_dict = pickle.load(f)
    content_dict.update(row)
    write_dict(content_dict)


def main():
    insert_new_link()


if __name__ == '__main__':
    main()
