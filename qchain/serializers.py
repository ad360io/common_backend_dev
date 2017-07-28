from rest_framework import serializers
from qchain.models import Agent, Website, Adspace, AdspaceForm, Ad, Contract, \
Stat, RequestForAdv


class AdspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adspace
        fields = ('publisher', 'website', 'name', 'adtype', 'genre',
        'height', 'width')

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ('ad', 'adspace', 'name', 'start_time', 'end_time', 'active',
        'currency', 'payout')
