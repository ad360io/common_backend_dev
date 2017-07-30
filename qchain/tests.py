from qchain.models import Adspace
# from qchain.models import Contract, RequestForAdv
from qchain.serializers import AdspaceSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
## Not functional now
# def func1():
#     print("func1")

adsp1 = Adspace.objects.get(pk=1)
ser = AdspaceSerializer()
print(repr(ser))
ser = AdspaceSerializer(adsp1)
print(ser.data)
