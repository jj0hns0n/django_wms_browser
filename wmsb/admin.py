from django.contrib.gis import admin

from django_wms_browser.wmsb.models import WmsEndpoint, OutputFormat, WmsCapability, WmsLayer, WmsLayerField, LayerAttribution, WmsStyle

admin.site.register(WmsEndpoint)
admin.site.register(OutputFormat)
admin.site.register(WmsCapability)
admin.site.register(WmsLayer, admin.GeoModelAdmin)
admin.site.register(WmsLayerField)
admin.site.register(LayerAttribution)
admin.site.register(WmsStyle)
