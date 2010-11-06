from django.contrib.gis import admin

from models import *

admin.site.register(WmsEndpoint)
admin.site.register(WmsLayer, admin.GeoModelAdmin)
admin.site.register(WmsLayerField)
