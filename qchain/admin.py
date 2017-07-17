from django.contrib import admin
from .models import (Agent, Website, Adspace, Contract, BaseRequest,
RequestForAdv)

admin.site.register(Agent)
admin.site.register(Website)
admin.site.register(Adspace)
admin.site.register(Contract)
admin.site.register(BaseRequest)
admin.site.register(RequestForAdv)
