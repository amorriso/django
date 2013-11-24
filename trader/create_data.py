from marketdata.models import *
from django.utils import timezone
import datetime

futures = Future.objects.all()
if len(futures) > 0:
    futures.delete()

option_definitions = OptionDefinition.objects.all()
if len(option_definitions) > 0:
    option_definitions.delete()

option_contracts = OptionContract.objects.all()
if len(option_contracts) > 0:
    option_contracts.delete()

future = Future(name = 'BUNDMAR14', bloomberg_id = 'BLOOMBERG_BUNDMAR14', easyscreen_id = 'EBF:FGBL Mar 13',
        bid = 140.0, bid_volume = 2, ask = 140.0, ask_volume = 2, value = 140.0, last_trade_value = 140.0, 
        last_updated = datetime.datetime(2013, 11, 01, 0, 0, 0), last_trade_volume = 2,
        month_tag = 'MAR14', expiry_date = datetime.datetime(2014,03,21,0,0,0))

future2 = Future(name = 'BUNDDEC13', bloomberg_id = 'BLOOMBERG_BUNDDEC13', easyscreen_id = 'EBF:FGBL Dec 13',
        bid = 140.0, bid_volume = 2, ask = 140.0, ask_volume = 2, value = 160.0, last_trade_value = 140.0, 
        last_updated = datetime.datetime(2013, 11, 01, 0, 0, 0), last_trade_volume = 2, 
        month_tag = 'DEC13', expiry_date = datetime.datetime(2014,06,21,0,0,0))

future3 = Future(name = 'BOBLMAR14', bloomberg_id = 'BLOOMBERG_BOBLMAR14', easyscreen_id = 'EBF:FGBM Mar 13',
        bid = 140.0, bid_volume = 2, ask = 140.0, ask_volume = 2, value = 180.0, last_trade_value = 140.0, 
        last_updated = datetime.datetime(2013, 11, 01, 0, 0, 0), last_trade_volume = 2,
        month_tag = 'MAR14', expiry_date = datetime.datetime(2014,06,21,0,0,0))

future.save()
future2.save()
future3.save()

option_defs = OptionDefinition.objects.all()
if len(option_defs) > 0:
    option_defs.delete()

future = Future.objects.get(pk=1)
future2 = Future.objects.get(pk=2)
future3 = Future.objects.get(pk=3)

###############################################################################
optiondefs = [
        ('BUND_OPT_JAN', 'BLOOM_BUND_OPT_JAN', 'JAN14', datetime.date(2014,1,21), 'EBO:OGBL Jan 14', 0.01), 
        ('BUND_OPT_FEB', 'BLOOM_BUND_OPT_FEB', 'FEB14', datetime.date(2014,2,21), 'EBO:OGBL Feb 14', 0.01),
        ('BUND_OPT_MAR', 'BLOOM_BUND_OPT_MAR', 'MAR14', datetime.date(2014,3,21), 'EBO:OGBL Mar 14', 0.01)
             ]

for optiondef in optiondefs:
    future.optiondefinition_set.create(name = optiondef[0], bloomberg_prefix = optiondef[1], month_tag = optiondef[2], expiry_date = optiondef[3], strike_interval = 0.5, easyscreen_prefix = optiondef[4], price_movement = optiondef[5] )
###############################################################################
optiondefs = [
        ('BUND_OPT_DEC', 'BLOOM_BUND_OPT_DEC', 'DEC13', datetime.date(2013,12,21), 'EBO:OGBL Dec 13', 0.01), 
             ]

for optiondef in optiondefs:
    future2.optiondefinition_set.create(name = optiondef[0], bloomberg_prefix = optiondef[1], month_tag = optiondef[2], expiry_date = optiondef[3], strike_interval = 0.5, easyscreen_prefix = optiondef[4], price_movement = optiondef[5] )
###############################################################################
optiondefs = [
        ('BOBL_OPT_JAN', 'BLOOM_BOBL_OPT_JAN', 'JAN14', datetime.date(2014,1,21), 'EBO:OGBM Jan 14', 0.01), 
        ('BOBL_OPT_FEB', 'BLOOM_BOBL_OPT_FEB', 'FEB14', datetime.date(2014,2,21), 'EBO:OGBM Feb 14', 0.01),
        ('BOBL_OPT_MAR', 'BLOOM_BOBL_OPT_MAR', 'MAR14', datetime.date(2014,3,21), 'EBO:OGBM Mar 14', 0.01)
             ]

for optiondef in optiondefs:
    future3.optiondefinition_set.create(name = optiondef[0], bloomberg_prefix = optiondef[1], month_tag = optiondef[2], expiry_date = optiondef[3], strike_interval = 0.5, easyscreen_prefix = optiondef[4], price_movement = optiondef[5] )
###############################################################################
