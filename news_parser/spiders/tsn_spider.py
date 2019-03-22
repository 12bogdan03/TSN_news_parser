import scrapy
import json
import re

from news_parser.items import NewsItem


class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['tsn.ua']
    start_urls = [
        'https://tsn.ua/ajax/show-more/politika?page=1',
        'https://tsn.ua/ajax/show-more/groshi?page=1',
        'https://tsn.ua/ajax/show-more/ato?page=1',
        'https://tsn.ua/ajax/show-more/tourism?page=1',
        'https://tsn.ua/ajax/show-more/nauka_it?page=1',
        'https://tsn.ua/ajax/show-more/books?page=1',
        'https://tsn.ua/ajax/show-more/glamur?page=1'
    ]
    allowed_topics = ['політика', 'економіка', 'ато', 'туризм',
                      'наука та it', 'книжки', 'гламур']

    def parse(self, response):
        json_response = json.loads(response.body.decode("utf-8"))
        next_page = json_response['next']
        news_urls = re.findall(r'<a\shref="(https?://tsn\.ua/.+?\d+?\.html)"',
                               json_response['html'])
        for url in news_urls:
            yield scrapy.Request(url=url, callback=self.parse_news)

        if next_page and not next_page.endswith('100'):
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_news(self, response):
        item = NewsItem()
        item['url'] = response.request.url
        item['published'] = response.xpath(
            '//meta[@property="article:published_time"]/@content'
        ).extract_first().split('T')[0]
        item['topic'] = self.topic_from_url(response.request.url)
        item['title'] = self.get_title(response)
        summary = response.css('div.o-cmr.u-content-read.js-select-bar-wrap >'
                               ' p::text').extract_first()
        raw_content = ' '.join(
            response.css('div.u-pos-r > article > div > p').extract()
        )
        content = self.clean_content(raw_content)
        item['text'] = ' '.join((summary, content)) if summary and content else content
        if item['topic'] and item['topic'].lower() in self.allowed_topics:
            yield item

    @staticmethod
    def topic_from_url(url):
        variants = {
            'politika': 'Політика',
            'groshi': 'Економіка',
            'ato': 'АТО',
            'tourism': 'Туризм',
            'nauka_it': 'Наука та IT',
            'books': 'Книжки',
            'glamur': 'Гламур'
        }
        url_topic = url.split('/')[3]
        return variants.get(url_topic)

    @staticmethod
    def clean_content(raw_content):
        content = re.sub(r'(\s|\n){3,}', '', raw_content)
        content = re.sub(r'</?[pi]>|<(?:article|iframe).+?>[\S\s]*?'
                         r'</(?:article|iframe)>|</?strong>|</?a.*?>|'
                         r'<img.+?>',
                         ' ',
                         content)
        content = re.sub(r'Читайте також:.+?\.', ' ', content)
        content = re.sub(r'\s{2,}|<p style=.+?>|\xa0|<em>.+?</em>|</?b>|'
                         r'/?span|<p dir=.+?>|<br>|<script.+?></script>|'
                         r'<style.+?</style>|< >|'
                         r'<div class=".*?embed.*?</div>|'
                         r'</?h.+?>|<div class="c-bar.*?</div>|'
                         r'<time.+?</time>|<svg.+?</svg>',
                         ' ', content)
        return content

    @staticmethod
    def get_title(response):
        title = response.css('div.c-post-meta > h1::text').\
            extract_first()
        if not title:
            title = response.css('div.c-post-meta > div > '
                                 'h1::text').extract_first()
        if not title:
            title = response.css('main > article > header > div '
                                 '> h1::text').extract_first()
        return title
