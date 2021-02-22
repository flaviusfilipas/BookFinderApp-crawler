# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    imgUrl = scrapy.Field()
    isbn = scrapy.Field()
    publisher = scrapy.Field()
    language = scrapy.Field()
    coverType = scrapy.Field()
    numberOfPages = scrapy.Field()
    offer = scrapy.Field()
