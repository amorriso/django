# Create your views here.
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import helper_functions as hf
import scipy
import pdb

from marketdata.models import *

def index(request):
    futures = Future.objects.all() 
    futures = [el for el in futures 
            if el.expiry_date > datetime.datetime.today()]

    options = OptionDefinition.objects.all() 
    options =  [el for el in options 
            if el.expiry_date > datetime.datetime.today()]

    futuredict = {}
    for future in futures:
        futuredict[future] = [o for o in options 
                if o.future_id == future.id]

    template = loader.get_template('marketdata/index.html')
    context = RequestContext(request, {
        'futuredict': futuredict,
    })
    return HttpResponse(template.render(context))

def detail(request, future):

    try:
        futures = Future.objects.all()
        future = [i for i in futures if i.name == future][0]

    except:
        raise Http404

    return render(request, 'marketdata/detail.html', {'future': future})


@csrf_exempt
def refresh_table(request, option_name):
    
    try:
        print " ------------------------------------------------------------------------------ "
        print request.POST
        print " ------------------------------------------------------------------------------ "
        print request.is_ajax()
        print " ------------------------------------------------------------------------------ "
        
        if request.is_ajax() and request.POST:
            option_name = request.POST['option_name']
            options = OptionDefinition.objects.all()
            option = [o for o in options if o.name == option_name][0]

            optioncontracts = sorted(
                OptionContract.objects.filter(optiondefinition_id=option.id), 
                key = lambda x : x.strike)

            published_options = sorted(
                    PublishOptionContract.objects.filter(optiondefinition_id=option.id),
                    key = lambda x : x.strike)

            future = option.future
            today = datetime.date.today()
            time2expiry = hf.diff_dates_year_fraction(option.expiry_date, today)

            # we need to know the last vol to calculate the change, we store this in a dict 
            # accessed by strike value 
            published_options_dict = dict([(i.strike, i.vol) for i in published_options])

            strikes = [float(i) for i in request.POST.getlist('strikes[]')]
            #json_strikes = json.dumps(strikes)
            vols = [float(i) for i in request.POST.getlist('vols[]')]
            call_values = [hf.black_pricer(time2expiry, future.bid, K, v, call = True) for K, v in zip(strikes, vols)]
            put_values = [hf.black_pricer(time2expiry, future.bid, K, v, call = False) for K, v in zip(strikes, vols)]
            call_deltas = [hf.black_delta(time2expiry, future.bid, K, v, call = True) for K, v, in zip(strikes, vols)]

            changes = []
            for s, v in zip(strikes, vols):
                if s in published_options_dict:
                    changes.append(v - published_options_dict[s])
                else:
                    changes.append(0.0)

            first_row = [(future.name, option.month_tag, future.bid, '', '', '', '', '')]

            atm_strike = hf.ATM_strike(strikes, future.bid)
            random_column = []
            for pos, (v, s) in enumerate(zip(vols, strikes)):
                if s == atm_strike:
                    random_column.append(scipy.round_(hf.black_pricer(time2expiry, future.bid, s, v, call = True) + hf.black_pricer(time2expiry, future.bid, s, v, call = False), decimals = 5)) 
                else:
                    random_column.append('')
    
            return HttpResponse(json.dumps({ 
                                            'option': option.name, 
                                            'strikes' : strikes,
                                            'call_values' : [scipy.round_(i, decimals=5) for i in call_values],
                                            'put_values' : [scipy.round_(i, decimals=5) for i in put_values],
                                            'deltas' : [scipy.round_(i, decimals=5) for i in call_deltas],
                                            'vols' : [scipy.round_(i, decimals=5) for i in vols],
                                            'changes' : [scipy.round_(i, decimals=5) for i in changes],
                                            'random_column' : random_column,
                                            'first_row' : first_row,
                                            }), mimetype="application/json" )
        else:
            print "else raise"
            raise Http404

    except Exception as e:
        print e
        raise Http404


