from django.conf.urls.defaults import *
from django.contrib import databrowse

from wmsb.models import WmsEndpoint, WmsLayer

from django.conf import settings
from django.contrib import admin
admin.autodiscover()

databrowse.site.register(WmsEndpoint)
databrowse.site.register(WmsLayer)

urlpatterns = patterns('',
    (r'^$', 'wmsb.views.index'),
    (r'^wmsb/', include('django_wms_browser.wmsb.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^databrowse/(.*)', databrowse.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
    )
