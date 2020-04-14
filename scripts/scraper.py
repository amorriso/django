import base_scraper
import urlparse
import os
import time
import re
import datetime
import pytz

from fetcher_statics import ScrapeStatics

import logging
import logging.config

from trader.marketdata import models as md_models

class ScrapeError(Exception):
    pass


class InfoScraper(base_scraper.BaseWebScraper):


    def __init__(self, driver, **kwargs):
        super(InfoScraper, self).__init__(driver = driver, **kwargs)

        self.base_url = 'https://www.barchart.com/'
        self.futures_url = self.base_url+'futures/quotes/'


    def _get_expiration(self, content):

        toolbar_list = ScrapeStatics.get_blocks(
                content,
                'div',
                {'class' : ['bc-datatable-toolbar', 'bc-options-toolbar']}
        )
        expiration_obj = toolbar_list[1]
        reg = re.search(
                r'expiration on ([0-9]+)/([0-9]+)/([0-9]+)', expiration_obj.text
        )

        year_str =  reg.group(3)
        if len(year_str) == 2:
            year_str = '20'+year_str
        year = int(year_str)

        expiration_date = datetime.date(
               year, int(reg.group(1)), int(reg.group(2))
        )

        return expiration_date


    def _get_option_dicts(self, content):

        table_content = ScrapeStatics.get_first_block(
                content,
                'div',
                {'class' : ['bc-table-scrollable']}
        )

        raw_option_list = ScrapeStatics.get_blocks(
                table_content,
                'tr',
        )

        for pos, line in enumerate(raw_option_list):
            if pos == 0:
                header = [e.text.strip() for e in ScrapeStatics.get_blocks(line, 'span')]
                option_dict = dict([(k, []) for k in header])
            else:
                vals = [e.text.strip() for e in ScrapeStatics.get_blocks(line, 'span')][::3]
                for k, v in zip(header, vals):
                    option_dict[k].append(v)

        # clean up
        _len = min([len(el) for el in option_dict.values()])
        for k, v in option_dict.iteritems():
            option_dict[k] = v[:_len]

        calls = []
        puts = []

        for i in xrange(_len):
            option = {}
            for h in header:
                option[h] = option_dict[h][i]
            if option['Strike'].endswith('C'):
                option['Type'] = 'C'
            else:
                option['Type'] = 'P'

            option['Strike'] = float(option['Strike'][:-1])

            try:
                option['Last'] = float(option['Last'][:-1])
            except:
                option['Last'] = -99

            try:
                option['Ask'] = float(option['Ask'][:-1])
            except:
                option['Ask'] = option['Last']

            try:
                option['Bid'] = float(option['Bid'][:-1])
            except:
                option['Bid'] = option['Last']

            try:
                option['High'] = float(option['High'][:-1])
            except:
                option['High'] = option['Last']

            try:
                option['Low'] = float(option['Low'][:-1])
            except:
                option['Low'] = option['Last']

            # TODO ask Gareth. unch. WTF?
            try:
                option['Change'] = float(option['Change'])
            except ValueError:
                option['Change'] = 0.0

            option['Premium'] = float(option['Premium'].replace(',',''))
            try:
                option['Volume'] = int(option['Volume'].replace(',',''))
            except:
                option['Volume'] = 0

            if option['Type'] == 'C':
                calls.append(option)
            else:
                puts.append(option)

        return {'calls' : calls, 'puts' : puts}


    def get_future_price(self, ticker):

        url = self.futures_url+ticker+'/overview'

        content = self.get_url_as_bs(url, wait_sequence=None)
        price_obj = ScrapeStatics.get_first_block(
                content,
                'span',
                {'class' : ['last-change']}
        )

        price_match = re.search(r'[0-9]+.[0-9]+', price_obj.text)

        if price_match:
            return float(price_match.group(0))
        else:
            raise SrapeError("Failed to regex find price")


    def get_options_prices(self, ticker):

        url = self.futures_url+ticker+'/options?moneyness=allRows'
        content = self.get_url_as_bs(url, wait_sequence=None)

        expiration = self._get_expiration(content)

        option_dict = self._get_option_dicts(content)

        return {'expiration' : expiration, 'option_dict' : option_dict}


