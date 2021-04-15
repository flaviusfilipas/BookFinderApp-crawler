import scrapy
from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


def process_isbn(isbn):
    isbn_start_value = 0
    for char in isbn:
        if not char.isalpha():
            isbn_start_value = isbn.index(char)
            break
    return isbn[isbn_start_value:len(isbn)].replace('-', '')


class LibrisSpider(scrapy.Spider):
    name = 'libris'

    def start_requests(self):
        url = 'https://www.libris.ro/?sn.l=30&sn.q=9789734648887'

        yield SplashRequest(url=url, callback=self.parse, args={'forbidden_content_types': 'text/css,font/*',
                                                                'filters': 'easylist'})

    def parse(self, response):
        urls = response.css('div.container-produs-singur::attr(data-sna-url)').getall()
        base_url = 'https://www.libris.ro'
        for url in urls:
            full_url = f'{base_url}{url}'
            yield SplashRequest(url=full_url,
                                callback=self.parse_book_info,
                                meta={'link': full_url},
                                args={'wait': 0.5, 'forbidden_content_types': 'text/css,font/* ',
                                      'filters': 'easylist'})

    def parse_book_info(self, response):
        book = BookItem()
        book['offer'] = {
            'link': response.meta.get('link'),
            'provider': 'Libris',
            'price': float(response.css('p#price::text').get().split()[0]),
            'hasStock': True if response.css('p#stoc::text').get().strip() != 'Indisponibil' else False,
            'transportationCost': 9.90
            }
        yield book
