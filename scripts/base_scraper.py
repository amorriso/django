import abc
import ast
import pytz
import bs4 as bs
import os
import requests
import urllib2
import urllib
import json
import sys
import gc
from fetcher_statics import ScrapeStatics
import selenium.webdriver as webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display

import logging

import pdb

DRIVER = None
DRIVER_REQUEST_COUNT = 0

class BaseWebScraper(object):


    def __init__(self, test = None, driver = 'chrome', **kwargs):

        self.display = None
        self.driver_string = driver
        if not test:
            if type(driver) == type(''):
                self.start_driver(driver, kwargs)

            else:
                m = "Using LIVE driver object!"
                logging.info(m)
                self.driver = driver

        if 'timeout' in kwargs:
            if type(kwargs['timeout']) != type(1):
                m = "timeout must be specified as an integer. You've supplied: "+\
                        str(kwargs['timeout'])
                logging.error(m)
                raise ValueError(m)
            self.driver.set_page_load_timeout(kwargs['timeout'])

        else:
            self.driver.set_page_load_timeout(30)

        self.test = test


    @staticmethod
    def jsonify(dic):

        '''
        Recursively JSON'ify a nested dictionary. Returns a new object!

        '''

        if not isinstance(dic, dict):
            return dic
        return {str(k): BaseWebScraper.jsonify(v) for k, v in dic.items()}


    def start_driver(self, driver, kwargs):

        global DRIVER
        global DRIVER_REQUEST_COUNT 

        if driver == 'firefox':

            self.driver = webdriver.Firefox()

        elif driver == 'firefox-nodisplay':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            #profile = webdriver.FirefoxProfile()
            ##profile.set_preference("general.useragent.override",
            ##        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:32.0)"+\
            ##                    " Gecko/20100101 Firefox/32.0"
            ##    )
            #self.driver = webdriver.Firefox(profile)
            self.driver = webdriver.Firefox()
            self.hold_display_open = True


        elif driver == 'chrome':
            self.driver = webdriver.Chrome()


        elif driver == 'chrome-maximize_window':
            self.driver = webdriver.Chrome()
            self.driver.maximize_window()


        elif driver == 'chrome-nodisplay-fake-windows':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            opts = webdriver.ChromeOptions()
            opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36")
            self.driver = webdriver.Chrome(chrome_options = opts)
            self.hold_display_open = True


        elif driver == 'chrome-nodisplay-fake-windows-cache':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            opts = webdriver.ChromeOptions()
            opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36")
            if DRIVER is None:
                self.driver = webdriver.Chrome(chrome_options = opts)
                DRIVER = self.driver
                DRIVER_REQUEST_COUNT = 0
            else:
                self.driver = DRIVER
                self.driver.delete_all_cookies()
                DRIVER_REQUEST_COUNT += 1
            self.hold_display_open = True



        elif driver == 'chrome-nodisplay':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            self.driver = webdriver.Chrome()
            self.hold_display_open = True


        elif driver == 'chrome-nodisplay-maximize_window':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            self.driver = webdriver.Chrome()
            self.driver.maximize_window()
            self.hold_display_open = True




        elif driver == 'chrome-nodisplay-cache':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            if DRIVER is None:
                self.driver = webdriver.Chrome()
                DRIVER = self.driver
                DRIVER_REQUEST_COUNT = 0
            else:
                self.driver = DRIVER
                self.driver.delete_all_cookies()
                DRIVER_REQUEST_COUNT += 1
            self.hold_display_open = True



        elif driver == 'chrome-nodisplay-startdisplay':

            self.display = Display(visible = 0, size=(2560,1440))
            self.display.start()

            self.driver = webdriver.Chrome()
            self.hold_display_open = False

        elif driver == 'chrome-proxy':

            if not 'proxy' in kwargs:
                m = "no proxy string specified as kwarg!"
                raise ValueError(m)

            options = webdriver.ChromeOptions()
            options.add_argument("--proxy-server=" + kwargs['proxy'])
            self.driver = webdriver.Chrome(chrome_options = options)


        elif driver == 'chrome-proxy-fake-windows':

            if not 'proxy' in kwargs:
                m = "no proxy string specified as kwarg!"
                raise ValueError(m)

            options = webdriver.ChromeOptions()
            options.add_argument("--proxy-server=" + kwargs['proxy'])
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36")
            self.driver = webdriver.Chrome(chrome_options = options)


        elif driver == 'chrome-nodisplay-proxy':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            if not 'proxy' in kwargs:
                m = "no proxy string specified as kwarg!"
                raise ValueError(m)

            options = webdriver.ChromeOptions()
            options.add_argument("--proxy-server=" + kwargs['proxy'])
            self.driver = webdriver.Chrome(chrome_options = options)
            self.hold_display_open = True


        elif driver == 'chrome-nodisplay-proxy-fake-windows':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            if not 'proxy' in kwargs:
                m = "no proxy string specified as kwarg!"
                raise ValueError(m)

            options = webdriver.ChromeOptions()
            options.add_argument("--proxy-server=" + kwargs['proxy'])
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36")
            self.driver = webdriver.Chrome(chrome_options = options)
            self.hold_display_open = True


        elif driver == 'chrome-nodisplay-proxy-fake-windows-cache':

            '''
            to install:

                pip install pyvirtualdisplay

                sudo apt-get install xvfb x11-xkb-utils xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic x11-apps
            '''

            if not 'proxy' in kwargs:
                m = "no proxy string specified as kwarg!"
                raise ValueError(m)

            options = webdriver.ChromeOptions()
            options.add_argument("--proxy-server=" + kwargs['proxy'])
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36")
            if DRIVER is None:
                self.driver = webdriver.Chrome(chrome_options = options)
                DRIVER = self.driver
                DRIVER_REQUEST_COUNT = 0
            else:
                self.driver = DRIVER
                self.driver.delete_all_cookies()
                DRIVER_REQUEST_COUNT += 1
            self.hold_display_open = True



        elif driver == 'chrome-nodisplay-startdisplay-proxy':

            if not 'proxy' in kwargs:
                m = "no proxy string specified as kwarg!"
                raise ValueError(m)

            self.display = Display(visible = 0, size=(2560,1440))
            self.display.start()

            options = webdriver.ChromeOptions()
            options.add_argument("--proxy-server=" + kwargs['proxy'])
            self.driver = webdriver.Chrome(chrome_options = options)
            self.hold_display_open = False

        elif driver == 'firefox-nodisplay-startdisplay':

            self.display = Display(visible = 0, size=(2560,1440))
            self.display.start()

            profile = webdriver.FirefoxProfile()
            self.driver = webdriver.Firefox(profile)
            self.hold_display_open = False

        elif driver == 'firefox-nodisplay-maximize_window':

            profile = webdriver.FirefoxProfile()
            self.driver = webdriver.Firefox(profile)
            self.driver.maximize_window()
            self.hold_display_open = True



        else:
            m = "Unknown webdriver! " + driver
            logging.error(m)
            raise ValueError(m)


    def kill_driver(self, cache_kill = True):

        global DRIVER
        global DRIVER_REQUEST_COUNT 

        do_kill = False
        if DRIVER is None:
            do_kill = True
        else:
            if cache_kill:
                do_kill = True

        # HACK HACK HACK HACK - we need to bring this inline with the celery setting
        # CELERYD_MAX_TASKS_PER_CHILD!
        if DRIVER_REQUEST_COUNT >= 25:
            do_kill = True
            DRIVER_REQUEST_COUNT = 0

        if do_kill:
            try:
                DRIVER.quit()
                DRIVER = None
            except:
                pass
                
            try:
                self.driver.quit()
            except:
                pass

            if not self.display is None:
                self.display.stop()
            gc.collect()
            logging.info("kill_driver() hitting gc.collect()!")
            #sys.exit()

    
    # ISSUES WITH KWARGS! BECAREFUL USING THIS
    #def restart_driver(self):
    #    self.kill_driver()
    #    self.start_driver(self.driver_string)


    def navigate(self, url, wait_sequence = []):

        return ScrapeStatics.navigate(
                self.driver,
                url,
                wait_sequence = wait_sequence,
                test = self.test
            )

    def refresh(self, wait_sequence = []):

        return ScrapeStatics.refresh(
                self.driver,
                wait_sequence = wait_sequence,
                test = self.test
            )



    def get_url_as_bs(self, url, wait_sequence = [], test = None, fail_str = None):

        return ScrapeStatics.get_url_as_bs(
                self.driver,
                url,
                wait_sequence = wait_sequence,
                test = test,
                fail_str = fail_str,
            )


    def get_url_as_string(self, url, wait_sequence = [], test = None, fail_str = None):

        return ScrapeStatics.get_url_as_string(
                self.driver,
                url,
                wait_sequence = wait_sequence,
                test = test,
                fail_str = fail_str,
            )


