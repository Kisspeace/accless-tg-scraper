#!python
from bs4 import BeautifulSoup
from accless_tg_scraper.parser import *
import re
from tg_tests import *
from accless_tg_scraper.serialize.markdown import *
import os
import fnmatch

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

posts = []

def add_post(filename: str) -> TgPost:
    global posts
    web_page = bs_from_file(filename)
    post = parse_widget_post(web_page)
    print_post(post)
    posts.append(post)
    return post

def add_posts(filename: str) -> list[TgPost]:
    global posts
    web_page = bs_from_file(filename)
    new_posts = parse_posts(web_page)
    print_posts(new_posts)
    posts = posts + new_posts

for f in os.listdir(os.curdir):
    if fnmatch.fnmatch(f, 'tg-single-post*'):
        add_post(f)
    elif fnmatch.fnmatch(f, 'tg-posts*'):
        add_posts(f)

# new = []
# for p in posts:
#     if p.has_service_msg():
#         new.append(p)
#         print(f'service msg_ {p.service_msg.type} : {p.service_msg.extra}')
# posts = new

dump_posts(posts, 'dump.md', 'a')
