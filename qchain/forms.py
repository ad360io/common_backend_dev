from django import forms
from django.forms.extras.widgets import SelectDateWidget
import account.forms
from qchain.models import (RequestForAdv, AD_TYPES, MAX_DIGITS,
DECIMAL_PLACES, GENRE_CHOICES, Adspace)
from django.forms import ModelForm

class DetailForm(forms.Form):
    birthdate = forms.DateField(widget=SelectDateWidget(years=range(1910,
                                                                    1991)))


# DEPRECATED FOR NOW
class WebsiteForm(forms.Form):
    link = forms.URLField()


# DEPRECATED FOR NOW
class AdForm(forms.Form):
    name = forms.CharField(max_length=20)


class RequestForm(forms.Form):
    # name = forms.CharField(max_length=20)

    currency = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(('eqc', 'EQC'), ('xqc', 'XQC')),
        label="Currency")
    # The GENRE_CHOICES is a quick hack. What is possibly better is just
    # defining it as a global variable in models.py and using it from there.
    # This is done for AD_TYPES for now.
    genre = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=GENRE_CHOICES,
        label="Genre")
    adtype = forms.MultipleChoiceField(
                                        required=False,
                                        widget=forms.CheckboxSelectMultiple,
                                        choices=AD_TYPES,
                                        label="Ad type")
    minrate = forms.DecimalField(required=False,
                                 label="Min. rate",
                                 min_value=0, max_digits=MAX_DIGITS,
                                 decimal_places=DECIMAL_PLACES)
    maxrate = forms.DecimalField(required=False,
                                 label="Max. rate", min_value=0,
                                 max_digits=MAX_DIGITS,
                                 decimal_places=DECIMAL_PLACES)

class AdspaceForm(ModelForm):
    class Meta:
        model = Adspace
        exclude = ['publisher']
        # widgets = {
        # 'adtype': forms.MultipleChoiceField(required=False,
        # widget=forms.CheckboxSelectMultiple)
        # }
