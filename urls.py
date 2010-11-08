from django.conf.urls.defaults import *
from django.contrib import databrowse

from wmsb.models import WmsEndpoint, WmsLayer

from django.conf import settings
from django.contrib import admin
admin.autodiscover()

databrowse.site.register(WmsEndpoint)
databrowse.site.register(WmsLayer)

urlpatterns = patterns('',
    (r'^$', 'wmsb.views.layers'),
    (r'^wmsb/', include('django_wms_browser.wmsb.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^databrowse/(.*)', databrowse.site.root),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
    )
