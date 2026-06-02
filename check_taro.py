import urllib.request
from bs4 import BeautifulSoup
import sys

url = 'https://tool-taro.com/image_to_ascii/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')

# Find the label or text containing AA変換
elements = soup.find_all(string=lambda text: text and 'AA変換' in text)
for el in elements:
    print("Found text:", el.strip())
    # find the nearest textarea
    parent = el.find_parent('div') or el.find_parent('form') or el.parent
    if parent:
        textarea = parent.find_next('textarea')
        if textarea:
            print("Next textarea:", textarea.attrs)
        
        # also print style or class of parent
        print("Parent classes:", parent.get('class'))
        print("Parent style:", parent.get('style'))

