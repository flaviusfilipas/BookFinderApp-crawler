import scrapy
from bookscraper.items import BookItem
from scrapy_splash import SplashRequest
import unicodedata


def process_author_name(author):
    return ' '.join(name.capitalize() for name in author.lower().split(' '))


class DivertaSpider(scrapy.Spider):
    name = 'diverta'

    def start_requests(self):
        url = 'https://www.dol.ro/?sn.q=9789734648887'

        yield SplashRequest(url=url, callback=self.parse, args={'wait': 1, 'images': 0, 'forbidden_content_types': 'text/css,'
                                                                                                        'font/* ',
                                                                'filters': 'easylist'})

    def parse(self, response):
        urls = response.css('h3.product-name a::attr(href)').getall()
        for url in urls:
            if url.find('carti') != -1:
                yield SplashRequest(url=url,
                                    callback=self.parse_book_info,
                                    meta={'link': url},
                                    args={'wait': 0.5, 'forbidden_content_types': 'text/css,font/* ',
                                          'filters': 'easylist'})

    def parse_book_info(self, response):
        link = response.meta.get('link')
        book = BookItem()
        book['title'] = response.css('h1::text').get().strip()
        author = response.css('h1 div::text').get().strip()
        if author is None or author == '':
            author = response.xpath("//td[contains(text(),'Autor')]/following-sibling::td/text()").get().strip()
            author = unicodedata.normalize("NFKD", author)
            author = process_author_name(author)
        else:
            author = unicodedata.normalize('NFKD', author)
            author = process_author_name(author)
        book['author'] = author
        book['publisher'] = response.xpath("//b[starts-with(text(),'Editura')]/parent::span/text()").get().strip()
        number_of_pages = response.xpath("//td[contains(text(),'pagini')]/following-sibling::td/text()").get() \
            .strip()
        book['numberOfPages'] = number_of_pages if number_of_pages != 'N/A' else None
        book['coverType'] = response.xpath("//td[contains(text(),'Tip')]/following-sibling::td/text()").get().strip()
        isbn = response.xpath("//td[starts-with(text(),'ISBN')]/following-sibling::td/text()").get()
        if isbn is not None:
            book['isbn'] = isbn.strip().replace('-', '')
        else:
            book['isbn'] = response.xpath("//td[starts-with(text(),'Cod')]/following-sibling::td/text()").get().strip() \
                .replace('-', '')
        book['imgUrl'] = response.css('img.product-picture-big::attr(src)').get()
        book['offer'] = {
            'link': link,
            'provider': 'Diverta',
            'price': float(response.xpath("concat(//div[@id='product_price']/text(),'.',//div["
                                          "@id='product_price']/child::sup/text())").get()),
            'hasStock': True,
            'transportationCost': 15.00
        }
        yield book
