from aitrust_map import views
from django.urls import include, path, re_path
from django.conf.urls import url



urlpatterns = [
    path('', views.azure_map_project, name='azure_map_project'),
    url(r'^process_loc/$', views.process_loc, name='process_loc'),
    url(r'^process_loc2/$', views.process_loc2, name='process_loc2'),
  	url(r'^draw_polygon/$', views.draw_polygon, name='draw_polygon'),
  	url(r'^draw_polygon_better/$', views.draw_polygon_better, name='draw_polygon_better'),
  	url(r'^search_for_airports/$', views.search_for_airports, name='search_for_airports'),
]