class BaseOddsScraper(BaseWebScraper):

    __metaclass__ = abc.ABCMeta

    def __init__(self, rawrace_guid, timezone, 
            venue_str, scheduled_jump_str,
            test = None,
            driver = 'phantomjs',
            **kwargs):

        super(BaseOddsScraper, self).__init__(test, driver, **kwargs)

        # uniquely identify race (rawfeed app.)
        self.rawrace_guid = rawrace_guid
        # we need to know timezone to map to UTC
        if not timezone in pytz.all_timezones_set:
            if isinstance(timezone, int):
                self.timezone = pytz.FixedOffset(timezone)
            else:
                raise pytz.UnknownTimeZoneError(timezone)
        else:
            self.timezone = pytz.timezone(timezone)

        self.venue_str = venue_str
        self.scheduled_jump_str = scheduled_jump_str
        self.source = None

        allowed_kwargs = set([
                'win_url', 'place_url', 
                'place2_url', 'place3_url', 
                'exacta_url', 'quinella_url',
                'swinger_url', 'POST_url',
                'timeout', 'proxy',
            ])

        self.urls = {}

        for kw in kwargs:
            if not kw in allowed_kwargs:
                m = "Unknown kwarg: " + str(kw) + ", Only allowed kwargs:\n" + \
                        str(allowed_kwargs)
                logging.error(m)
                raise ValueError(m)

            if kw.endswith('_url'):
                self.urls[kw] = kwargs[kw]

        # we can store the last odds we fetched. Current thinking is that
        # true feeds die after they fetch as send off odds where as feeds 
        # associated with pools don't die. These scrape the pool info at
        # a high frequency, when the odds change, the modified odds get sent
        # to some websever/queue for further processing.
        self.odds = {}
        self.previous_odds = {}
        self.probs = {}


    def POST(self, key, timeout = 10):

        valid_keys = ['win', 'place', 'place2', 'place3']
        if not key in valid_keys:
            m = "Unknown data type to post. key = "+str(key)
            logging.error(m)
            raise ValueError(m)

        m = "No POST_url set!"

        if not 'POST_url' in self.urls:
            logging.error(m)
            raise RuntimeError(m)

        if self.urls['POST_url'] is None:
            logging.error(m)
            raise RuntimeError(m)


        numeric_info = {'Odds' : self.odds[key], 'Probs' : self.probs[key]}
        info = {'Source' : self.source, 'Key' : key, 'Data' : numeric_info}
        json_info = json.dumps(self.jsonify(info))

        # NOTE! I should be able to use requests to post data. but can't get
        # this working
        #response = requests.post(self.urls['POST_url'], data = json_info)
        request = urllib2.Request(self.urls['POST_url'], data = json_info)
        response = urllib2.urlopen( request, timeout = timeout )

        if response.read() != 'True':
            m = "Failed to POST data for event. Venue: "+ self.venue_str+ ", "+\
                    "Scheduled jump: " + self.scheduled_jump_str
            logging.error(m)
            raise RuntimeError(m)

        # Example GET request below -> this doesn't go here. comment example only
        #payload = {
        #        'RawRaceGUID' : '81534ceb6eb95ae80323602c82c61cc270c97e66',
        #        'BetType' : 'win',
        #        'DataType' : 'probs',
        #        'SafeOdds' : 'True', # or False
        #    }
        #response = requests.get(self.urls['POST_url'], params = payload)
        #data = ast.literal_eval(response.content)

        return None
        


    @abc.abstractmethod
    def calculate_win_probs(self):
        pass


    @abc.abstractmethod
    def calculate_place_probs(self):
        pass


    @abc.abstractmethod
    def calculate_exacta_probs(self):
        pass


    @abc.abstractmethod
    def calculate_quinella_probs(self):
        pass


    @abc.abstractmethod
    def calculate_swinger_probs(self):
        pass


    @abc.abstractmethod
    def get_win_odds(self):
        pass


    @abc.abstractmethod
    def get_place_odds(self):
        pass


    @abc.abstractmethod
    def get_exacta_odds(self):
        pass


    @abc.abstractmethod
    def get_quinella_odds(self):
        pass


    @abc.abstractmethod
    def get_swinger_odds(self):
        pass


