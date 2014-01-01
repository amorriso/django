# Create your views here.
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import datetime
import json
import helper_functions as hf
import scipy
import collections
import pdb

from marketdata.models import *

@csrf_exempt
def home(request):

    selected_options = set(request.POST.keys())

    futures = sorted(
            Future.objects.all() ,
            key = lambda x : x.name)
    
    futures = [el for el in futures 
            if el.expiry_date > datetime.datetime.today()]

    published_options = sorted(
            #PublishOptionContract.objects.filter(optiondefinition_id=option.id),
            PublishOptionContract.objects.all(),
            key = lambda x : x.strike)

    published_option_definitions = set([])
    for o in published_options:
        published_option_definitions.add(o.optiondefinition)

    options = OptionDefinition.objects.all() 
    options =  [el for el in options 
            if el.expiry_date > datetime.datetime.today() and el in published_option_definitions]

    futuredict = collections.OrderedDict()
    checked_futuredict = collections.OrderedDict()

    for future in futures:
        #futuredict[future] = [o for o in options 
        #        if o.future_id == future.id]
        futuredict[future] = [] 
        for o in options:
            if o.future_id == future.id:
                if o.name in selected_options:
                    futuredict[future].append((o,True))
                else:
                    futuredict[future].append((o,False))

    template = loader.get_template('index.html')
    context = RequestContext(request, {
        'futuredict': futuredict,
    })
    return HttpResponse(template.render(context))


@csrf_exempt
def prices(request):

    try:
        required_options = set([o for o in request.POST.keys() if request.POST[o] == u'true'])

        published_options = sorted(
                #PublishOptionContract.objects.filter(optiondefinition_id=option.id),
                PublishOptionContract.objects.all(),
                key = lambda x : x.strike)
    
        published_option_definitions = set([])
        for o in published_options:
            published_option_definitions.add(o.optiondefinition)
    
        futures = sorted(
                Future.objects.all() ,
                key = lambda x : x.name)
    
        futures = [el for el in futures 
                if el.expiry_date > datetime.datetime.today()]
    
        option_definitions = OptionDefinition.objects.all() 

        #if len(required_options) == 0:
        #    required_options = set(option_definitions)

        option_definitions =  [el for el in option_definitions
                if el.expiry_date > datetime.datetime.today() and el.name in required_options]
        #option_definition_dict = dict([(o, o.name) for o in option_definitions])
    
        futuredict = collections.OrderedDict()
        for future in futures:
            futuredict[future] = collections.OrderedDict()
            for option_def in option_definitions:
                if option_def.future == future:
                    #futuredict[future][option_definition_dict[option_def]] = collections.OrderedDict()
                    futuredict[future][option_def] = collections.OrderedDict()
    
                    publishedcontracts = sorted(
                            [i for i in published_options if i.optiondefinition == option_def],
                            key = lambda x : x.strike)
    
                    if len(publishedcontracts) > 0:
                        futuredict[future][option_def]['published'] = True
                        #futuredict[future][option_definition_dict[option_def]]['published_time'] = publishedcontracts[0].publish_time
                        futuredict[future][option_def]['published_time'] = publishedcontracts[0].publish_time
        
                        table_data = []
                        atm_strike = hf.ATM_strike([c.strike for c in publishedcontracts], publishedcontracts[0].future_value)
                        time2expiry = hf.diff_dates_year_fraction(option_def.expiry_date, publishedcontracts[0].publish_time)
        
                        random_column = []
                        for pos, o in enumerate(publishedcontracts):
                            if o.strike == atm_strike:
                                random_column.append(scipy.round_(hf.black_pricer(time2expiry, o.future_value, o.strike, o.vol, call = True) + hf.black_pricer(time2expiry, o.future_value, o.strike, o.vol, call = False), decimals = 5)) 
                            else:
                                random_column.append('')
        
                        published_strikes = []
                        published_vols = []
                        for pos, c in enumerate(publishedcontracts):
                            table_data.append(
                                    (
                                        scipy.round_(c.strike, decimals=5),
                                        scipy.round_(c.call_value, decimals=5),
                                        scipy.round_(c.put_value, decimals=5),
                                        random_column[pos],
                                        scipy.round_(c.call_delta, decimals=5),
                                        scipy.round_(c.put_delta, decimals=5),
                                        scipy.round_(c.gamma, decimals=5),
                                        scipy.round_(c.theta, decimals=5),
                                        scipy.round_(c.vega, decimals=5),
                                        scipy.round_(c.vol, decimals=5),
                                        scipy.round_(c.change, decimals=5),
                                    )
                                )
                            published_strikes.append(c.strike)
                            published_vols.append(c.vol)
                        #futuredict[future][option_definition_dict[option_def]]['table_data'] = table_data
                        futuredict[future][option_def]['table_data'] = table_data
                        
                        optioncontracts = sorted(
                            OptionContract.objects.filter(optiondefinition_id=option_def.id), 
                            key = lambda x : x.strike)

                        strikes = [o.strike for o in optioncontracts] 

                        all_strikes = set(strikes)
                        all_strikes.update(set(published_strikes))
                        all_strikes = sorted(list(all_strikes))

                        published_vols = hf.remap_values(published_vols, published_strikes, all_strikes)
                        futuredict[future][option_def]['published_vols'] = published_vols

                        bids = hf.remap_values([o.bid if o.bid > 0 else None for o in optioncontracts], strikes, all_strikes)
                        asks = hf.remap_values([o.ask if o.ask > 0 else None for o in optioncontracts], strikes, all_strikes)
                        last_trade_value = hf.remap_values([o.last_trade_value if o.last_trade_value > 0 else None for o in optioncontracts], strikes, all_strikes)
                        values = hf.remap_values([o.value if o.value > 0 else None for o in optioncontracts], strikes, all_strikes)
                
                        future = option_def.future
                        callbool = [True if o.easy_screen_mnemonic[-3] == 'c' else False for o in optioncontracts]
                        today = datetime.date.today()
                        time2expiry = hf.diff_dates_year_fraction(option_def.expiry_date, today)
                
                        bid_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, bids, callbool)]
                        ask_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, asks, callbool)]
                        last_trade_vols = [hf.black_pricer_vol(time2expiry, future.last_trade_value, K, Val, call) for K, Val, call in zip(strikes, last_trade_value, callbool)]
                        value_vols = [hf.black_pricer_vol(time2expiry, future.bid, K, Val, call) for K, Val, call in zip(strikes, values, callbool)]
                        value_vols = hf.spline_interpolate(value_vols, strikes)

                        futuredict[future][option_def]['strikes'] = json.dumps(all_strikes)
                        futuredict[future][option_def]['bid_vols'] = json.dumps(bid_vols)
                        futuredict[future][option_def]['ask_vols'] = json.dumps(ask_vols)
                        futuredict[future][option_def]['last_trade_vols'] = json.dumps(last_trade_vols)
                        futuredict[future][option_def]['value_vols'] = json.dumps(value_vols)
        
                    else:
                        futuredict[future][option_def]['published'] = False
    
        template = loader.get_template('prices.html')
        context = RequestContext(request, {
            'futuredict': futuredict
            })
        return HttpResponse(template.render(context))

    except Exception as e:
        print e
        raise Http404



    return render(request, 'prices.html')
