import asyncio, aiohttp
import copy
from bs4 import BeautifulSoup
from accless_tg_scraper.classes import *
from accless_tg_scraper.parser import *

class TgScraper():
    def __init__(self):
        self.base_url: str = TELEGRAM_WEB_URL
        self.timeouts = aiohttp.ClientTimeout(connect=0.6)
        self._headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'TE': 'trailers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:107.0) Gecko/20100101 Firefox/107.0'
        }
        
    def _url_preview(self, channel_name: str) -> str:
        return f"{self.base_url}/s/{channel_name}"
    
    def _url_post_widget(self, channel: str, post_id: int) -> str:
        return f"{self.base_url}/{channel}/{post_id}?embed=1&mode=tme"
    
    def _bs(self, response) -> BeautifulSoup:
        return BeautifulSoup(response, 'html.parser')    

    def _new_session(self, *args, **kwargs) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(headers=self._headers, timeout=self.timeouts)
    
    # Setters & getters:

    def set_headers(self, headers: dict):
        self._headers = copy.deepcopy(headers)

    def get_headers(self) -> dict:
        return copy.deepcopy(self._headers)

    # functions

    async def get_post(self, channel: str, post_id: int) -> TgPost:
        res = None
        async with self._new_session() as session:
            resp = await session.get(
                url=self._url_post_widget(channel, post_id))
            text = await resp.text()
        return parse_widget_post(self._bs(text))

    async def get_posts_page(self, channel: str, q: str = '', before = '', after = '', full_url: str = '') -> TgPostsPage:
        res = None
        params = {}

        if full_url == '':
            url = self._url_preview(channel)  

            params = {
                'q': str(q),
                'before': str(before),
                'after': str(after)
            }
        else:
            url = full_url

        async with self._new_session() as session:
            resp = await session.get(
                url=url,
                params=params)
            text = await resp.text()
            
        res = parse_posts_page(self._bs(text))
        return res
    