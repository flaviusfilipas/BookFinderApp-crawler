# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    imgUrl = scrapy.Field()
    price = scrapy.Field()
    isbn = scrapy.Field()
    hasStock = scrapy.Field()
    publisher = scrapy.Field()
    language = scrapy.Field()
    coverType = scrapy.Field()
    provider = scrapy.Field()
    numberOfPages = scrapy.Field()
    link = scrapy.Field()
