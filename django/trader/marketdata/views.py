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

@login_required
def index(request):

    futures = Future.objects.filter(expiry_date__gte = datetime.datetime.now()).order_by('expiry_date', 'name')

    options = OptionDefinition.objects.all() 
    options =  [el for el in options 
            if el.expiry_date > datetime.datetime.today()]

    futuredict = collections.OrderedDict()
    for future in futures:
        futuredict[future] = [o for o in options 
                if o.future_id == future.id]

    template = loader.get_template('marketdata/index.html')
    context = RequestContext(request, {
        'futuredict': futuredict,
    })

    return HttpResponse(template.render(context))

@login_required
def detail(request, future):

    try:
        futures = Future.objects.filter(expiry_date__gte = datetime.datetime.now()).order_by('expiry_date', 'name')
        future = [i for i in futures if i.name == future][0]

    except:
        raise Http404

    return render(request, 'marketdata/detail.html', {'future': future})


@login_required
def published(request):

    try:
        published_options = sorted(
                PublishOptionContract.objects.all(),
                key = lambda x : x.strike)
    
        published_option_definitions = set([])
        for o in published_options:
            published_option_definitions.add(o.optiondefinition)
    
        futures = Future.objects.filter(expiry_date__gte = datetime.datetime.now()).order_by('expiry_date', 'name')
    
        option_definitions = OptionDefinition.objects.all() 
        option_definitions =  [el for el in option_definitions
                if el.expiry_date > datetime.datetime.today()]
        #option_definition_dict = dict([(o, o.name) for o in option_definitions])
    
        futuredict = collections.OrderedDict()
        counter = 0
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
                        futuredict[future][option_def]['counter'] = counter
                        counter += 1
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
                                        scipy.round_(c.call_delta, decimals=2),
                                        scipy.round_(c.put_delta, decimals=2),
                                        scipy.round_(c.gamma, decimals=3),
                                        scipy.round_(c.theta, decimals=2),
                                        scipy.round_(c.vega, decimals=2),
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
                        futuredict[future][option_def]['published_vols'] = json.dumps(published_vols)

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
    
        template = loader.get_template('marketdata/published.html')
        context = RequestContext(request, {
            'futuredict': futuredict
            })
        return HttpResponse(template.render(context))

    except Exception as e:
        #print e
        raise Http404



