from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework_jwt.views import obtain_jwt_token
from django.contrib import admin
import qchain.views


urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r'^marketplace/', qchain.views.marketplace_ser, name='list'), # marketplace
    url(r'^marketplace/(?P<ad_id>[0-9]+)/$', qchain.views.ad_detail, name='ad_detail'), # posting details
    url(r'^pub-dashboard/$', qchain.views.pub_dashboard_ser, name='pub_dashboard'), # publisher dashboard
    # url(r'^pubdash-charts/$', qchain.views.pub_dashboard_charts, name='pubdash-charts'),
    url(r'^dashboard-tables/$', qchain.views.dashboard_tables, name='dashboard-tables'),
    url(r'^pubdash-topstat/$', qchain.views.pub_dashboard_topstat, name='pubdash-topstats'),
    url(r'^dashboard-stats/$', qchain.views.dashboard_stats, name='dashboard-stats'),
    url(r'^display-marketplace/$', qchain.views.display_marketplace, name='display-marketplace'),
    # url(r'^pubdash-charts/$', qchain.views.dashboard_charts, name='pubdash-charts'),
    url(r'^dashboard-charts/', qchain.views.dashboard_charts, name='dashboard-charts'),
    url(r'^testview/(?P<ctype1>[0-2])/$', qchain.views.testview1, name='testview'),
    url(r'^testview/$', qchain.views.testview0, name='testview'),
    url(r'^create-adspace/$', qchain.views.create_adspace, name='create-adspace'),
    #url(r'^create-adsp/$', qchain.views.create_adsp_ser, name='create-adsp'),
    #url(r'^sites/(?P<web_id>[0-9]+)/$', qchain.views.ad_list, name='ad_list'),
#    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^login/$', qchain.views.login3210, name='loginass1234'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
