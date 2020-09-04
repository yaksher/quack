from html.parser import HTMLParser
import requests
import re

'''
Returns a random SMBC comic represented by a tuple: (title, url, image source, hovertext, after comic source)
'''
def get_random():
    comic = str(requests.get('https://www.smbc-comics.com/rand.php').content)[3:-2]
    return SMBCParser(comic).parse()

'''
Returns the latest SMBC comic represented by a tuple: (title, url, image source, hovertext, after comic source)
'''
def get_latest():
    url = "https://www.smbc-comics.com/comic/"
    smbc_page = requests.get(url).text
    # HTML parsing with regex because I'm too lazy to learn to use the HTML parser.
    tmp = re.search(r'id="permalinktext" type="text" value="http://smbc-comics.com/comic/.+"', smbc_page).group()
    title = re.search(r'value="http://smbc-comics.com/comic/.+"', tmp).group()[36:-1]
    return SMBCParser(title).parse()


'''
Returns a specific comic by title.
'''
def get_comic(title):
    return SMBCParser(title).parse()

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
        url = f"https://www.smbc-comics.com/comic/{self.title}"
        smbc_page = requests.get(url).text
        self.feed(smbc_page)
        return (self.title, url, self.comic_embed, self.hover_text, self.after_comic_embed)
    
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
            self.after_comic_embed = attrs['src']

