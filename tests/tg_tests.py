import asyncio
from bs4 import BeautifulSoup
from accless_tg_scraper.parser import *
from accless_tg_scraper.client import *
from accless_tg_scraper.classes import *
import re

DELIM = ''

def print_channel_info(c: TgChannelInfo):
    print(f'{c.display_name} - {c.name} - {c.subscribers} subs, {c.photos} photos, {c.videos} videos, {c.links} links. {c.url}')
    print(f'avatar: {c.avatar}')
    print(f'desc: {c.description}')
    if c.has_preview:
        print(f'channel has preview page.')

def print_post(post: TgPost):
    print('(' + post.author.name + ') ' + post.author.url + ' on ' + post.url + ' at ' + str(post.timestamp) + ' with ' + post.views + ' views.')
    
    if post.has_forward():
        print('📰 forwarded from: ' + post.forwarded_from.name + ' : ' + post.forwarded_from.url)
        
    if post.has_reply():
        print('✉️ reply: ' + post.reply.author_name + ' : ' + post.reply.url + ' : ' + post.reply.image_url)
        print('✉️ reply metatext: ' + post.reply.metatext)
        
    if post.content != "":
        print("Text: " +  post.content)
        
    if post.has_sticker():
        print('🗿 Sticker: ' + post.sticker.image_url)
        
    if post.has_not_supported:
        print('⚠️ Post has not supported media !')
        
    if post.has_voice():
        print(f'🔊 {post.voice.duration} -> {post.voice.url}')    
        
    if post.has_rounded_video():
        print(f'📹 {post.rounded_video.duration} -> {post.rounded_video.url}\nthumb: {post.rounded_video.thumbnail}')
    
    if post.has_images():
        for img in post.images:
            print('🌉 image: ' + img.url + ' : ' + img.url_single)
            
    if post.has_videos():
        for vid in post.videos:
            print('🎥 video: ' + vid.url + ' : ' + vid.image_url + ' : ' + vid.url_single)
            
    if post.has_link_previews():
        for link in post.link_previews:
            print('🔗 link (' + link.site_name + '): ' + link.url + ' - ' + link.title + ' - ' + link.description)
            print('🔗 link thumbnail: ' + link.image_url)

    if post.has_poll():
        print(f"❔: {post.poll.question} with {post.poll.voters} voters:")
        i = 0
        for opt in post.poll.options:
            i += 1
            print(f"{i} ) [{opt.percents}%]: {opt.value}")

    if post.has_invoice():
        print(f"💳: {post.invoice.title}: {post.invoice.description}")

def print_posts(posts: any):
    if type(posts) is TgPostsPage:
        posts = posts.posts
    print('Count: ' + str(len(posts)))
    for post in posts:
        print_post(post)
        print(DELIM)