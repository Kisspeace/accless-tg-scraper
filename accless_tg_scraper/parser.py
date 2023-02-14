from accless_tg_scraper.classes import *
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Tuple
import re

TELEGRAM_WEB_URL = 'https://t.me'

def channel_name_from_url(url: str, base_url: str = TELEGRAM_WEB_URL+'/') -> str:
    base = url.find(base_url)
    if base != -1:
        res = url[base+len(base_url):]
        snslash = res[:2]
        res = res[2:] if snslash == 's/' else res            
        last = res.rfind('/')
        last = res.rfind('?') if last == -1 else last
        res = res[:last] if last != -1 else res      
        return res
    else:
        return url

def post_id_from_url(url: str, base_url: str = TELEGRAM_WEB_URL+'/') -> int:
    base_end = url.find(base_url)  
    if base_end != -1:
        base_end += len(base_url)

    next_slash = url.find('/', base_end+1)
    if next_slash != -1:
        res = url[next_slash+1:]
        params_sign = res.find('?')
        if params_sign != -1:
            res = res[:params_sign]
        return res
    return None # default

def parse_bg_image_url(style_str: str) -> str:
    return re.search("background-image:url\('(.*?)'\)", style_str).group(1)

def parse_emoji(element: BeautifulSoup) -> TgEmoji:
    res = TgEmoji()
    if 'emoji-id' in element.attrs:
        res.id = element['emoji-id'] # Emoji id.

    tg_emoji_wrap = element.find(class_='tg-emoji-wrap')
    if tg_emoji_wrap is not None:

        tg_emoji: BeautifulSoup = tg_emoji_wrap.find(class_='tg-emoji')
        if tg_emoji is not None:
            res.custom = True
            res.custom_image_url = tg_emoji['data-webp']

            if res.custom_image_url in ('', None):
                # tgs file url.
                source_tgs = tg_emoji.find(attrs={'type': 'application/x-tgsticker'})
                res.tgs_url = source_tgs['srcset'] if source_tgs is not None else ''

                # svg+xml data.
                source_xml = tg_emoji.find(attrs={'type': 'image/svg+xml'})
                res.data = source_xml['srcset'] if source_xml is not None else ''

    # Original enoji image url.
    emoji = element.find(class_='emoji')
    if emoji is not None:
        res.image_url = parse_bg_image_url(emoji['style'])

    return res

def parse_text_with_entities(element: BeautifulSoup) -> Tuple[str, list[TgMessageEntity]]:
    """
    Args:
        element (BeautifulSoup): element for parse text from.

    Returns:
        Tuple: first item is a full text, second item is a list of entities.
    """
    FIX_ISSUES = True
    entities = []
    full_text: str = ''

    def create_entity(subject: BeautifulSoup) -> TgMessageEntity:
        if 'class' in subject.attrs:
            l_classes = subject.attrs['class']
        else:
            l_classes = []

        if (subject.name == 'tg-emoji') or ('emoji' in l_classes): # Telegram emoji.
            res = TgMessageEntityEmoji()
            res.emoji = parse_emoji(subject)
        elif subject.name == 'b': # Bold text.
            res = TgMessageEntityBold()
        elif subject.name == 'i': # Italic text.
            res = TgMessageEntityItalic()
        elif subject.name == 'a': # Hyperlink or user mention.
            res = TgMessageEntityUrl()
            res.url = subject['href']
        elif subject.name == 'u': # Underlined text.
            res = TgMessageEntityUnderlined()
        elif subject.name == 's': # Strikethrough text.
            res = TgMessageEntityStrikethrough()
        elif subject.name == 'tg-spoiler':
            res = TgMessageEntitySpoiler()
        # elif subject.name == '':
        #     pass
        return res

    def parse_entities(subject: BeautifulSoup, work_on_br: bool = True):
        DISALLOW_EMPTY_ENTITIES = True

        nonlocal full_text
        nonlocal entities

        for el in subject:
            if el.name is not None: # Is not just a text.
                if (el.name == 'br'):
                    # br tag must break line like on the web-page.
                    if work_on_br:
                        full_text += '\n'
                else:
                    # Create entity.
                    allow_entity = True
                    current_offset: int = len(full_text)
                    entity: TgMessageEntity = create_entity(el)
                    entity.offset = current_offset

                    parse_entities(el, True)
                    entity.length = len(full_text) - entity.offset

                    # Fixing entities that starts or ends with whitespace.
                    if FIX_ISSUES:
                        s = full_text[entity.offset : entity.offset + entity.length]
                        diff = entity.length - len(s.lstrip())
                        rdiff = entity.length - len(s.rstrip())
                        entity.offset += diff
                        entity.length -= (diff + rdiff)

                    if DISALLOW_EMPTY_ENTITIES:
                        if entity.length < 1:
                            allow_entity = False

                    if allow_entity:
                        entities.append(entity)
            else:
                full_text += el.text

    parse_entities(element)

    if FIX_ISSUES:
        stop = len(entities)
        for i in range(0, stop):
            ent = entities[i]

            # Cleaning entities inside emojis.
            if isinstance(ent, TgMessageEntityEmoji):
                for n in range(0, stop):
                    e = entities[n]
                    if (e is ent) or (e is None):
                        continue
                    if ent.same_place(e):
                        if isinstance(e, TgMessageEntityEmoji):
                            if ent.emoji.custom:
                                entities[n] = None
                            else:
                                entities[i] = None
                                break
                        elif isinstance(e, (TgMessageEntityBold, TgMessageEntityItalic)):
                            entities[n] = None

    # cleaning null objects.
    tmp_entities = []
    for ent in entities:
        if ent is not None:
            tmp_entities.append(ent)
    entities = tmp_entities

    return full_text, entities

