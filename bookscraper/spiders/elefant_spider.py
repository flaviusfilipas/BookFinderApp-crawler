import scrapy
from selenium.common.exceptions import NoSuchElementException

from bookscraper.items import BookItem
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ElefantSpider(scrapy.Spider):
    name = 'elefant'

    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(executable_path=r"C:\Users\Flavius\Documents\bookscraper\chromedriver.exe",
                                       chrome_options=options)

    def start_requests(self):
        url = 'https://www.elefant.ro/search?SearchTerm=9789734648887'

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(2)
        try:
            self.driver.find_element_by_class_name("no-search-result-title")
        except NoSuchElementException:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "current-price")))
            html = self.driver.find_element_by_tag_name('html').get_attribute('innerHTML')
            res = response.replace(body=html)
            price = res.css("div.current-price::attr(data-price)").get()
            link = res.css("a.product-title::attr(href)").get()
            if price is None:
                price = response.xpath("concat(//div[@data-testing-id ='current-price']/text(),'',//div["
                                       "@data-testing-id= 'current-price']/child::sup/text())").get().replace(',', '.')\
                    .replace('lei', '').strip()
                link = self.driver.current_url
            book = BookItem()
            book['offer'] = {
                'link': link,
                'price': float(price),
                'provider': 'Elefant',
                'hasStock': True,
                'transportationCost': 17.98
            }
            yield book

    def scroll(self):
        init_position = 0
        max_scroll_height = self.driver.execute_script("return document.body.scrollHeight;")
        while init_position <= max_scroll_height:
            self.driver.execute_script(f"window.scrollTo({init_position},{init_position + 500});")
            init_position += 500
            time.sleep(0.1)

    def parse_book_info(self, response):
        book = BookItem()
        book['imgUrl'] = response.meta['img']
        book['title'] = response.css('h1.product-title::text').get()
        book['author'] = response.css('h2.product-brand a::text').get()
        publisher = response.xpath("//dt[starts-with(text(),'Editura')]/following-sibling::dd/text()").get()
        book['publisher'] = publisher.strip() if publisher is not None else None
        book['numberOfPages'] = response.xpath("//dt[starts-with(text(),'Numar')]/following-sibling::dd/text()").get()
        book['isbn'] = response.xpath("//dt[starts-with(text(),'ISBN')]/following-sibling::dd/text()").get().replace(
            '-', '')
        cover_type = response.xpath("//dt[starts-with(text(),'Tip')]/following-sibling::dd/text()").get()
        book['coverType'] = cover_type.strip() if cover_type is not None else None
        book['offer'] = {
            'link': response.meta['link'],
            'price': float(response.xpath("concat(//div[@data-testing-id ='current-price']/text(),'',//div["
                                          "@data-testing-id= 'current-price']/child::sup/text())").get().replace(',',
                                                                                                                 '.')
                           .replace('lei', '').strip()),
            'provider': 'Elefant',
            'hasStock': True,
            'transportationCost': 17.98
        }
        yield book
