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

    



#class ContractCollection(models.Model):
#
#    contract_name = models.CharField(max_length=200)
#    option_type = models.CharField(max_length=200,choices = [('Call','Call'),('Put','Put')])
#    month_tag = models.CharField(max_length=200)
#    expiry_date = models.DateTimeField('Contract Expiry')
#    future = models.CharField(max_length=200) 
#    future_value = models.FloatField() 
#    min_strike = models.FloatField(default = 0.0)
#    max_strike = models.FloatField(default = 0.0)
#    strike_interval = models.FloatField(default = 0.0)
#
#    num_strikes = int( (float(max_strike) - float(min_strike)) / float(strike_interval) )
#    strike = min_strike
#    for i in range(0, num_strikes, 1):
#        Contract(collection = contract_name, future = future, expiry = expiry_date).save()
#        strike += strike_interval 
#
#    #def __unicode__(self):
#    #    pass
#
#
#class Contract(models.Model):
#
#    collection = models.ForeignKey(ContractCollection)
#    future = models.CharField(max_length=200) 
#    future_value = models.FloatField(default = 0.0) 
#    strike = models.FloatField()
#    premium = models.FloatField() 
#    vol = models.FloatField()
#    expiry = models.DateTimeField('Contract Expiry')
#
#    #def __unicode__(self):
#    #    ostring = 'Month: ' + self.month + ', Strike: ' + \
#    #            str(self.strike) + ', Expiry: ' + str(self.expiry)
#    #    return ostring 
#
#
#
