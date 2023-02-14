from accless_tg_scraper.serialize.markdown import *
from accless_tg_scraper.serialize.classes import *
from accless_tg_scraper.classes import *

text = 'Hello. md has no spoilers support'
entities = [
    TgMessageEntityItalic(1, 2),
    TgMessageEntityBold(1, 2),
    TgMessageEntityUrl(0, 1, 'https://youtu.be/HTMDNZOlUq4'),
    TgMessageEntityStrikethrough(3, 3),
    TgMessageEntityBold(4, 1),
    TgMessageEntitySpoiler(7, 26)
]

md = dump_content(text, entities, RULE_SET_MD)
print(md)