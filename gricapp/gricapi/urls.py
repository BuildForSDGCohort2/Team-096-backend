from django.conf.urls import url, include
from gricapi.views import produce_details

app_name = "api"
urlpatterns = [
    url(r'^catalog/produce/(?P<pk>[0-9]+)/$',
        produce_details, name="produce-detail")
]