@login_required
@csrf_exempt
def refresh_table(request, option_name):
    
    try:
        #print " ------------------------------------------------------------------------------ "
        #print request.POST
        #print " ------------------------------------------------------------------------------ "
        #print request.is_ajax()
        #print " ------------------------------------------------------------------------------ "
        
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
            published_options_changes_dict = dict([(i.strike, i.change) for i in published_options])

            strikes = [float(i) for i in request.POST.getlist('strikes[]')]
            #json_strikes = json.dumps(strikes)
            vols = [float(i) for i in request.POST.getlist('vols[]')]
            call_values = [hf.black_pricer(time2expiry, future.bid, K, v, call = True) for K, v in zip(strikes, vols)]
            put_values = [hf.black_pricer(time2expiry, future.bid, K, v, call = False) for K, v in zip(strikes, vols)]
            call_deltas = [hf.black_delta(time2expiry, future.bid, K, v, call = True) for K, v, in zip(strikes, vols)]
            # extra stuff Gareth wants
            put_delta = [hf.black_delta(time2expiry, future.bid, K, vol, call = False) for K, vol in zip(strikes, vols)]
            value_gamma = [hf.black_gamma(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, vols)]
            value_theta = [hf.black_theta(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, vols)]
            value_vega = [hf.black_vega(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, vols)]

            changes = []
            # if we're updating on a publish table event we just want the changes from the db, this is because
            # the db gets changed before we update the table, therefore when we query the db to find what the
            # old vols were, because we've just changed them, they're the same as the new.
            if request.POST['update'] == 'gradeX':
                for s, v in zip(strikes, vols):
                    changes.append(published_options_changes_dict[s])
            # if we're updated on an update table event, then we need to calculate the changes
            else:
                for s, v in zip(strikes, vols):
                    if s in published_options_dict:
                        changes.append(v - published_options_dict[s])
                    else:
                        changes.append(0.0)

            #print changes

            heading_row = [future.name, option.name, future.bid]

            atm_strike = hf.ATM_strike(strikes, future.bid)
            random_column = []
            for pos, (v, s) in enumerate(zip(vols, strikes)):
                if s == atm_strike:
                    random_column.append(scipy.round_(hf.black_pricer(time2expiry, future.bid, s, v, call = True) + hf.black_pricer(time2expiry, future.bid, s, v, call = False), decimals = 5)) 
                else:
                    random_column.append('')
    
            return HttpResponse(json.dumps({ 
                                            'strikes' : strikes,
                                            'call_values' : [scipy.round_(i, decimals=5) for i in call_values],
                                            'put_values' : [scipy.round_(i, decimals=5) for i in put_values],
                                            'call_deltas' : [scipy.round_(i, decimals=5) for i in call_deltas],
                                            'put_deltas' : [scipy.round_(i, decimals=5) for i in put_delta],
                                            'value_gamma' : [scipy.round_(i, decimals=5) for i in value_gamma],
                                            'value_theta' : [scipy.round_(i, decimals=5) for i in value_theta],
                                            'value_vega' : [scipy.round_(i, decimals=5) for i in value_vega],
                                            'vols' : [scipy.round_(i, decimals=5) for i in vols],
                                            'changes' : [scipy.round_(i, decimals=5) for i in changes],
                                            'random_column' : random_column,
                                            'heading_row' : heading_row,
                                            }), mimetype="application/json" )
        else:
            #print "else raise"
            raise Http404

    except Exception as e:
        #print e
        raise Http404


