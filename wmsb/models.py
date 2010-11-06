from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon

from owslib.wms import WebMapService

from urllib import urlencode
from BeautifulSoup import BeautifulSoup

# TODO: Figure out why I cannot import owslib.util
import sys
sys.path.append('/usr/src/OWSLib/owslib')
import util

# ********************************************
# TODO: Verify ALL entities against WMS Spec
#       and DTD and modify model accordingly
# ********************************************

class WmsEndpoint(models.Model):
	name = models.CharField(max_length=255) # shall include
	title = models.CharField(max_length=255) # shall include
	abstract = models.TextField(null=True, blank=True) # optional
	keywords = models.TextField(null=True, blank=True) # optional
	online_resource = models.URLField(verify_exists = False) # shall include
	fees = models.CharField(max_length=1000, null=True, blank=True)
	access_contraints = models.CharField(max_length=255, null=True, blank=True)
	version = models.CharField(max_length=10, null=True, blank=True)
	#username # Should these be saved or requested every time?
	#password
	# TODO: Verify Service Contact Info against WMS spec, more than one allowed?
	contact_person = models.CharField(max_length=255, null=True, blank=True)
	contact_organization = models.CharField(max_length=255, null=True, blank=True)
	contact_position = models.CharField(max_length=255, null=True, blank=True)
	contact_address_type = models.CharField(max_length=255, null=True, blank=True)
	contact_address = models.CharField(max_length=255, null=True, blank=True)
	contact_city = models.CharField(max_length=255, null=True, blank=True)
	contact_state_province = models.CharField(max_length=255, null=True, blank=True)
	contact_post_code = models.CharField(max_length=255, null=True, blank=True)
	contact_country = models.CharField(max_length=255, null=True, blank=True)
	contact_voice_telephone = models.CharField(max_length=255, null=True, blank=True)
	contact_fax_telephone = models.CharField(max_length=255, null=True, blank=True)
	contact_email = models.CharField(max_length=255, null=True, blank=True)

	def __unicode__(self):
		return self.title

	def parse_wms_url(self, url, username=None, password=None):
		# TODO: Check for existing WMS record for same url
		# If exists update it rather than creating new record
		wms = WebMapService(url)
		# TODO: save username/password?
		self.name = wms.identification.type
		self.version = wms.identification.version
		self.title = wms.identification.title
		self.abstract = wms.identification.abstract
		self.keywords = ','.join(wms.identification.keywords)
		# Not Implemented by OWSLib 
		# TODO: Add to OWSLib (access_constraings, fees)
		#self.access_constraints = wms.identification.accessconstraints 
		#self.fees = wms.identification.fees
		self.online_resource = wms.provider.url
		# TODO: Save ServiceProvider/ContactMetadata
		# TODO: Save SRSs for Service
		self.save()
		
		for layer in list(wms.contents):
			wmsl = WmsLayer()
			wmsl.wms = self 
			wmsl.title = wms[layer].title
			wmsl.name = wms[layer].name
			wmsl.keywords = ','.join(wms[layer].keywords)
			wmsl.queryable = wms[layer].queryable
			# Not Implemented by OWSLib 
			# TODO: Implement in OWSLib (abstract, cascaded, opaque, no_subsets, fixed_width, fixed_height)
			#wmsl.abstract = wms[layer].abstract 
			#wmsl.cascaded
			#wmsl.opaque
			#wmsl.no_subsets
			#wmsl.fixed_width
			#wmsl.fixed_height
			wmsl.save()	

			# TODO: Save Native SRS and BBOX
			bbox = wms[layer].boundingBoxWGS84
			if(bbox == None):
				#Parent Layer?
				continue
			else:
				# TODO: Move to bbox2poly function
				# TODO: Test if bbox is valid for EPSG:4326
				bboxpoly = Polygon(((bbox[0], bbox[3]), (bbox[2], bbox[3]), (bbox[2], bbox[1]), (bbox[0], bbox[1]), (bbox[0], bbox[3])))
				wmsl.latlon_bbox_poly = bboxpoly
				wmsl.latlon_bbox = bbox
				wmsl.save()

			# TODO: Save Styles
			# TODO: Save SRSs for Layer

			wmsl.generate_preview_image()	
	
			# This is a dirty ugly hack :( the WMS Specification does *not* require 
			# that servers provide a way to query a layer for its features attributes.
			# nor require that the output of GetFeatureInfo be in a 'standard format'
			# So various server implementations do it differently.
			# This is using the text/html output which *most* servers support
			# The response is parsed by BeautifulSoup and the columns derived
			# Tested against geoserver and esri WMS implementations
			# TODO: Needs Further Testing, and discusion of alternatives needed
			# TODO: Derive Max/Min/Mean/Median/StdDev by requesting all records?? 

			if(wms[layer].queryable):
				base_url = wms.getOperationByName('GetFeatureInfo').methods['Get']['url']
				request = {'version': wms.version, 'request': 'GetFeatureInfo'}
				request['bbox'] = ','.join([str(x) for x in bbox])
				request['LAYERS'] = layer
				request['QUERY_LAYERS'] = layer
				request['feature_count'] = 1 # Get only the first Feature
				request['width'] = 1 # Get a 1x1 Image
				request['height'] = 1
				request['srs'] = 'EPSG:4326'
				request['info_format'] = 'text/html'
				request['x'] = 1 # Query the 1x1 image
				request['y'] = 1

				data = urlencode(request)
				u = util.openURL(url, data)
				soup = BeautifulSoup(u)
				count = 0
				for field in soup.findAll('th'):
					if(field.string == None):
						field_name = field.contents[0].string
					else:
						field_name = field.string
					WmsLayerField(wms_layer=wmsl, position = count, name=unicode(field_name)).save()

