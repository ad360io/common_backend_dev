from django.contrib import admin

from .models import Agent, Website, Adspace

admin.site.register(Agent)
admin.site.register(Website)
admin.site.register(Adspace)