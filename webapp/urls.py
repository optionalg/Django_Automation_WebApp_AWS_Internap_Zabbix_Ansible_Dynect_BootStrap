from django.conf.urls import patterns, url

from webapp import views

urlpatterns = patterns('',
    url(r'^$', 'webapp.views.index'),
    url(r'^updateDB/$', 'webapp.views.updateDB'),
    url(r'^inventory/$', 'webapp.views.inventory'),
    url(r'^mojo/$', 'webapp.views.mojo'),
    url(r'^failover/$', 'webapp.views.failover'),
    url(r'^console/$', 'webapp.views.console'),
    url(r'^dns/$', 'webapp.views.dns'),
    url(r'^dsf/$', 'webapp.views.dsf'),
    url(r'^exportCSV/$', 'webapp.views.exportCSV'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'webapp/login.html'}),
)
