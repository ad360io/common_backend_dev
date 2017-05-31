from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin
import qchain.views


urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r'^list/$', qchain.views.list, name='list'), # list of all adspaces
    url(r'^list/(?P<ad_id>[0-9]+)/$', qchain.views.ad_detail, name='ad_detail'), # adspace details with ad_id in url
    url(r'^details/', qchain.views.agent_details, name='agent_details'), # agent details (user profile)
    url(r'^create/', qchain.views.create_ad, name='create'), # create new adspace
    url(r'^sites/$', qchain.views.website_list, name='website_list'), # list of websites owned by user
    url(r'^sites/(?P<web_id>[0-9]+)/$', qchain.views.ad_list, name='ad_list'), # list of adspaces on a website with web_id in url
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)