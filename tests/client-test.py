#!python
import asyncio
from bs4 import BeautifulSoup
from accless_tg_scraper.client import *
from accless_tg_scraper.classes import *
import re
from tg_tests import *
from accless_tg_scraper.serialize.markdown import *

tg = TgScraper()
last_posts_page = None

ponasenkov_tg = 'evgenii_ponasenkov'

async def get_n_print(channel: str, *args, **kwargs):
    global last_posts_page
    posts_page = await tg.get_posts_page(channel=channel, *args, **kwargs)
    last_posts_page = posts_page
    print_posts(posts_page)

async def main():    
    await get_n_print(ponasenkov_tg)
    await get_n_print(ponasenkov_tg, before=last_posts_page.posts[0].id) 
    post = await tg.get_post(ponasenkov_tg, 7561)
    print_post(post)
    print(DELIM)
if __name__ == '__main__':
    asyncio.run(main())