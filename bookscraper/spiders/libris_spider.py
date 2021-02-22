import scrapy
from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


class LibrisSpider(scrapy.Spider):
    name = 'libris'

    def start_requests(self):
        url = 'https://www.libris.ro/?sn.l=30&sn.q=Sapiens'

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
        title_and_author = response.css("h1::text").get().split('-')
        book['provider'] = 'Libris'
        book['title'] = title_and_author[0].strip()
        book['author'] = title_and_author[1]
        book['publisher'] = response.xpath(
            "//p[starts-with(text(),'Editura')]/child::a/text()").get()
        book['numberOfPages'] = response.xpath("//p[starts-with(text(),'Nr.')]/text()").get().split(':')[1].strip()
        isbn = response.css("p#cod::text").get().split(':')[1].strip()
        book['isbn'] = isbn[3:len(isbn)].replace('-', '')
        cover_type = response.xpath("//p[starts-with(text(),'Editie')]/text()").get()
        if cover_type is not None:
            book['coverType'] = cover_type.split(':')[1].strip()
        book['imgUrl'] = response.css('img.imgProdus::attr(src)').get()
        book['offer'] = {
            'link': response.meta.get('link'),
            'provider': 'Libris',
            'price': response.css('p#price::text').get().split()[0],
            'hasStock': True if response.css('p#stoc::text').get().strip() != 'Indisponibil' else False
        }
        yield book