@login_required
@csrf_exempt
def publish_table(request, option_name):
    
    try:
        #print " ------------------------------------------------------------------------------ "
        #print request.POST
        #print " ------------------------------------------------------------------------------ "
        #print request.is_ajax()
        #print " ------------------------------------------------------------------------------ "
        
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

            # extra stuff Gareth wants
            put_deltas = [hf.black_delta(time2expiry, future.bid, K, vol, call = False) for K, vol in zip(strikes, vols)]
            value_gamma = [hf.black_gamma(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, vols)]
            value_theta = [hf.black_theta(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, vols)]
            value_vega = [hf.black_vega(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, vols)]

            changes = []
            for s, v in zip(strikes, vols):
                if s in published_options_dict:
                    changes.append(v - published_options_dict[s])
                else:
                    changes.append(0.0)

            for o in published_options:
                o.delete()

            publish_time = datetime.datetime.now()
            for s, v, cval, pval, cdelta, pdelta, g, th, veg, c in zip(strikes, vols, call_values, put_values, call_deltas, put_deltas, value_gamma, value_theta, value_vega, changes): 

                if s in published_options_dict:
                    previous_vol = published_options_dict[s]
                else:
                    previous_vol = -99

                option.publishoptioncontract_set.create(future_id = option.future_id, future_value = future.bid, 
                        call_delta = cdelta, put_delta = pdelta, gamma = g, theta = th, vega = veg, strike = s, call_value = cval, put_value = pval, vol = v, 
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


@login_required
@csrf_exempt
def refresh_option(request, option_name):
    
    try:
        #print " ------------------------------------------------------------------------------ "
        #print request.POST
        #print " ------------------------------------------------------------------------------ "
        #print request.is_ajax()
        #print " ------------------------------------------------------------------------------ "
        
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

            #print "refresh_option bids ..."
            #print bid_vols

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
                                            'future_bid': future.bid, 
                                            'future_last_updated': future.last_updated.strftime("%Y-%m-%d %H:%M:%S"), 
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
            #print "else raise"
            raise Http404

    except Exception as e:
        #print e
        raise Http404
   
    
@login_required
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

        # extra stuff Gareth wants
        put_delta = [hf.black_delta(time2expiry, future.bid, K, vol, call = False) for K, vol in zip(strikes, value_vols)]
        value_gamma = [hf.black_gamma(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, value_vols)]
        value_theta = [hf.black_theta(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, value_vols)]
        value_vega = [hf.black_vega(time2expiry, future.bid, K, vol) for K, vol in zip(strikes, value_vols)]

        
        publishedcontracts = sorted(
                PublishOptionContract.objects.filter(optiondefinition_id=option.id),
                key = lambda x : x.strike)

        if len(publishedcontracts) == 0:

            published = False
            published_time = json.dumps(datetime.datetime(1900,1,1,0,0,0).strftime("%Y-%m-%d %H:%M:%S"))
            table_data = []#(future.name, option.month_tag, future.bid, '', '', '', '', '')]

            atm_strike = hf.ATM_strike(strikes, future.bid)
            random_column = []
            for pos, (v, s) in enumerate(zip(value_vols, strikes)):
                if s == atm_strike:
                    random_column.append(scipy.round_(hf.black_pricer(time2expiry, future.bid, s, v, call = True) + hf.black_pricer(time2expiry, future.bid, s, v, call = False), decimals = 5)) 
                else:
                    random_column.append('')

            for p in xrange(len(random_column)):
                table_data.append(
                        (
                            scipy.round_(strikes[p], decimals=5),
                            scipy.round_(hf.black_pricer(time2expiry, future.bid, strikes[p], value_vols[p], True), decimals=5),
                            scipy.round_(hf.black_pricer(time2expiry, future.bid, strikes[p], value_vols[p], False), decimals=5),
                            random_column[p],
                            scipy.round_(call_delta[p], decimals=5),
                            scipy.round_(put_delta[p], decimals=5),
                            scipy.round_(value_gamma[p], decimals=5),
                            scipy.round_(value_theta[p], decimals=5),
                            scipy.round_(value_vega[p], decimals=5),
                            scipy.round_(value_vols[p], decimals=5),
                            '-'
                        )
                    )
        else:
            # here we need to get stuff from the publishedcontracts
            published = True
            published_time = publishedcontracts[0].publish_time
            table_data = []#(future.name, option.month_tag, publishedcontracts[0].future_value, '', '', '', '', '')]

            atm_strike = hf.ATM_strike([c.strike for c in publishedcontracts], publishedcontracts[0].future_value)
            time2expiry = hf.diff_dates_year_fraction(option.expiry_date, publishedcontracts[0].publish_time)

            random_column = []
            for pos, o in enumerate(publishedcontracts):
                if o.strike == atm_strike:
                    random_column.append(scipy.round_(hf.black_pricer(time2expiry, o.future_value, o.strike, o.vol, call = True) + hf.black_pricer(time2expiry, o.future_value, o.strike, o.vol, call = False), decimals = 5)) 
                else:
                    random_column.append('')

            for pos, c in enumerate(publishedcontracts):
                table_data.append(
                        (
                            scipy.round_(c.strike, decimals=5),
                            scipy.round_(c.call_value, decimals=5),
                            scipy.round_(c.put_value, decimals=5),
                            random_column[pos],
                            scipy.round_(c.call_delta, decimals=2),
                            scipy.round_(c.put_delta, decimals=2),
                            scipy.round_(c.gamma, decimals=3),
                            scipy.round_(c.theta, decimals=2),
                            scipy.round_(c.vega, decimals=2),
                            scipy.round_(c.vol, decimals=5),
                            scipy.round_(c.change, decimals=5),
                        )
                    )

    except Exception as e:
        #print e
        #raise Http404
        return render(
                    request, 'marketdata/no-data-option.html',
                    {
                        'option': option, 
                    })

    return render(
                    request, 'marketdata/option.html', 
                    {
                        'future': future, 
                        'future_bid': future.bid, 
                        'future_last_updated': future.last_updated, 
                        'option': option, 
                        'strikes' : json_strikes,
                        'non_json_strikes' : strikes,
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

