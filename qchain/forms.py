from django import forms
from django.forms.extras.widgets import SelectDateWidget

import account.forms

class DetailForm(forms.Form):
    birthdate = forms.DateField(widget=SelectDateWidget(years=range(1910, 1991)))

# DEPRECATED FOR NOW
class WebsiteForm(forms.Form):
    link = forms.URLField()

# DEPRECATED FOR NOW
class AdForm(forms.Form):
    name = forms.CharField(max_length=20)