def parse_channel_info(page: BeautifulSoup) -> TgChannelInfo:
    res = TgChannelInfo()
    tgme_page = page.find(class_='tgme_page')
    # Avatar
    photo = tgme_page.find(class_='tgme_page_photo')
    res.avatar = photo.find('img')['src']
    # Telegram username
    res.name = photo.find('a')['href']
    eq_sign = res.name.rfind('=')
    res.name = res.name[eq_sign+1:]
    # Url
    res.url = f'{TELEGRAM_WEB_URL}/{res.name}'
    # Display name
    res.display_name = tgme_page.find(class_='tgme_page_title').find('span').get_text()
    # Subscribers count
    extra = tgme_page.find(class_='tgme_page_extra')
    if not extra is None:
        extra = extra.get_text()
        s_pos = extra.find(' s')
        res.subscribers = extra[:s_pos]
    # Description
    desc = tgme_page.find(class_='tgme_page_description')
    if not desc is None:
        res.description = desc.get_text()
    preview_btn = tgme_page.find(class_='tgme_page_context_link')
    res.has_preview = (not preview_btn is None) 
    return res

def parse_right_column_channel_info(page: BeautifulSoup) -> TgChannelInfo:
    res = TgChannelInfo()
    res.has_preview = True
    tgme_channel_info = page.find(class_="tgme_channel_info")
    header = tgme_channel_info.find(class_='tgme_channel_info_header')
    # Avatar
    photo = header.find(class_='tgme_page_photo_image')
    res.avatar = photo.find('img')['src']
    title = header.find(class_='tgme_channel_info_header_title')
    # Display name
    res.display_name = header.find(class_='tgme_channel_info_header_title').find('span').get_text()
    # Url
    res.url = header.find(class_='tgme_channel_info_header_username').find('a')['href']
    # Telegram username
    res.name = channel_name_from_url(res.url)
    # All counters (subscribers, photos, videos, links)
    counters = tgme_channel_info.find(class_='tgme_channel_info_counters')
    counters = counters.find_all(class_='tgme_channel_info_counter')
    for counter in counters:
        value = counter.find(class_='counter_value').get_text()
        name = counter.find(class_='counter_type').get_text()
        setattr(res, name, value)
    # Description
    desc = tgme_channel_info.find(class_='tgme_channel_info_description')
    if not desc is None:
        res.description = desc.get_text()    
    return res

