# Create your views here.
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import helper_functions as hf

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
            bids = [o.bid for o in optioncontracts]
            asks = [o.ask for o in optioncontracts]
            values = [o.value for o in optioncontracts]
            bid_volume = [o.bid_volume for o in optioncontracts]
            ask_volume = [o.ask_volume for o in optioncontracts]
            last_trade_value = [o.last_trade_value for o in optioncontracts]
            last_trade_volume = [o.last_trade_volume for o in optioncontracts]
            last_updated = json.dumps([o.last_updated.strftime("%Y-%m-%d %H:%M:%S") for o in optioncontracts])

            return HttpResponse(json.dumps({
                                            'option': option.name, 
                                            'strikes' : strikes,
                                            'bids' : bids,
                                            'asks' : asks,
                                            'values' : values,
                                            'bid_volume' : bid_volume,
                                            'ask_volume' : ask_volume,
                                            'last_trade_value' : last_trade_value,
                                            'last_trade_volume' : last_trade_volume,
                                            'last_updated' : last_updated,
                                            }), mimetype="application/json" )
        else:
            print "else raise"
            raise Http404

    except:
        print "except raise"
        raise Http404

    
    
def option(request, option_name):

    try:
        options = OptionDefinition.objects.all()
        option = [o for o in options if o.name == option_name][0]
        optioncontracts = sorted(
            OptionContract.objects.filter(optiondefinition_id=option.id), 
            key = lambda x : x.strike)

        strikes = [o.strike for o in optioncontracts]
        bids = [o.bid for o in optioncontracts]
        asks = [o.ask for o in optioncontracts]
        values = [o.value for o in optioncontracts]
        bid_volume = [o.bid_volume for o in optioncontracts]
        ask_volume = [o.ask_volume for o in optioncontracts]
        last_trade_value = [o.last_trade_value for o in optioncontracts]
        last_trade_volume = [o.last_trade_volume for o in optioncontracts]
        last_updated = json.dumps([o.last_updated.strftime("%Y-%m-%d %H:%M:%S") for o in optioncontracts])

    except:
        raise Http404

    return render(
                    request, 'marketdata/option.html', 
                    {
                        'option': option, 
                        'strikes' : strikes,
                        'bids' : bids,
                        'asks' : asks,
                        'values' : values,
                        'bid_volume' : bid_volume,
                        'ask_volume' : ask_volume,
                        'last_trade_value' : last_trade_value,
                        'last_trade_volume' : last_trade_volume,
                        'last_updated' : last_updated,
                     }
                 )

