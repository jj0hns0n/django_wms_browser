from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect

from olwidget.widgets import MapDisplay

from wmsb.models import WmsEndpoint, WmsLayer, WmsLayerField
from wmsb.forms import RegisterWmsEndpointForm

def register_url(request):
	if request.method == 'POST':
		form = RegisterWmsEndpointForm(request.POST)
		if form.is_valid():
			new_url = form.cleaned_data['new_url']
			wmse = WmsEndpoint()
			wms, msg = wmse.parse_save_wms_url(new_url)
			if(wms):
				#TODO: Display/Flash Message that URL Parsed Successfully
				layers = WmsLayer.objects.filter(wms=wmse)	
				return render_to_response('wmsb/server.html', { 'server' : wmse, 'layer_list': layers }, context_instance=RequestContext(request))	
			else:
				#TODO: Display/Flash Error
				return render_to_response('wmsb/register.html', {'form': form, 'msg': msg}, context_instance=RequestContext(request))	
	else:
		form = RegisterWmsEndpointForm()
	return render_to_response('wmsb/register.html', {'form': form,}, context_instance=RequestContext(request))


def servers(request):
	server_list = WmsEndpoint.objects.all() # TODO: Add order date_added descending after adding field to model 
	paginator = Paginator(server_list, 20)
	
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	try:
		server_list = paginator.page(page)
	except (EmptyPage, InvalidPage):
		server_list = paginator.page(1)
	form = RegisterWmsEndpointForm()
	return render_to_response('wmsb/servers.html', { 'server_list': server_list, 'register_form': form} , context_instance=RequestContext(request))

def server(request, server_id):
	wms_server = get_object_or_404(WmsEndpoint, pk=server_id)
	layers = WmsLayer.objects.filter(wms=wms_server)
	
	#TODO: Construct OLWidget Map with all Layers for this endpoint/server?
	
	return render_to_response('wmsb/server.html', { 'server' : wms_server, 'layer_list': layers }, context_instance=RequestContext(request))

def layers(request):
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
	form = RegisterWmsEndpointForm()
	return render_to_response('wmsb/index.html', { 'layer_list': layer_list, 'register_form': form } , context_instance=RequestContext(request))

def layer(request, layer_id):
	layer = get_object_or_404(WmsLayer, pk=layer_id)
	fields = WmsLayerField.objects.filter(wms_layer=layer).order_by('position')
	
	if(layer.latlon_bbox_poly):
		map = MapDisplay(fields=[layer.latlon_bbox_poly], options={'overlay_style': {'fill_opacity': 0.0},}) 
	else:
		map = None
	return render_to_response('wmsb/wms_layer.html', { 'layer' : layer, 'fields': fields, 'map' : map }, context_instance=RequestContext(request))

def search(request):
	return render_to_response('wmsb/search.html', {}, context_instance=RequestContext(request))

def about(request):
	return render_to_response('wmsb/about.html', {}, context_instance=RequestContext(request))
