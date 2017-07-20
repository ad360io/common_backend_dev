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
    url(r'^details/$', qchain.views.agent_details, name='agent_details'), # agent profile
    url(r'^marketplace/', qchain.views.list, name='list'), # marketplace
    url(r'^marketplace/(?P<ad_id>[0-9]+)/$', qchain.views.ad_detail, name='ad_detail'), # posting details
    #url(r'^new-adspace/', qchain.views.create_ad, name='create_ad'),
    #url(r'^new-website/', qchain.views.create_ad, name='create'),
    url(r'^pub-dashboard/$', qchain.views.pub_dashboard, name='pub_dashboard'), # publisher dashboard
    url(r'^pub-dashboard/(?P<ctype1>[0-2])/$', qchain.views.pub_dashboard, name='pub_dashboard2'), # publisher dashboard
    url(r'^pub-dashboard/(?P<ctype1>[0-2])/(?P<ctype2>[0-2])/$', qchain.views.pub_dashboard, name='pub_dashboard2'), # publisher dashboard
    url(r'^testview/(?P<ctype1>[0-2])/$', qchain.views.testview, name='testview')
    #url(r'^sites/(?P<web_id>[0-9]+)/$', qchain.views.ad_list, name='ad_list'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
