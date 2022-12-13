from setuptools import setup

setup(
    name = 'accless_tg_scraper',
    version = '0.1.0',
    author='Kisspeace',
    keywords='telegram scraper parser web',
    url='http://github.com/Kisspeace/accless-tg-scraper',
    description='Scrap telegram web WITHOUT account or API token',
    packages = ['accless_tg_scraper', 
                'accless_tg_scraper.serialize'],
    install_requires=[
        'aiohttp',
        'bs4'
    ]
)
