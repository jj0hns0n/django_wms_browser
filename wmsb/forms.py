from django import forms

class RegisterWmsEndpointForm(forms.Form):
	new_url = forms.CharField(max_length=1000)
