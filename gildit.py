#! /usr/bin/env python
import json
from bs4 import BeautifulSoup
import requests


def get_content_dict():
    with open('content.json') as f:
        content = json.load(f)
    return content


def get_content(url):
    r = requests.get(url, headers={'User-Agent': 'a user agent'})
    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.find('h1', {'class': 'the-title'}).get_text(' ', strip=True)
    text = ''
    for p in soup.find("div", { "class" : "rte" }).find_all('p'):
        text += ' ' + p.get_text(' ', strip=True)
    slop = u'Gild drops\xa0the smartest talent acquisition stories in your inbox every week.\xa0Don\u2019t miss the good stuff. Sign up here'
    text = text.replace(slop, '')
    text = ' '.join(text.split())
    if text[-3:] == '. .':
        text = text[:-2]
    return text, title


def write_dict(new_dict):
    with open('content.json', 'wb') as f:
        json.dump(new_dict, f, indent=4)


def insert_new_link(message=None, link=None):
    if not message or not link:
        message = raw_input('Message: ')
        link = raw_input('Link: ')
    text, title = get_content(link)
    row = {
            'message': message,
            'link': link,
            'text': text,
            'title': title
    }
    content = get_content_dict()
    content.append(row)
    write_dict(content)


def main():
    insert_new_link()


if __name__ == '__main__':
    main()