def parse_post_from_node(p: BeautifulSoup) -> TgPost:
    new_post = TgPost()
    tgme_widget_message = p.find(class_="tgme_widget_message", recursive=False)
    new_post.url = f"{TELEGRAM_WEB_URL}/{tgme_widget_message['data-post']}"      
    u = new_post.url
    new_post.id = int(u[u.rfind('/')+1:])

    # Author
    tgme_widget_message_user = p.find(class_="tgme_widget_message_user")
    tgme_widget_message_user_photo = tgme_widget_message_user.find(class_="tgme_widget_message_user_photo")
    new_post.author.url = str(tgme_widget_message_user.find("a")["href"])
    new_post.author.avatar = str(tgme_widget_message_user_photo.find("img")["src"])
    new_post.author.name = channel_name_from_url(new_post.author.url)

    # Author display_name
    tgme_widget_message_owner_name = p.find(class_="tgme_widget_message_owner_name")
    if not (tgme_widget_message_owner_name is None):
        try:
            span = tgme_widget_message_owner_name.find('span')
            new_post.author.display_name = span.get_text()
        except:
            pass

    # Reply info
    tgme_widget_message_reply = p.find(class_="tgme_widget_message_reply")
    if not tgme_widget_message_reply is None:
        new_post.reply = TgPostReply()
        new_post.reply.url = tgme_widget_message_reply['href']
        new_post.reply.author_name = tgme_widget_message_reply.find(class_="tgme_widget_message_author_name").get_text()
        try:
            tgme_widget_message_metatext = tgme_widget_message_reply.find(class_="tgme_widget_message_metatext")
            if not (tgme_widget_message_metatext is None):
                new_post.reply.metatext = tgme_widget_message_metatext.get_text()
            style = tgme_widget_message_reply.find(class_="tgme_widget_message_reply_thumb")['style']
            new_post.reply.image_url = parse_bg_image_url(style)
        except:
            pass

    # Forwarded from
    try:
        tgme_widget_message_forwarded_from_name = p.find(class_="tgme_widget_message_forwarded_from_name")
        if not tgme_widget_message_forwarded_from_name is None:
            new_post.forwarded_from = TgChannel()
            new_post.forwarded_from.name = tgme_widget_message_forwarded_from_name.find('span').get_text()
            new_post.forwarded_from.url = tgme_widget_message_forwarded_from_name['href']
    except:
        pass

    # Text content
    try:
        tgme_widget_message_text = p.find_all(class_="tgme_widget_message_text")
        if len(tgme_widget_message_text) > 1:
            message_text_elem = tgme_widget_message_text[1]
        else:
            message_text_elem = tgme_widget_message_text[0]
        # content = message_text_elem.get_text(separator = '\n\n', strip = True)
        # fix_line_breakers(message_text_elem)
        # content, msg_entities = parse_text_with_entities(message_text_elem)
        new_post.content, new_post.entities = parse_text_with_entities(message_text_elem)
        # new_post.content = content
    except:
        pass

    # Rounded video
    rounded_vid = p.find(class_="tgme_widget_message_roundvideo_player")
    if not (rounded_vid is None):
        new_post.rounded_video = TgPostRoundedVideo()
        thumb = rounded_vid.find(class_='tgme_widget_message_roundvideo_thumb')
        new_post.rounded_video.thumbnail = parse_bg_image_url(thumb['style'])
        vid = rounded_vid.find(class_='tgme_widget_message_roundvideo')
        new_post.rounded_video.url = vid['src']
        duration = rounded_vid.find(class_='tgme_widget_message_roundvideo_duration')
        new_post.rounded_video.duration = duration.get_text()

    # Voice
    voice_player = p.find(class_='tgme_widget_message_voice_player')
    if not (voice_player is None):
        voice = voice_player.find(class_="tgme_widget_message_voice") 
        if not (voice is None):
            new_post.voice = TgPostVoice()
            new_post.voice.url = voice['src']
            try:
                duration = voice_player.find(class_="tgme_widget_message_voice_duration")
                new_post.voice.duration = duration.get_text()
                new_post.voice.data_waveform = voice['data-waveform']
                new_post.voice.data_ogg = voice['data-ogg']
            except:
                pass

    # Images
    images = p.find_all(class_="tgme_widget_message_photo_wrap")
    for image in images:
        new_image = TgPostImage()
        style = image["style"]
        new_image.url = parse_bg_image_url(style)
        new_image.url_single = image["href"]
        new_post.images.append(new_image)

    # Supported videos
    videos = p.find_all(class_="tgme_widget_message_video_player")
    for vid in videos:
        new_video = TgPostVideo()
        style = vid.find(class_="tgme_widget_message_video_thumb")['style']

        try:
            new_video.image_url = parse_bg_image_url(style)
        except:
            pass

        try:
            new_video.url = vid.find(class_="tgme_widget_message_video")['src']
        except:
            pass

        new_video.url_single = vid['href']
        new_post.videos.append(new_video)

    # Link previews
    link_previews = p.find_all(class_="tgme_widget_message_link_preview")
    for prev in link_previews:
        new_prev = TgPostLinkPreview()
        new_prev.url = prev["href"]

        try:
            thumb = prev.find(class_="link_preview_image")
            if thumb is None:
                thumb = prev.find(class_="link_preview_right_image")
            if not thumb is None:    
                style = thumb['style']
                new_prev.image_url = parse_bg_image_url(style)

            new_prev.title = prev.find(class_="link_preview_title").get_text()
            new_prev.description = prev.find(class_="link_preview_description").get_text()
        except:
            pass

        new_prev.site_name = prev.find(class_="link_preview_site_name").get_text() 
        new_post.link_previews.append(new_prev)

    # Views
    tgme_widget_message_views = p.find(class_="tgme_widget_message_views")
    if not tgme_widget_message_views is None:
        new_post.views = str(tgme_widget_message_views.get_text())

    # Timestamp
    tgme_widget_message_date = p.find(class_="tgme_widget_message_date")
    time = tgme_widget_message_date.find("time")
    new_post.timestamp = datetime.fromisoformat(time["datetime"])

    # Sticker
    tgme_widget_message_sticker_wrap = p.find(class_='tgme_widget_message_sticker_wrap')
    if not tgme_widget_message_sticker_wrap is None:
        new_post.sticker = TgSticker()

        # static sticker
        tgme_widget_message_sticker = p.find(class_='tgme_widget_message_sticker')
        if not tgme_widget_message_sticker is None:
            if 'data-webp' in tgme_widget_message_sticker.attrs:
                new_post.sticker.image_url = tgme_widget_message_sticker['data-webp']

        # Animated sticker
        tgme_widget_message_videosticker = p.find(class_='tgme_widget_message_videosticker')
        if not tgme_widget_message_videosticker is None:
            new_post.sticker.animated = True

            js_videosticker_video = tgme_widget_message_videosticker.find(class_='js-videosticker_video')
            if js_videosticker_video is not None:
                new_post.sticker.video_url = js_videosticker_video['src']

            webm_sticker_done = js_videosticker_video.find(class_='webm_sticker_done')
            if webm_sticker_done is not None:
                new_post.sticker.image_url = webm_sticker_done['src']

            if new_post.sticker.image_url == '':
                img = js_videosticker_video.find('img')
                if img is not None:
                    new_post.sticker.image_url = img['src']
                # new_post.sticker.image_url = parse_bg_image_url(tgme_widget_message_videosticker['style'])

    # Detect unsupported media
    message_media_not_supported_wrap = p.find(class_="message_media_not_supported_wrap")
    if not (message_media_not_supported_wrap is None):
        message_media_not_supported_label = message_media_not_supported_wrap.find(class_="message_media_not_supported_label")
        if not (message_media_not_supported_label is None):
            not_support_msg = message_media_not_supported_label.get_text()
            new_post.has_not_supported = (not_support_msg.find('in your browser') == -1)
        else:
            new_post.has_not_supported = True

    # Poll
    tgme_widget_message_poll = p.find(class_="tgme_widget_message_poll")
    if not (tgme_widget_message_poll is None):
        try:
            new_post.poll = TgPoll()

            # Question
            question = tgme_widget_message_poll.find(class_='tgme_widget_message_poll_question')
            new_post.poll.question = question.get_text()

            # Poll type
            tgme_widget_message_poll_type = tgme_widget_message_poll.find(class_="tgme_widget_message_poll_type")
            new_post.poll.type = tgme_widget_message_poll_type.get_text()

            # Options
            tgme_widget_message_poll_options = tgme_widget_message_poll.find(class_='tgme_widget_message_poll_options')  
            options = tgme_widget_message_poll_options.find_all(class_='tgme_widget_message_poll_option')
            for opt in options:
                new_opt = TgPoll.TgPollOption()
                new_opt.value = opt.find(class_="tgme_widget_message_poll_option_value").get_text().strip()
                percents = opt.find(class_='tgme_widget_message_poll_option_percent')
                if not (percents is None):
                    percents = percents.get_text()
                    percents = percents[:len(percents)-1]
                    new_opt.percents = int(percents)
                    new_post.poll.options.append(new_opt)

            # Voters count        
            voters = p.find(class_="tgme_widget_message_voters") 
            if not (voters is None):
                new_post.poll.voters = voters.get_text()
            else:
                voters = p.find(class_="tgme_widget_message_poll_votes")
                voters = voters.get_text()
                space_pos = voters.rfind(' ')
                if space_pos != -1:
                    voters = voters[:space_pos-1]
                new_post.poll.voters = voters
        except:
            pass

    # Invoice
    tgme_widget_message_invoice = p.find(class_="tgme_widget_message_invoice")
    if not (tgme_widget_message_invoice is None):
        new_post.invoice = TgPostInvoice()
        title = tgme_widget_message_invoice.find(class_='tgme_widget_message_invoice_title')
        new_post.invoice.title = title.get_text()
        desc = tgme_widget_message_invoice.find(class_='tgme_widget_message_invoice_description')
        new_post.invoice.description = desc.get_text()

    return new_post

def parse_widget_post(page: BeautifulSoup) -> TgPost:
    p = page.find(class_="widget_frame_base")
    return parse_post_from_node(p)

def parse_posts(page: BeautifulSoup) -> []:
    history = page.find(class_="tgme_channel_history")
    p_posts = history.find_all(class_="tgme_widget_message_wrap", recursive=False)
    posts = []

    for p in p_posts:
        new_post = parse_post_from_node(p)    
        posts.append(new_post)

    return posts

def parse_posts_page(page: BeautifulSoup):
    res = TgPostsPage()
    res.posts = parse_posts(page)
    res.channel = parse_right_column_channel_info(page)
    return res
