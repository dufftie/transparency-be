# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    id = scrapy.Field()
    article_id = scrapy.Field()
    media_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    date_time = scrapy.Field()
    authors = scrapy.Field()
    paywall = scrapy.Field()
    category = scrapy.Field()
    preview_url = scrapy.Field()
    body = scrapy.Field()
