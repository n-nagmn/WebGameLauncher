import urllib.request
import re

url = 'https://tool-taro.com/image_to_ascii/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    textareas = re.findall(r'<textarea[^>]*>', html, re.IGNORECASE)
    print("TEXTAREAS:", textareas)
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    print("STYLES:", styles)
    css_links = re.findall(r'<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"', html, re.IGNORECASE)
    print("CSS LINKS:", css_links)
except Exception as e:
    print(e)
