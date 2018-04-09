import scrapy


class NewsItem(scrapy.Item):
    url = scrapy.Field()
    published = scrapy.Field()
    topic = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