def easyscreen_mnemonic(future, option_dict, expiry):
    mnemonic = '___:'+future.barchart_id
    mnemonic += expiry.strftime(" %b %-y ")
    mnemonic += str(format(option_dict['Strike'], '.2f')).replace('.', '')
    if option_dict['Type'] == 'C':
        mnemonic += 'c 0'
    else:
        mnemonic += 'p 0'
    return mnemonic


def fetch(ticker, driver, *args, **kwargs):

    future = md_models.Future.objects.get(barchart_id=ticker)
    option_def = md_models.OptionDefinition.objects.get(future=future)
    db_options = md_models.OptionContract.objects.filter(
            optiondefinition=option_def
    )

    # --------------------------------------------------------------------------
#    import cPickle as pickle
#
#    option_expiry = datetime.date(2020, 4, 27)
#    with open('options.pickle') as fh:
#        call_options, put_options = pickle.load(fh)
#
#        for option_list in (call_options, put_options):
#            for option in option_list:
#                option['Mnemonic'] = easyscreen_mnemonic(future, option, option_expiry)
#    future_price = 31.48
    # --------------------------------------------------------------------------
    try:
        scraper = InfoScraper(driver=driver)
        future_price = scraper.get_future_price(ticker)
        option_dict = scraper.get_options_prices(ticker)
    finally:
        scraper.kill_driver()
    option_expiry = option_dict['expiration']
    call_options = option_dict['option_dict']['calls']
    put_options = option_dict['option_dict']['puts']

    for option in call_options:
        option['Moneyness'] = option['Strike'] - future_price
        option['Mnemonic'] = easyscreen_mnemonic(future, option, option_expiry)

    for option in put_options:
        option['Moneyness'] = future_price - option['Strike']
        option['Mnemonic'] = easyscreen_mnemonic(future, option, option_expiry)
    

    call_options = sorted([o for o in call_options if o['Moneyness'] >= 0.0], key=lambda o: o['Moneyness'])
    put_options = sorted([o for o in put_options if o['Moneyness'] >= 0.0], key=lambda o: o['Moneyness'])
    # --------------------------------------------------------------------------

    future.bid = future_price
    future.ask = future_price
    future.last_trade_value = future_price
    future.last_updated = datetime.datetime.now()
    future.save()

    n = option_def.number_of_OTM_options

    option_dict = dict([(option['Mnemonic'], option) for option in call_options[:n/2]])
    option_dict.update(dict([(option['Mnemonic'], option) for option in put_options[:n/2]]))

    easy_screen_mnemonics_keep = set()

    for option in option_dict.itervalues():
        try:
            db_option = md_models.OptionContract.objects.get(easy_screen_mnemonic=option['Mnemonic'])
            db_option.bid = option['Bid']
            db_option.ask = option['Ask']
            db_option.value = (option['Bid'] + option['Ask'])/2.
            db_option.last_trade_volume = option['Volume']
            db_option.last_updated = datetime.datetime.now()
            db_option.save()

        except:
            db_option = md_models.OptionContract(
                    optiondefinition=option_def,
                    easy_screen_mnemonic=option['Mnemonic'],
                    strike=option['Strike'],
                    bid=option['Bid'],
                    ask=option['Ask'],
                    value=(option['Bid'] + option['Ask'])/2.,
                    last_trade_volume = option['Volume'],
                    last_updated = datetime.datetime.now(),
            )
            db_option.save()

        easy_screen_mnemonics_keep.add(db_option.easy_screen_mnemonic)


    db_options = md_models.OptionContract.objects.filter(optiondefinition=option_def)
    
    for option in db_options:
        if not option.easy_screen_mnemonic in easy_screen_mnemonics_keep:
            option.delete()


if __name__ == '__main__':

    """Remember to: export DJANGO_SETTINGS_MODULE=trader.trader.settings
    """

    fetch('$VIX', 30)

#    obj = InfoScraper(driver='chrome')
#    #price = obj.get_future_price('CBM20')
#    options_dict = obj.get_options_prices('CBM20')
#    pprint(options_dict)
#    obj.kill_driver()
