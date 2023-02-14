from accless_tg_scraper.classes import *
from accless_tg_scraper.serialize.classes import *
from copy import deepcopy

class TgEntityRuleSetMarkdown(TgEntityRuleSet):

    class EntityRuleUrl(TgEntityRuleSet.EntityRule):
        def __init__(self, ent_type=TgMessageEntityUrl, prefix='[', postfix=']'):
            TgEntityRuleSet.EntityRule.__init__(self, ent_type=TgMessageEntityUrl, prefix='[', postfix=']')
            self.prefix = prefix
            self.postfix = postfix
            self.url_prefix: str = '('
            self.url_postfix: str = ')'

        def convert(self, entity: TgMessageEntity, source: str):
            sub_str = source[entity.offset : entity.offset + entity.length]
            return f'{self.prefix}{sub_str}{self.postfix}{self.url_prefix}{entity.url}{self.url_postfix}'

    def __init__(self):
        TgEntityRuleSet.__init__(self)
        self.bold = self.EntityRule(TgMessageEntityBold,  '**', '**')
        self.italic = self.EntityRule(TgMessageEntityItalic, '*', '*')
        self.strikethrogh = self.EntityRule(TgMessageEntityStrikethrough, '~~', '~~')
        self.underlined = self.EntityRule(TgMessageEntityUnderlined, '<u>', '</u>')
        self.url = self.EntityRuleUrl()
        self.spoiler = self.EntityRule(TgMessageEntitySpoiler, '', '')
        self.emoji = self.EntityRule(TgMessageEntityEmoji, '', '')

# global entity rule set for markdown.
RULE_SET_MD = TgEntityRuleSetMarkdown()

def dump_posts(posts: list[TgPost], file: any, fmode: str = 'a') -> None:
    if isinstance(file, str):
        file = open(file, mode=fmode)
        opened_localy = True
    else:
        opened_localy = False

    def out(string: str) -> None:
        file.write(string)

    for post in posts:
        out(f'### [{post.author.display_name}]({post.author.url}): [post]({post.url}) at {post.timestamp} with {post.views} views.  \n')

        if post.has_forward():
            out(f'**📰 forwarded from**: [{post.forwarded_from.name}]({post.forwarded_from.url})  \n')

        if post.has_reply():
            out(f'**✉️ reply**: [{post.reply.author_name}]({post.reply.url})  \n')
            out(f'**✉️ reply metatext**: {post.reply.metatext}  \n')

        if post.content != '':
            content = dump_content(post.content, post.entities, RULE_SET_MD)
            content = content.replace('\n', '  \n')
            out(f'{content}  \n')

        if post.has_sticker():
            if not post.sticker.animated:
                out(f'[🗿 Sticker]({post.sticker.image_url})  \n')
            else:
                out(f'[🗿 Sticker]({post.sticker.video_url}) [thumb]({post.sticker.image_url})  \n')

        if post.has_not_supported:
            out(f'~~⚠️ Post has not supported media !~~  \n')

        if post.has_voice():
            out(f'[🔊 {post.voice.duration}]({post.voice.url})  \n')    

        if post.has_rounded_video():
            out(f'[📹 {post.rounded_video.duration}]({post.rounded_video.url})  \n ![thumbnail]({post.rounded_video.thumbnail})  \n')

        if post.has_images():
            for img in post.images:
                out(f'![🌉 image]({img.url})  \n')

        if post.has_videos():
            for vid in post.videos:
                if vid.url:
                    out(f'[🎥 video]({vid.url})  \n')

        if post.has_link_previews():
            for link in post.link_previews:
                out(f'[🔗 link ({link.site_name})]({link.url}): {link.title} - {link.description}  \n')
                out(f'[🔗 link thumbnail]({link.image_url})  \n')

        if post.has_poll():
            out(f'**❔ poll**: {post.poll.question} with {post.poll.voters} voters:  \n')
            i = 0
            for opt in post.poll.options:
                i += 1
                out(f'{i} ) [{opt.percents}%]: {opt.value}  \n')

        if post.has_invoice():
            out(f'**💳 invoice**: {post.invoice.title}: {post.invoice.description}  \n')

        out(f'\n')

    if opened_localy:
        file.close()
