import sys, re
from django.test import TestCase
from django_wms_browser.wmsb.models import WmsEndpoint, OutputFormat, WmsCapability, WmsLayer, WmsLayerField, LayerAttribution, WmsStyle 
from django_wms_browser.wmsb.tests import *

import urllib2

class WmsTest(TestCase):
	def setUp(self):
		# Clean out database between each test
		WmsEndpoint.objects.all().delete()		

	def tearDown(self):
		pass

	def check_parse_save_wms_url(self, url):
		# First Check if the accessing the URL raises Errors
		# and make sure they are caught appropriately
		http_error = False
		url_error = False
		try:
			# If service or request are already in URL, submit as is
			if(url.upper().find('SERVICE') > 0 or url.upper().find('REQUEST') > 0):
				r = urllib2.urlopen(url)
			else:
				# If not, add it with ? or & if ? exists
				# TODO: There is a more pythonic way to do this
				if(url.find('?') > 0):
					r = urllib2.urlopen('%s&service=wms&request=GetCapabilities' % (url))
				else:
					r = urllib2.urlopen('%s?service=wms&request=GetCapabilities' % (url))
		except urllib2.HTTPError:
			http_error = True
		except urllib2.URLError:
			url_error = True

		wmse = WmsEndpoint()
		wms, msg = wmse.parse_save_wms_url(url)
		if(wms == None or msg == None):
			# TODO: Unhandled??
			print "wms or msg = None"
			self.assertTrue(False)
		if(http_error):
			self.assertTrue(re.search('404', msg) != None)
		elif(url_error):
			self.assertTrue(re.search('URLError', msg) != None)
		else:	
			if(re.search('successfully', msg) != None):	
				self.assertTrue(WmsEndpoint.objects.count() == 1)
			else:
				# Other Exception
				# TODO:
				print "No WmsEndpoint objects"
				self.assertTrue(False)
	'''	
	def test_parse_save_wms_layers(self):
		# Check number of saved layers matches wms
		self.assertTrue(False)

	def test_parse_save_styles(self):
		self.assertTrue(False)

	def test_generate_preview_image(self):
		self.assertTrue(False)

	def test_retrieve_layer_attributes(self):
		self.assertTrue(False)

	def test_valid_latlon_bbox(self):
		self.assertTrue(False)

	def test_parse_save_output_formats(self):
		self.assertTrue(False)

	def test_parse_save_capabilities(self):
		self.assertTrue(False)
		
	def test_parse_save_layer_attribution(self):
		self.assertTrue(False)

	def test_parse_save_style(self):
		self.assertTrue(False)
	'''

###############################################
# Note: This is an attempt to do parameterized
# tests with python unittest. This needs to be 
# investigated further and optimized.
# See Here http://bit.ly/2zwSAw 
# ############################################

def _add_wms_tests(name, url):
	def test_parse_url(self):
		self.check_parse_save_wms_url(url)
	setattr(WmsTest, 'test_'+name, test_parse_url)
	test_parse_url.__name__ = 'test_'+name

url_file = open('test_url_list', 'ro')

count = 0
while 1:
        line = url_file.readline()
        if not line:
                break
        _add_wms_tests(str(count), line.strip())
	count += 1
