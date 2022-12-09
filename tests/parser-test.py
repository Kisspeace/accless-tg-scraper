#!python
from bs4 import BeautifulSoup
from accless_tg_scraper.parser import *
import re
from tg_tests import *

def bs_from_file(filename: str) -> BeautifulSoup:
    fp = open(filename)
    page = BeautifulSoup(fp, 'html.parser')
    return page

def test_url_parse(url: str):
    print(F"{channel_name_from_url(url)} from {url}")

def test_post_id_parse(url: str):
    print(F"{post_id_from_url(url)} from {url}")
    
test_url_parse('https://t.me/s/channel_name')
test_url_parse('https://t.me/s/channel_name?after=1030')
test_url_parse('https://t.me/channel_name/752')
test_url_parse('https://t.me/channel_name?someparams=sgduh23847tgdhs')
test_url_parse('https://t.me/channel_name')
test_url_parse('channel_name')

test_post_id_parse('https://t.me/channel_name/1812')
test_post_id_parse('https://t.me/channel_name/1488?embed=1&mode=tme')

page = bs_from_file('tg-single-post-1.html')
print_post(parse_widget_post(page))
print(DELIM)

page = bs_from_file('tg-posts-1.html')
posts = parse_posts(page)
print_posts(posts)
print(DELIM)
