from django.conf.urls.defaults import *
from wmsb.models import WmsEndpoint, WmsLayer

urlpatterns = patterns('',
	(r'^servers/$', 'wmsb.views.servers'),
	(r'^server/(?P<server_id>\d+)/$', 'wmsb.views.server'),
        (r'^layers/$', 'wmsb.views.layers'),
	(r'^layer/(?P<layer_id>\d+)/$', 'wmsb.views.layer'),
        (r'^register_url/$', 'wmsb.views.register_url'),
        (r'^search/$', 'wmsb.views.search'),
        (r'^about/$', 'wmsb.views.about'),
)
