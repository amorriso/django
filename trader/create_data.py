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
        last_trade_time = datetime.datetime(2014, 06, 01, 0, 0, 0),
        month_tag = 'MAR14', expiry_date = datetime.datetime(2014,03,01,0,0,0))

future2 = Future(name = 'BUNDJUN14', bloomberg_id = 'BLOOMBERG_BUNDJUN14', easyscreen_id = 'EBF:FGBL Jun 13',
        bid = 140.0, bid_volume = 2, ask = 140.0, ask_volume = 2, value = 160.0, last_trade_value = 140.0, 
        last_trade_time = datetime.datetime(2014, 06, 01, 0, 0, 0), 
        month_tag = 'JUN14', expiry_date = datetime.datetime(2014,06,01,0,0,0))

future3 = Future(name = 'BUBBLEJUN14', bloomberg_id = 'BLOOMBERG_BUBBLEJUN14', easyscreen_id = 'EBF:FGBL Dec 13',
        bid = 140.0, bid_volume = 2, ask = 140.0, ask_volume = 2, value = 180.0, last_trade_value = 140.0, 
        last_trade_time = datetime.datetime(2014, 06, 01, 0, 0, 0),
        month_tag = 'JUN14', expiry_date = datetime.datetime(2014,06,01,0,0,0))

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
        ('BUND_OPT_JAN', 'BLOOM_BUND_OPT_JAN', 'JAN14', datetime.date(2014,1,1)), 
        ('BUND_OPT_FEB', 'BLOOM_BUND_OPT_FEB', 'FEB14', datetime.date(2014,2,1)),
        ('BUND_OPT_MAR', 'BLOOM_BUND_OPT_MAR', 'MAR14', datetime.date(2014,3,1))
             ]

for optiondef in optiondefs:
    future.optiondefinition_set.create(name = optiondef[0], bloomberg_prefix = optiondef[1], month_tag = optiondef[2], expiry_date = optiondef[3], strike_interval = 0.5)
###############################################################################
optiondefs = [
        ('BUND_OPT_APR', 'BLOOM_BUND_OPT_APR', 'APR14', datetime.date(2014,1,1)), 
        ('BUND_OPT_MAY', 'BLOOM_BUND_OPT_MAY', 'MAY14', datetime.date(2014,2,1)),
        ('BUND_OPT_JUN', 'BLOOM_BUND_OPT_JUN', 'JUN14', datetime.date(2014,3,1))
             ]

for optiondef in optiondefs:
    future2.optiondefinition_set.create(name = optiondef[0], bloomberg_prefix = optiondef[1], month_tag = optiondef[2], expiry_date = optiondef[3], strike_interval = 0.5)
###############################################################################
optiondefs = [
        ('BUBBLE_OPT_APR', 'BLOOM_BUBBLE_OPT_APR', 'APR14', datetime.date(2014,1,1)), 
        ('BUBBLE_OPT_MAY', 'BLOOM_BUBBLE_OPT_MAY', 'MAY14', datetime.date(2014,2,1)),
        ('BUBBLE_OPT_JUN', 'BLOOM_BUBBLE_OPT_JUN', 'JUN14', datetime.date(2014,3,1))
             ]

for optiondef in optiondefs:
    future3.optiondefinition_set.create(name = optiondef[0], bloomberg_prefix = optiondef[1], month_tag = optiondef[2], expiry_date = optiondef[3], strike_interval = 0.5)
###############################################################################
