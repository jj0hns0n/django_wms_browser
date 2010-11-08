from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from olwidget.widgets import MapDisplay

from wmsb.models import WmsEndpoint, WmsLayer

def index(request):
	layer_list = WmsLayer.objects.all() # TODO: Add order date_added descending after adding field to model 
	paginator = Paginator(layer_list, 20)
	
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		layer_list = paginator.page(page)
	except (EmptyPage, InvalidPage):
		layer_list = paginator.page(1)

	return render_to_response('wmsb/index.html', { 'layer_list': layer_list } , context_instance=RequestContext(request))

def layer(request, layer_id):
	layer = get_object_or_404(WmsLayer, pk=layer_id)
	
	if(layer.latlon_bbox_poly):
		map = MapDisplay(fields=[layer.latlon_bbox_poly], options={'overlay_style': {'fill_opacity': 0.0},}) 
	else:
		map = None
	return render_to_response('wmsb/wms_layer.html', { 'layer' : layer, 'map' : map }, context_instance=RequestContext(request))
	

def about(request):
	return render_to_response('about.html', {}, context_instance=RequestContext(request))