@csrf_exempt
def publish_table(request, option_name):
    
    try:
        print " ------------------------------------------------------------------------------ "
        print request.POST
        print " ------------------------------------------------------------------------------ "
        print request.is_ajax()
        print " ------------------------------------------------------------------------------ "
        
        if request.is_ajax() and request.POST:
            option_name = request.POST['option_name']
            options = OptionDefinition.objects.all()
            option = [o for o in options if o.name == option_name][0]

            optioncontracts = sorted(
                OptionContract.objects.filter(optiondefinition_id=option.id), 
                key = lambda x : x.strike)

            published_options = sorted(
                    PublishOptionContract.objects.filter(optiondefinition_id=option.id),
                    key = lambda x : x.strike)

            future = option.future
            today = datetime.date.today()
            time2expiry = hf.diff_dates_year_fraction(option.expiry_date, today)

            # we need to know the last vol to calculate the change, we store this in a dict 
            # accessed by strike value 
            published_options_dict = dict([(i.strike, i.vol) for i in published_options])

            strikes = [float(i) for i in request.POST.getlist('strikes[]')]
            #json_strikes = json.dumps(strikes)
            vols = [float(i) for i in request.POST.getlist('vols[]')]
            call_values = [hf.black_pricer(time2expiry, future.bid, K, v, call = True) for K, v in zip(strikes, vols)]
            put_values = [hf.black_pricer(time2expiry, future.bid, K, v, call = False) for K, v in zip(strikes, vols)]
            call_deltas = [hf.black_delta(time2expiry, future.bid, K, v, call = True) for K, v, in zip(strikes, vols)]

            changes = []
            for s, v in zip(strikes, vols):
                if s in published_options_dict:
                    changes.append(v - published_options_dict[s])
                else:
                    changes.append(0.0)

            for o in published_options:
                o.delete()

            publish_time = datetime.datetime.now()
            for s, v, cval, pval, cdelta, c in zip(strikes, vols, call_values, put_values, call_deltas, changes): 

                if s in published_options_dict:
                    previous_vol = published_option_dict[s]
                else:
                    previous_vol = -99

                option.publishoptioncontract_set.create(future_id = option.future_id, future_value = future.bid, 
                        delta = cdelta, strike = s, call_value = cval, put_value = pval, vol = v, 
                        previous_vol = previous_vol, change = c, publish_time = publish_time) 
    
            return HttpResponse(json.dumps({ 
                                            'Success': True, 
                                            }), mimetype="application/json" )
        else:
            return HttpResponse(json.dumps({ 
                                            'Success': False, 
                                            }), mimetype="application/json" )

    except Exception as e:
        return HttpResponse(json.dumps({ 
                                        'Success': False, 
                                        }), mimetype="application/json" )


