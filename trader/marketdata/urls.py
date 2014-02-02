from django.conf.urls import patterns, url

from marketdata import views

urlpatterns = patterns('',
    # /marketdata/
    url(r'^$', views.index, name='index'),
    url(r'^(?P<future>\w+)/$', views.detail, name='detail'),
    url(r'^option/(?P<option_name>\w+)/$', views.option, name='option'),
    url(r'^option/refresh/(?P<option_name>\w+)/$', views.refresh_option, name='refresh_option'),
    url(r'^option/refresh-table/(?P<option_name>\w+)/$', views.refresh_table, name='refresh_table'),
    url(r'^option/publish-table/(?P<option_name>\w+)/$', views.publish_table, name='publish_table'),
    url(r'^published-tables/', views.published, name='published'),
)


