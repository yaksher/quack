from html.parser import HTMLParser
import requests
import sqlite3
import re

def get_random():
    comic = str(requests.get('https://www.smbc-comics.com/rand.php').content)[3:-2]
    print(comic)
    return SMBCParser(comic).parse()

def get_latest():
    return SMBCParser('').parse()

class SMBCParser(HTMLParser):
    def __init__(self, comic):
        super().__init__()
        self.div = None
        self.current = comic
        self.comic = None
        self.title = None
        self.after_comic = None

    def parse(self):
        smbc_page = str(requests.get(f"https://www.smbc-comics.com/comic/{self.current}").content)
        self.feed(smbc_page)
        return (self.current, self.comic, self.title, self.after_comic)

    def get_next(self):
        smbc_page = str(requests.get(f"https://www.smbc-comics.com/comic/{self.current}").content)
        self.feed(smbc_page)
        return self.next


    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and 'id' in attrs:
            self.div = attrs['id']
        if self.div == 'cc-comicbody' and tag == 'img' and attrs['id'] == 'cc-comic':
            self.comic = attrs['src']
            self.title = attrs['title']
        if self.div == 'aftercomic' and tag == 'img':
            self.after_comic = attrs['src'][2:-2]