@csrf_exempt
def refresh_option(request, option_name):
    
    try:
        print " ------------------------------------------------------------------------------ "
        print request.POST
        print " ------------------------------------------------------------------------------ "
        print request.is_ajax()
        print " ------------------------------------------------------------------------------ "
        
        if request.is_ajax() and request.POST:
            option_name = request.POST['option_name']
            options = OptionDefinition.objects.all()
            option = [o for o in options if o.name == option_name][0]
            optioncontracts = sorted(
                OptionContract.objects.filter(optiondefinition_id=option.id), 
                key = lambda x : x.strike)
    
            strikes = [o.strike for o in optioncontracts]
            json_strikes = json.dumps(strikes)
            bids = [o.bid if o.bid > 0 else None for o in optioncontracts]
            asks = [o.ask if o.ask > 0 else None for o in optioncontracts]
            values = [o.value if o.value > 0 else None for o in optioncontracts]
            bid_volume = [o.bid_volume if o.bid_volume > 0 else None for o in optioncontracts]
            ask_volume = [o.ask_volume if o.ask_volume > 0 else None for o in optioncontracts]
            last_trade_value = [o.last_trade_value if o.last_trade_value > 0 else None for o in optioncontracts]
            last_trade_volume = [o.last_trade_volume if o.last_trade_volume > 0 else None for o in optioncontracts]
            last_updated = json.dumps([o.last_updated.strftime("%Y-%m-%d %H:%M:%S") for o in optioncontracts])

            #get future price
            future = option.future
            callbool = [True if o.easy_screen_mnemonic[-3] == 'c' else False for o in optioncontracts]
            today = datetime.date.today()
            time2expiry = hf.diff_dates_year_fraction(option.expiry_date, today)
    
            # calc vols and deltas
            bid_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, bids, callbool)]
            bid_delta = [hf.black_delta(time2expiry, future.bid, K, vol, call) for K, vol, call in zip(strikes, bid_vols, callbool)]
    
            # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
            # therefore need to choose one of bid or ask. We choose bid.
            ask_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, asks, callbool)]
            # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
            # therefore need to choose one of bid or ask. We choose bid.
            ask_delta = [hf.black_delta(time2expiry, future.bid, K, vol, call) for K, vol, call in zip(strikes, ask_vols, callbool)]
    
            # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
            # therefore need to choose one of bid or ask. We choose bid.
            value_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, values, callbool)]

            #interpolate on vol surface. Presently order 3 spline.
            value_vols = hf.spline_interpolate(value_vols, strikes)
            # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
            # therefore need to choose one of bid or ask. We choose bid.
            value_delta = [hf.black_delta(time2expiry, future.bid, K, vol, call) for K, vol, call in zip(strikes, value_vols, callbool)]

            last_trade_vols = [hf.black_pricer_vol(time2expiry, future.last_trade_value, K, Val, call) for K, Val, call in zip(strikes, last_trade_value, callbool)]

            return HttpResponse(json.dumps({ 
                                            'option': option.name, 
                                            'strikes' : json_strikes,
                                            'bids' : bid_vols,
                                            'bids_delta' : bid_delta,
                                            'asks' : ask_vols,
                                            'asks_delta' : ask_delta,
                                            'values' : value_vols,
                                            'values_delta' : value_delta,
                                            'bid_volume' : bid_volume,
                                            'ask_volume' : ask_volume,
                                            'last_trade_value' : last_trade_vols,
                                            'last_trade_volume' : last_trade_volume,
                                            'last_updated' : last_updated,
                                            }), mimetype="application/json" )
        else:
            print "else raise"
            raise Http404

    except Exception as e:
        print e
        raise Http404
   
    
