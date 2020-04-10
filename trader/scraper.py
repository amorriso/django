import base_scraper
import urlparse
import os
import time
import re
import datetime
import logging
import logging.config
import bs4 as bs

from selenium.webdriver.support.ui import WebDriverWait


class InfoScraper(base_scraper.BaseWebScraper):


    def __init__(self, driver = 'phantomjs',
            **kwargs
        ):
        super(InfoScraper, self).__init__(driver = driver, **kwargs)

    def get_future_price(self, url):

        content = self.get_url_as_bs(url)
        import pdb;pdb.set_trace()
        




if __name__ == '__main__':
    
    URL = 'https://www.betfair.com/exchange/horse-racing'
    timezone = 'Europe/London'#

    obj = InfoScraper(driver='chrome')
    obj.get_future_price('https://www.barchart.com/futures/quotes/CBM20/overview')
