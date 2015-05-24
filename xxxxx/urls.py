from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'xxxxx.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', include('webapp.urls')),
    url(r'^webapp/', include('webapp.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
