import scrapy
from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


class CarturestiSpider(scrapy.Spider):
    name = "carturesti"
    # only for testing purposes. url will be passed through scrapyrt as a param
    def start_requests(self):
        url = f'https://carturesti.ro/product/search/Sapiens?page=1&id_product_type=26'
        yield SplashRequest(url=url, callback=self.parse, args={'forbidden_content_types': 'text/css,font/*',
                                                                'filters': 'easylist'})

    def parse(self, response):
        books = response.css('div.cartu-grid-tile')
        base_url = 'https://carturesti.ro'
        for b in books:
            book = BookItem()
            book['title'] = b.css('h5::text').get()
            book['author'] = b.css('div.subtitlu-produs a::text').get()
            book['imgUrl'] = b.css('div.productImageContainer img::attr(src)').get()
            book['price'] = b.css('span.suma::attr(content)').get()
            book['hasStock'] = True if b.css('div.productStock span::text').get() != 'Indisponibil' else False
            book['provider'] = 'Carturesti'
            individual_book_url = b.css('a::attr(href)').get()
            book_link = f'{base_url}{individual_book_url}'
            book['link'] = book_link
            yield SplashRequest(url=book_link,
                                callback=self.parse_book_info,
                                args={'wait': 0.5, 'images': 0, 'forbidden_content_types': 'text/css,font/* ',
                                      'filters': 'easylist'},
                                meta={'book': book})

    def parse_book_info(self, response):
        book = response.meta.get('book')
        book['language'] = response.xpath("//span[contains(text(),'Limba: ')]/following-sibling::div/text()").get()
        book['publisher'] = response.xpath("//span[contains(text(),'Editura: ')]/following-sibling::div/span/a/text()").get()
        book['numberOfPages'] = response.xpath("//span[starts-with(text(),'Nr')]/following-sibling::div/text()").get()
        book['isbn'] = response.xpath("//span[starts-with(text(),'ISBN')]/following-sibling::div/text()").get()
        book['coverType'] = response.xpath("//span[starts-with(text(),'Tip')]/following-sibling::div/text()").get()

        yield book
