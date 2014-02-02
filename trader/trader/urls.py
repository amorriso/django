from django.conf.urls import patterns, include, url 
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'trader.views.home', name='home'),
    url(r'^prices\.html$', 'trader.views.prices', name='prices'),
    url(r'^skews\.html$', 'trader.views.skews', name='skews'),
    url(r'^index\.html$', 'trader.views.home', name='home'),
    url(r'^refresh/(?P<option_name>\w+)/$', 'trader.views.refresh_option', name='refresh_option'),
    # url(r'^trader/', include('trader.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^marketdata/', include('marketdata.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root' : settings.MEDIA_ROOT})
)
