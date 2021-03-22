import scrapy
from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


class BooksExpressSpider(scrapy.Spider):
    name = 'booksExpress'

    def start_requests(self):
        url = 'https://www.books-express.ro/search?q=Sapiens&p=1'

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
        link = response.meta.get('link')
        book = BookItem()
        book['title'] = response.css('h1 span::text').get()
        book['author'] = response.xpath('//h1/following-sibling::a/text()').get()
        publisher = response.xpath("//a[@itemprop = 'publisher']/text()").get()
        if publisher is not None:
            book['publisher'] = publisher
        else:
            book['publisher'] = response.xpath("//a[@itemprop = 'manufacturer']/text()").get()
        book['numberOfPages'] = response.xpath("//span[@itemprop = 'numberOfPages']/text()").get()
        isbn = link.split(',')
        if len(isbn) > 1:
            book['isbn'] = isbn[1]
        else:
            book['isbn'] = response.xpath("//span[@itemprop = 'isbn']/text()").get()
        book['imgUrl'] = response.css('figure.cover a img::attr(src)').get()
        book['coverType'] = response.xpath("//link[@itemprop='bookFormat']/@href").get().split("/")[3]
        book['offer'] = {
            'link': link,
            'provider': 'Books Express',
            'price': response.css('h4 span::attr(content)').get(),
            'hasStock': True if response.css('header h4::text').get != 'Carte indisponibilă temporar' else False,
            'transportationCost': 9.90
        }
        yield book
