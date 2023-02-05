from datetime import datetime

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

class TgPost():
    def __init__(self):
        self.url: str = ''
        self.id: int = -1
        self.content: str = ''
        self.timestamp: datetime = datetime.now()
        self.author: TgChannel = TgChannel()
        self.views: str = '' # like '1.8k'
        self.images = [] # list of TgPostImage
        self.videos = [] # list of TgPostVideo
        self.voice: TgPostVoice = None
        self.rounded_video: TgPostRoundedVideo = None
        self.link_previews = [] # list of TgPostLinkPreview
        self.has_not_supported: bool = False # Media is too big : VIEW IN TELEGRAM
        self.forwarded_from: TgChannel = None
        self.reply: TgPostReply = None
        self.sticker: TgSticker = None
        self.poll: TgPoll = None
        self.invoice: TgPostInvoice = None
        
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

    def has_link_previews(self) -> bool:
        return len(self.link_previews) > 0
    
    def has_poll(self) -> bool:
        return self.poll != None
    
    def has_invoice(self) -> bool:
        return self.invoice != None
    
class TgPostsPage():
    def __init__(self):
        self.posts = [] # list of TgPost
        self.channel = TgChannelInfo() # channel info from right column on web page