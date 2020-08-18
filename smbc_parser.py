from html.parser import HTMLParser
import requests

'''
Returns a random SMBC comic represented by a tuple: (title, image source, hovertext, after comic source)
'''
def get_random():
    comic = str(requests.get('https://www.smbc-comics.com/rand.php').content)[3:-2]
    print(comic)
    return SMBCParser(comic).parse()

'''
Returns the latest SMBC comic represented by a tuple: (title, image source, hovertext, after comic source)
'''
def get_latest():
    return SMBCParser('').parse()

'''
Parses SMBC webpage given the name of a comic in the constructor
'''
class SMBCParser(HTMLParser):
    def __init__(self, comic):
        super().__init__()
        self.div = None
        self.title = comic
        self.comic_embed = None
        self.hover_text = None
        self.after_comic_embed = None

    '''
    Returns the actual components of the comic itself parsed from the page
    '''
    def parse(self):
        smbc_page = str(requests.get(f"https://www.smbc-comics.com/comic/{self.current}").content)
        self.feed(smbc_page)
        return (self.title, self.comic_embed, self.hover_text, self.after_comic_embed)
    
    '''
    Internal function to help parse the webpage
    '''
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and 'id' in attrs:
            self.div = attrs['id']
        if self.div == 'cc-comicbody' and tag == 'img' and attrs['id'] == 'cc-comic':
            self.comic_embed = attrs['src']
            self.hover_text = attrs['title']
        if self.div == 'aftercomic' and tag == 'img':
            self.after_comic_embed = attrs['src'][2:-2]

