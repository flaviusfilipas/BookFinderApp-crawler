import scrapy
from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


class BooksExpressSpider(scrapy.Spider):
    name = 'booksExpress'

    def start_requests(self):
        url = 'https://www.books-express.ro/search?q=9789734648887'

        yield SplashRequest(url=url, callback=self.parse, args={'images': 0, 'forbidden_content_types': 'text/css,'
                                                                                                        'font/* ',
                                                                'filters': 'easylist'})

    def parse(self, response):
        urls = response.css('article figure a::attr(href)').getall()
        base_url = 'https://www.books-express.ro'
        for url in urls:
            absolute_url = f'{base_url}{url}'
            yield SplashRequest(url=absolute_url,
                                callback=self.parse_book_info,
                                meta={'link': absolute_url},
                                args={'forbidden_content_types': 'text/css,font/* ',
                                      'filters': 'easylist'})

    def parse_book_info(self, response):
        link = response.url
        book = BookItem()
        stock = response.css('header h4::text').get()
        price = response.css('h4 span::attr(content)').get()
        if price is not None:
            book['offer'] = {
                'link': link,
                'provider': 'Books Express',
                'price': float(price) if price is not None else None,
                'hasStock': True if stock != 'Carte indisponibilă temporar' and stock != 'Disponibilitate incertă'
                else False,
                'transportationCost': 9.90
            }
            yield book
