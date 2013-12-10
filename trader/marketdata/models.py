from django.db import models

# Create your models here.

class Future(models.Model):
    name = models.CharField(max_length=200)
    bloomberg_id = models.CharField(max_length=200)
    easyscreen_id = models.CharField(max_length=200)
    bid = models.FloatField() 
    bid_volume = models.FloatField() 
    ask = models.FloatField() 
    ask_volume = models.FloatField() 
    value = models.FloatField() 
    last_trade_value = models.FloatField()
    last_updated = models.DateTimeField()
    last_trade_volume = models.FloatField()
    month_tag = models.CharField(max_length=200)
    # should we rename expiry_date as effective_date?
    expiry_date = models.DateTimeField()

    def __unicode__(self):
        return self.name


class OptionDefinition(models.Model):
    name = models.CharField(max_length=200)
    future = models.ForeignKey(Future)
    bloomberg_prefix = models.CharField(max_length=200)
    easyscreen_prefix = models.CharField(max_length=200)
    month_tag = models.CharField(max_length=200)
    expiry_date = models.DateTimeField()
    strike_interval = models.FloatField(default=0.5)
    price_movement = models.FloatField(default=0.01)
    number_of_OTM_options = models.IntegerField(default=10)

    def __unicode__(self):
        return self.name + ', based on: ' + str(self.future)


class OptionContract(models.Model):
    optiondefinition = models.ForeignKey(OptionDefinition)
    easy_screen_mnemonic = models.CharField(max_length=200)
    bloomberg_name = models.CharField(max_length=200)
    strike = models.FloatField() 
    bid = models.FloatField() 
    bid_volume = models.FloatField() 
    ask = models.FloatField() 
    ask_volume = models.FloatField() 
    value = models.FloatField() 
    last_trade_value = models.FloatField()
    last_trade_volume = models.FloatField()
    vol = models.FloatField() 
    delta = models.FloatField()
    expiry_date = models.DateTimeField()
    time_to_expiry = models.FloatField() 
    last_updated = models.DateTimeField()

    
class PublishOptionContract(models.Model):
    optiondefinition = models.ForeignKey(OptionDefinition)
    future = models.ForeignKey(Future)
    future_value = models.FloatField() 
    delta = models.FloatField() 
    strike = models.FloatField() 
    call_value = models.FloatField() 
    put_value = models.FloatField() 
    vol = models.FloatField()
    previous_vol = models.FloatField()
    change = models.FloatField()
    publish_time = models.DateTimeField()
    

