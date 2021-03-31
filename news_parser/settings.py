BOT_NAME = 'news_parser'

SPIDER_MODULES = ['news_parser.spiders']
NEWSPIDER_MODULE = 'news_parser.spiders'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 1

FEED_EXPORT_FIELDS = ['url', 'published', 'topic', 'title', 'text']