def option(request, option_name):

    try:
        options = OptionDefinition.objects.all()
        option = [o for o in options if o.name == option_name][0]
        optioncontracts = sorted(
            OptionContract.objects.filter(optiondefinition_id=option.id), 
            key = lambda x : x.strike)

        strikes = [o.strike for o in optioncontracts]
        bids = [o.bid if o.bid > 0 else None for o in optioncontracts]
        json_strikes = json.dumps(strikes)
        json_bids = json.dumps(bids)
        asks = [o.ask if o.ask > 0 else None for o in optioncontracts]
        json_asks = json.dumps(asks)
        values = [o.value if o.value > 0 else None for o in optioncontracts]
        json_values = json.dumps(values)
        bid_volume = json.dumps([o.bid_volume if o.bid_volume > 0 else None for o in optioncontracts])
        ask_volume = json.dumps([o.ask_volume if o.ask_volume > 0 else None for o in optioncontracts])
        last_trade_value = [o.last_trade_value if o.last_trade_value > 0 else None for o in optioncontracts]
        json_last_trade_value = json.dumps(last_trade_value)
        last_trade_volume = json.dumps([o.last_trade_volume if o.last_trade_volume > 0 else None for o in optioncontracts])
        last_updated = json.dumps([o.last_updated.strftime("%Y-%m-%d %H:%M:%S") for o in optioncontracts])

        #get future price
        future = option.future
        callbool = [True if o.easy_screen_mnemonic[-3] == 'c' else False for o in optioncontracts]
        today = datetime.date.today()
        time2expiry = hf.diff_dates_year_fraction(option.expiry_date, today)

        # calc vols and deltas
        bid_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, bids, callbool)]
        json_bid_vols = json.dumps(bid_vols)
        bid_delta = [hf.black_delta(time2expiry, future.bid, K, vol, call) for K, vol, call in zip(strikes, bid_vols, callbool)]
        json_bid_delta = json.dumps(bid_delta)

        # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
        # therefore need to choose one of bid or ask. We choose bid.
        ask_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, asks, callbool)]
        json_ask_vols = json.dumps(ask_vols)
        # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
        # therefore need to choose one of bid or ask. We choose bid.
        ask_delta = json.dumps([hf.black_delta(time2expiry, future.bid, K, vol, call) for K, vol, call in zip(strikes, ask_vols, callbool)])

        # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
        # therefore need to choose one of bid or ask. We choose bid.
        value_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, values, callbool)]

        #interpolate on vol surface. Presently order 3 spline.
        value_vols = hf.spline_interpolate(value_vols, strikes)
        json_value_vols = json.dumps(value_vols)
        # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
        # therefore need to choose one of bid or ask. We choose bid.
        value_delta = [hf.black_delta(time2expiry, future.bid, K, vol, call) for K, vol, call in zip(strikes, value_vols, callbool)]
        json_value_delta = json.dumps(value_delta)

        # always future.bid. Why? you can't hedge against a price future price that don't exist, so we don't use the value. We 
        # therefore need to choose one of bid or ask. We choose bid.
        call_delta = [hf.black_delta(time2expiry, future.bid, K, vol, call = True) for K, vol in zip(strikes, value_vols)]

        last_trade_vols = [hf.black_pricer_vol(time2expiry, future.last_trade_value, K, Val, call) for K, Val, call in zip(strikes, last_trade_value, callbool)]
        json_last_trade_vols = json.dumps(last_trade_vols)
        last_trade_delta = json.dumps([hf.black_delta(time2expiry, future.last_trade_value, K, vol, call) for K, vol, call in zip(strikes, last_trade_vols, callbool)])

        # now for the "published" data
        # ask Gareth about ... 
        # when sourcing the data and adding this to the db, we calculate the ATM option using the mid of the bid - ask spread for the future value. Here when we calcuate 
        # the stradle price we're going to use the future.bid price.
        atm_strike = hf.ATM_strike(strikes, future.bid)
        random_column = []
        for pos, (v, s) in enumerate(zip(value_vols, strikes)):
            if s == atm_strike:
                random_column.append(scipy.round_(hf.black_pricer(time2expiry, future.bid, s, v, call = True) + hf.black_pricer(time2expiry, future.bid, s, v, call = False), decimals = 5)) 
            else:
                random_column.append('')

        table_data = [(future.name, option.month_tag, future.bid, '', '', '', '', '')]
        
        publishedcontracts = sorted(
                PublishOptionContract.objects.filter(optiondefinition_id=option.id),
                key = lambda x : x.strike)

        if len(publishedcontracts) == 0:
                
            published = False
            published_time = json.dumps(datetime.datetime(1900,1,1,0,0,0).strftime("%Y-%m-%d %H:%M:%S"))
            for p in xrange(len(random_column)):
                table_data.append(
                        (
                            scipy.round_(call_delta[p], decimals=5),
                            scipy.round_(strikes[p], decimals=5),
                            random_column[p],
                            scipy.round_(hf.black_pricer(time2expiry, future.bid, strikes[p], value_vols[p], True), decimals=5),
                            scipy.round_(hf.black_pricer(time2expiry, future.bid, strikes[p], value_vols[p], False), decimals=5),
                            scipy.round_(strikes[p], decimals=5),
                            scipy.round_(value_vols[p], decimals=5),
                            '-'
                        )
                    )
        else:
            pass
            # here we need to get stuff from the publishedcontracts




    except:
        raise Http404

    return render(
                    request, 'marketdata/option.html', 
                    {
                        'future': future, 
                        'option': option, 
                        'strikes' : json_strikes,
                        'bids' : json_bid_vols,
                        'bids_delta' : json_bid_delta,
                        'asks' : json_ask_vols,
                        'asks_delta' : ask_delta,
                        'values' : json_value_vols,
                        'values_delta' : json_value_delta,
                        'bid_volume' : bid_volume,
                        'ask_volume' : ask_volume,
                        'last_trade_value' : json_last_trade_vols,
                        'last_trade_volume' : last_trade_volume,
                        'last_updated' : last_updated,
                        'published' : published,
                        'published_time' : published_time,
                        'table_data' : table_data
                     }
                 )

