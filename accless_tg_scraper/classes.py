from datetime import datetime

# Consts
TG_SERVICE_MSG_UNKNOWN = -1
TG_SERVICE_MSG_CHANNEL_CREATED = 0
TG_SERVICE_MSG_CHANNEL_RENAMED = 1
TG_SERVICE_MSG_CHANNEL_PHOTO_REMOVED = 2
TG_SERVICE_MSG_CHANNEL_PHOTO_UPDATED = 3
TG_SERVICE_MSG_LIVE_STREAM_FINISHED = 4
TG_SERVICE_MSG_LIVE_STREAM_SHEDULED = 5
TG_SERVICE_MSG_PINNED = 6

# Document types:
TG_DOCUMENT_UNKNOWN = -1
TG_DOCUMENT_AUDIO = 0

class TgChannel():
    def __init__(self):
        self.url: str = ''
        self.avatar: str = ''
        self.name: str = ''
        self.display_name: str = ''

class TgChannelInfo(TgChannel):
    def __init__(self):
        TgChannel.__init__(self)
        self.subscribers: str = '' # like '73.2 k'
        self.photos: str = ''
        self.videos: str = ''
        self.links: str = ''
        self.description: str = ''
        self.has_preview: bool = None # can be parsed from links like 'https://t.me/channel_name'

class TgPostVoice():
    def __init__(self):
        self.url: str = ''
        self.data_waveform: str = ''
        self.data_ogg: str = '' # sometimes empty
        self.duration: str = '' # like '0:25'

class TgPostRoundedVideo():
    def __init__(self):
        self.url: str = ''
        self.thumbnail: str = ''
        self.duration: str = ''

class TgPostImage():
    def __init__(self):
        self.url: str = ''
        self.url_single: str = ''

class TgPostInvoice():
    def __init__(self):
        self.title: str = ''
        self.description: str = ''

class TgPostVideo(TgPostImage):
    def __init__(self):
        TgPostImage.__init__(self)
        self.image_url: str = '' # thumbnail

class TgPostReply():
    def __init__(self):
        self.author_name: str = ''
        self.url: str = ''
        self.image_url = ''    
        self.metatext: str = ''

class TgPostLinkPreview():
    def __init__(self):
        self.site_name: str = '' # like 'YouTube'
        self.url: str = ''
        self.title: str = ''
        self.description: str = ''
        self.image_url: str = ''

class TgSticker():
    def __init__(self):
        self.animated: bool = False
        self.image_url: str = ""
        self.video_url: str = ""

class TgPoll():

    class TgPollOption():
        def __init__(self):
            self.value: str = ''
            self.percents: int = -1

    def __init__(self):
        self.type: str = '' # Like 'Anonymous poll'
        self.question: str = ''
        self.options = [] # list of TgPollOption
        self.voters: str = '' # like '32.3k'

class TgEmoji():
    """Telegram emoji.
    id: Emoji id.
    custom: True if its a custom emoji.
    animated: True if its animated emoji.
    image_url: Original representation of emoji (also available for a custom).
    custom_image_url: Custom representation of emoji.
    data: Image svg+xml data.
    tgs_url: link on .tgs file.

    """
    def __init__(self):
        self.id: int = -1 # Emoji id.
        self.custom: bool = False
        self.animated: bool = False
        self.image_url: str = ''
        self.custom_image_url: str = ''
        self.data: str = '' # Image data as text.
        self.tgs_url = '' # link on .tgs file.

class TgMessageEntity():
    """Base class for all message entities.
    See: https://core.telegram.org/api/entities

    offset: Offset in string.
    length: Characters count.
    """
    def __init__(self, offset: int, length: int):
        self.offset = offset # Offset in string
        self.length = length # Characters count

    def same_place(self, entity) -> bool:
        return (self.offset == entity.offset) and (self.length == entity.length)

    def starts_after(self, entity) -> bool:
        """
        Returns:
            bool: True if current entity start position is bigger than end position of given entity.
        """
        return (self.offset >= (entity.offset + entity.length))

    def starts_inside(self, entity) -> bool:
        """
        Returns:
            bool: True if current entity starts inside given entity.
        """
        return (not self.starts_after(entity)) and (self.offset >= entity.offset)
    
