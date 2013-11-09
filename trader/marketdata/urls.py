from django.conf.urls import patterns, url

from marketdata import views

urlpatterns = patterns('',
    # /marketdata/
    url(r'^$', views.index, name='index'),
    # /marketdata/FUTURENAME
    url(r'^(?P<future>\w+)/$', views.detail, name='detail'),
    # /marketdata/option/OPTIONNAME
    url(r'^option/(?P<option_name>\w+)/$', views.option, name='option')
)


