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
        title_and_author = response.css("h1::text").get()
        if title_and_author is not None:
            title_and_author = title_and_author.split('-')
            if len(title_and_author) > 1:
                book['title'] = title_and_author[0].strip()
                book['author'] = title_and_author[1]
            else:
                book['title'] = title_and_author[0].strip()
                book['author'] = response.xpath("//p[contains(text(),'Autor')]/child::a/text()").get()
            publisher = response.xpath(
                "//p[starts-with(text(),'Editura')]/child::a/text()").get()
            book['publisher'] = publisher.strip() if publisher is not None else None
            number_of_pages = response.xpath("//p[starts-with(text(),'Nr.')]/text()").get()
            book['numberOfPages'] = number_of_pages.split(':')[1].strip() if number_of_pages is not None else None
            book['imgUrl'] = response.css('img.imgProdus::attr(src)').get()
            book['offer'] = {
                'link': response.meta.get('link'),
                'provider': 'Libris',
                'price': float(response.css('p#price::text').get().split()[0]),
                'hasStock': True if response.css('p#stoc::text').get().strip() != 'Indisponibil' else False,
                'transportationCost': 9.90
            }
            cover_type = response.xpath("//p[starts-with(text(),'Editie')]/text()").get()
            if cover_type is not None:
                book['coverType'] = cover_type.split(':')[1].strip()
                isbn = response.css("p#cod::text").get().split(':')[1].strip()
                book['isbn'] = process_isbn(isbn)
            else:
                cover_types = response.xpath("//p[starts-with(text(),'Formate')]/text()").get()
                if cover_types is not None:
                    cover_types = cover_types.split(':')[1].split(',')
                    if len(cover_types) > 1:
                        isbn_types = response.xpath("//p[contains(text(),'ISBN')]/text()").getall()
                        for index, cover_type in enumerate(cover_types):
                            book['coverType'] = cover_type.strip()
                            book['isbn'] = isbn_types[index].split(':')[1].strip().replace('-', '')
                            yield book
                        return
                    else:
                        book['coverType'] = cover_types[0].strip()
                        isbn = response.css("p#cod::text").get().split(':')[1].strip()
                        book['isbn'] = process_isbn(isbn)
            yield book
