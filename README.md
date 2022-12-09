### <img src="https://telegram.org/img/favicon.ico" height="20">  accless-tg-scraper
Scrap posts from telegram web WITHOUT account or API token
#### Install
```shell
python -m pip install "git+https://github.com/Kisspeace/accless-tg-scraper.git#egg=accless-tg-scraper" 
```
#### Simple example
```python
import asyncio
from accless_tg_scraper import *

async def main():
  telegram = TgScraper()
  page = await telegram.get_posts_page('evgenii_ponasenkov')
  posts = page.posts

  print(f'got {len(posts)} posts.')
  for post in posts:
    print(f'{post.url}:{post.content}\n')
    
asyncio.run(main())
```
