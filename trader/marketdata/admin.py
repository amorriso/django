from django.contrib import admin
from marketdata.models import *

class FutureAdmin(admin.ModelAdmin):
    #fields = ['name', 'bloomberg_id', 'easyscreen_id', 'month_tag', 'expiry_date']
    #fields = ['name', 'easyscreen_id', 'month_tag', 'expiry_date']
    fields = ['name', 'easyscreen_id', 'expiry_date']

class OptionDefinitionAdmin(admin.ModelAdmin):
    #fields = ['name', 'future', 'easyscreen_prefix', 'month_tag', 'expiry_date', 'strike_interval', 'price_movement', 'number_of_OTM_options']
    #fields = ['name', 'future', 'easyscreen_prefix', 'expiry_date', 'strike_interval', 'price_movement', 'number_of_OTM_options']
    fields = ['name', 'future', 'easyscreen_prefix', 'expiry_date', 'strike_interval', 'number_of_OTM_options']

admin.site.register(Future, FutureAdmin)
admin.site.register(OptionDefinition, OptionDefinitionAdmin)
