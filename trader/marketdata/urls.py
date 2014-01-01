from django.conf.urls import patterns, url

from marketdata import views

urlpatterns = patterns('',
    # /marketdata/
    url(r'^$', views.index, name='index'),
    # /marketdata/FUTURENAME
    url(r'^(?P<future>\w+)/$', views.detail, name='detail'),
    # /marketdata/option/OPTIONNAME
    url(r'^option/(?P<option_name>\w+)/$', views.option, name='option'),
    # /marketdata/option/OPTIONNAME/refresh (ajax)
    url(r'^option/refresh/(?P<option_name>\w+)/$', views.refresh_option, name='refresh_option'),
    # /marketdata/option/OPTIONNAME/refresh-table (ajax)
    url(r'^option/refresh-table/(?P<option_name>\w+)/$', views.refresh_table, name='refresh_table'),
    # /marketdata/option/OPTIONNAME/publish-table (ajax)
    url(r'^option/publish-table/(?P<option_name>\w+)/$', views.publish_table, name='publish_table'),
    # /marketdata/published
    url(r'^published-tables/', views.published, name='published'),
)