class TgMessageEntityUrl(TgMessageEntity):
    """Message entity with text and url behind the text.
    """
    def __init__(self, offset: int = 0, length: int = 0, url: str = ''):
        TgMessageEntity.__init__(self, offset, length)
        # self.text: str = text
        self.url: str = url

class TgMessageEntityEmoji(TgMessageEntity):
    """Message entity with telegram emoji.
    """
    def __init__(self, offset: int = 0, length: int = 0):
        TgMessageEntity.__init__(self, offset, length)
        self.emoji: TgEmoji = None

class TgMessageEntityBold(TgMessageEntity):
    """Message entity with bold text.
    """
    def __init__(self, offset: int = 0, length: int = 0):
        TgMessageEntity.__init__(self, offset, length)

class TgMessageEntityItalic(TgMessageEntity):
    """Message entity with italic text.
    """
    def __init__(self, offset: int = 0, length: int = 0):
        TgMessageEntity.__init__(self, offset, length)

class TgMessageEntityStrikethrough(TgMessageEntity):
    """Message entity with Strikethrough text.
    """
    def __init__(self, offset: int = 0, length: int = 0):
        TgMessageEntity.__init__(self, offset, length)

class TgMessageEntityUnderlined(TgMessageEntity):
    """Message entity with underlined text.
    """
    def __init__(self, offset: int = 0, length: int = 0):
        TgMessageEntity.__init__(self, offset, length)

class TgMessageEntitySpoiler(TgMessageEntity):
    """Message entity with hidden text.
    """
    def __init__(self, offset: int = 0, length: int = 0):
        TgMessageEntity.__init__(self, offset, length)

class TgServiceMessage():
    def __init__(self):
        self.type: int = TG_SERVICE_MSG_UNKNOWN
        self.extra: str = '' # (url, text) depends on type

class TgDocument():
    def __init__(self):
        self.type: int = TG_DOCUMENT_UNKNOWN
        self.url: str = ''
        self.title: str = ''
        self.extra: str = ''

class TgPost():
    def __init__(self):
        self.url: str = ''
        self.id: int = -1
        # self.type: int = TG_MESSAGE
        self.content: str = ''
        self.entities: list[TgMessageEntity] = []
        self.timestamp: datetime = datetime.now()
        self.author: TgChannel = TgChannel()
        self.views: str = '' # like '1.8k'
        self.images: list[TgPostImage] = []
        self.videos: list[TgPostVideo] = []
        self.documents: list[TgDocument] = [] # list of attached files
        self.voice: TgPostVoice = None
        self.rounded_video: TgPostRoundedVideo = None
        self.link_previews: list[TgPostLinkPreview] = []
        self.has_not_supported: bool = False # Media is too big : VIEW IN TELEGRAM
        self.forwarded_from: TgChannel = None
        self.reply: TgPostReply = None
        self.sticker: TgSticker = None
        self.poll: TgPoll = None
        self.invoice: TgPostInvoice = None
        self.service_msg: TgServiceMessage = None
        
    def has_service_msg(self) -> bool:
        return self.service_msg != None

    def has_forward(self) -> bool:
        return self.forwarded_from != None

    def has_reply(self) -> bool:
        return self.reply != None

    def has_sticker(self) -> bool:
        return self.sticker != None

    def has_voice(self) -> bool:
        return self.voice != None

    def has_rounded_video(self) -> bool:
        return self.rounded_video != None

    def has_images(self) -> bool:
        return len(self.images) > 0

    def has_videos(self) -> bool:
        return len(self.videos) > 0

    def has_entities(self) -> bool:
        return len(self.entities) > 0

    def has_link_previews(self) -> bool:
        return len(self.link_previews) > 0

    def has_documents(self) -> bool:
        return len(self.documents) > 0

    def has_poll(self) -> bool:
        return self.poll != None

    def has_invoice(self) -> bool:
        return self.invoice != None

class TgPostsPage():
    def __init__(self):
        self.posts: list[TgPost] = []
        self.channel = TgChannelInfo() # channel info from right column on web page
