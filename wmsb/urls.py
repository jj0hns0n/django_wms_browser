from django.conf.urls.defaults import *
from wmsb.models import WmsEndpoint, WmsLayer

urlpatterns = patterns('',
	(r'^wms_layer/(?P<layer_id>\d+)/$', 'wmsb.views.layer'),
)
