from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^map/$', views.map, name='map'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^pop_radius/$', views.pop_radius, name='pop_radius'),
	url(r'^directions/$', views.directions, name='directions'),
    url(r'^get_summary_for_added_point/$', views.get_summary_for_added_point, name='get_summary_for_added_point'),
]
