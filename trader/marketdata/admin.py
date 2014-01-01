from django.contrib import admin
from marketdata.models import *

class FutureAdmin(admin.ModelAdmin):
    fields = ['name', 'bloomberg_id', 'easyscreen_id', 'month_tag']

#class OptionDefinitionAdmin(admin.ModelAdmin):
#    fields = ['name', 'bloomberg_prefix', 'easyscreen_prefix', 'month_tag', 'expiry_date', 'strike_interval', 'price_movement', 'number_of_OTM_options']

admin.site.register(Future, FutureAdmin)
admin.site.register(OptionDefinition)#, OptionDefinitionAdmin)
