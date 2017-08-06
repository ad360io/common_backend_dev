from rest_framework import serializers
from qchain.models import Agent, Website, Adspace, Ad, Contract, \
Stat, RequestForAdv
from qchain.forms import AdspaceForm

class AdspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adspace
        fields = ('publisher', 'website', 'name', 'adtype', 'genre',
        'height', 'width')

# class AdspaceFormSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdspaceForm
#         fields = "__all__"

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = "__all__"

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ('ad', 'adspace', 'name', 'start_time', 'end_time', 'active',
        'currency', 'payout')

class RequestForAdvSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestForAdv
        fields = "__all__"
