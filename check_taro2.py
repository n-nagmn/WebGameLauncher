import urllib.request
from bs4 import BeautifulSoup

url = 'https://tool-taro.com/image_to_ascii/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')
textarea = soup.find('textarea', {'name': 'result'})
if textarea:
    print("TEXTAREA HTML:", str(textarea))
    print("PARENT HTML:", str(textarea.parent))