class OutputFormat(models.Model):
	format = models.CharField(max_length=255, null=True, blank=True)

CAPABILITY_CHOICES = (
	('gc', 'GetCapabilities'),
	('gm', 'GetMap'),
	('gf', 'GetFeatureInfo'),
	('dl', 'DescribeLayer'),
	('gl', 'GetLegendGraphic'),
	('gs', 'GetStyles'),
	('ps', 'PutStyles'))

class WmsCapability(models.Model):
	wms = models.ForeignKey(WmsEndpoint)
	capability = models.CharField(max_length=2, choices=CAPABILITY_CHOICES)
	# TODO: Implement DCP Type
	formats = models.ManyToManyField(OutputFormat)

# TODO: Implement Exceptions
# TODO: Implement VendorSpecificCapabilities
# TODO: Implement UserDefinedSymbolization

class WmsLayer(models.Model):
	wms = models.ForeignKey(WmsEndpoint)
	title = models.CharField(max_length=255)
	name = models.CharField(max_length=255, null=True, blank=True)
	abstract = models.TextField(null=True, blank=True)
	keywords = models.TextField(null=True, blank=True)
	#parent = models.ForeignKey(WmsLayer) # TODO: Implement Parent Layer Inheritance
	queryable = models.NullBooleanField()
	cascaded = models.PositiveIntegerField(null=True, blank=True)
	opaque = models.NullBooleanField()
	no_subsets = models.NullBooleanField()
	fixed_width = models.PositiveIntegerField(null=True, blank=True)
	fixed_height = models.PositiveIntegerField(null=True, blank=True)
	#AuthorityURL
	#Itentifier
	#srs
	#native_bbox
	latlon_bbox = models.CharField(max_length=255, null=True, blank=True)
	latlon_bbox_poly = models.PolygonField(null=True, blank=True)
	#metadata
	min_scale_hint = models.PositiveIntegerField(null=True, blank=True)
	max_scale_hint = models.PositiveIntegerField(null=True, blank=True)
	#dimension
	#extent
	#FeatureListURL
	#layer thumbnail
	objects = models.GeoManager()
	def __unicode__(self):
		return self.title

	def generate_preview_image(self, styles=None):
		wms = WebMapService(self.wms.online_resource)
		img = wms.getmap(layers=[self.name],
			srs='EPSG:4326',
			bbox=self.latlon_bbox,
			size=(300,250), # TODO: Calculate optimum size for preview image at this approx size
			format='image/jpeg',
			transparent=True)
		out = open(('%s.jpg' % (self.name)), 'wb')
		out.write(img.read())
		out.close()

FIELD_TYPE_CHOICES = (
	('text', 'Text'),
	('int', 'Integer'),
	('dec', 'Decimal'))

class WmsLayerField(models.Model):
	wms_layer = models.ForeignKey(WmsLayer)
	position = models.PositiveIntegerField()
	name = models.CharField(max_length=255, null=True, blank=True)
	type = models.CharField(max_length=5, choices=FIELD_TYPE_CHOICES, null=True, blank=True)
	# TODO: Calculate Max/Min/Range/Median/Mean/StdDev for numeric types
	def __unicode__(self):
		return self.name

class LayerAttribution(models.Model):
	title = models.CharField(max_length=255)
	name = models.CharField(max_length=255)
	online_resource = models.URLField(verify_exists = False)
	logo_format  = models.CharField(max_length=50, null=True, blank=True)
	logo_online_resource = models.URLField(verify_exists = False)

class WmsStyle(models.Model):
	wms = models.ForeignKey(WmsEndpoint)
	title = models.CharField(max_length=255)
	name = models.CharField(max_length=255)
	abstract = models.TextField(null=True, blank=True)
	legend_online_resource = models.URLField(verify_exists = False)
	legend_width = models.PositiveIntegerField(null=True, blank=True)
	legend_height = models.PositiveIntegerField(null=True, blank=True)
	legend_format = models.CharField(max_length=50, null=True, blank=True)
	stylesheet_onlineresource  = models.URLField(verify_exists = False)
	stylesheet_format = models.CharField(max_length=50, null=True, blank=True)