class BaseInfoScraper(BaseWebScraper):

    __metaclass__ = abc.ABCMeta

    def __init__(self, BETTING_INFO_URL, BASE_URL,
                    racetype_id, feed_id, timezone,
                 test = None, driver = 'phantomjs', **kwargs):

        super(BaseInfoScraper, self).__init__(test, driver, **kwargs)

        self.main_page_url = BETTING_INFO_URL
        self.base_url = BASE_URL
        self.raw_win_info = None
        self.raw_place_info = None
        # so we know what type of race this is. Horse, dog etc
        self.racetype_id = racetype_id
        # associate with feed (feed app.)
        self.feed_id = feed_id
        if not timezone in pytz.all_timezones_set:
            if isinstance(timezone, int):
                self.timezone = pytz.FixedOffset(timezone)
            else:
                raise pytz.UnknownTimeZoneError(timezone)
        else:
            self.timezone = pytz.timezone(timezone)


    @abc.abstractmethod
    def scrape_win(self, test = None, **kwargs):

        pass


    @abc.abstractmethod
    def scrape_place(self, test = None, **kwargs):

        pass

    @abc.abstractmethod
    def db_add_win(self, raw_info = None, **kwargs):

        pass


    @abc.abstractmethod
    def db_add_place(self, raw_info = None, **kwargs):

        pass
