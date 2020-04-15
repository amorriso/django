import os
import sys
sys.path.append('..')
import datetime
from django.db import models

# Create your models here.

class Future(models.Model):
    name = models.CharField(max_length=200, unique=True)
    bloomberg_id = models.CharField(max_length=200, default = 'BLOOM')
    easyscreen_id = models.CharField(max_length=200)
    barchart_id = models.CharField(max_length=200)
    bid = models.FloatField(default = -99) 
    bid_volume = models.FloatField(default = -99) 
    ask = models.FloatField(default = -99) 
    ask_volume = models.FloatField(default = -99) 
    value = models.FloatField(default = -99) 
    last_trade_value = models.FloatField(default = -99)
    last_updated = models.DateTimeField(default = datetime.datetime(1900,1,1,0,0,0))
    last_trade_volume = models.FloatField(default = -99)
    month_tag = models.CharField(max_length=200, default = 'NA')
    # should we rename expiry_date as effective_date?
    expiry_date = models.DateTimeField(default = datetime.datetime(1900,1,1,0,0,0))

    def __unicode__(self):
        return self.name


    def save(self, *args, **kwargs):

        if self.easyscreen_id != self.barchart_id:
            self.easyscreen_id = self.barchart_id

        super(Future, self).save(*args, **kwargs)




class OptionDefinition(models.Model):
    name = models.CharField(max_length=200)
    future = models.ForeignKey(Future)
    bloomberg_prefix = models.CharField(max_length=200, default = 'BLOOM')
    month_tag = models.CharField(max_length=200, default = 'NA')
    expiry_date = models.DateTimeField()
    strike_interval = models.FloatField(default=0.5)
    price_movement = models.FloatField(default=0.01)
    number_of_OTM_options = models.IntegerField(default=10, verbose_name="No. of options")


    def __unicode__(self):
        return self.name + ', based on: ' + str(self.future)


    def save(self, *args, **kwargs):

        if not self.month_tag:
            self.month_tag = self.expiry_date.strftime('%b').upper()

        super(OptionDefinition, self).save(*args, **kwargs)



class OptionContract(models.Model):
    optiondefinition = models.ForeignKey(OptionDefinition)
    easy_screen_mnemonic = models.CharField(max_length=200, unique=True)
    bloomberg_name = models.CharField(max_length=200, default = 'BLOOM')
    strike = models.FloatField(default = -99) 
    bid = models.FloatField(default = -99) 
    bid_volume = models.FloatField(default = -99) 
    ask = models.FloatField(default = -99) 
    ask_volume = models.FloatField(default = -99) 
    value = models.FloatField(default = -99) 
    last_trade_value = models.FloatField(default = -99)
    last_trade_volume = models.FloatField(default = -99)
    vol = models.FloatField(default = -99) 
    delta = models.FloatField(default = -99)
    expiry_date = models.DateTimeField(default = datetime.datetime(1900,1,1,0,0,0))
    time_to_expiry = models.FloatField(default = -99) 
    last_updated = models.DateTimeField(default = datetime.datetime(1900,1,1,0,0,0))

    
class PublishOptionContract(models.Model):
    optiondefinition = models.ForeignKey(OptionDefinition)
    future = models.ForeignKey(Future)
    future_value = models.FloatField(default = -99) 
    call_delta = models.FloatField(default = -99) 
    put_delta = models.FloatField(default = -99) 
    gamma = models.FloatField(default = -99) 
    theta = models.FloatField(default = -99) 
    vega = models.FloatField(default = -99) 
    strike = models.FloatField(default = -99) 
    call_value = models.FloatField(default = -99) 
    put_value = models.FloatField(default = -99) 
    vol = models.FloatField(default = -99)
    previous_vol = models.FloatField(default = -99)
    change = models.FloatField(default = -99)
    publish_time = models.DateTimeField(default = datetime.datetime(1900,1,1,0,0,0))
    

