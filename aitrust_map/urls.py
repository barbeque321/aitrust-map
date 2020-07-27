from aitrust_map import views
from django.urls import include, path, re_path
from django.conf.urls import url



urlpatterns = [
    path('', views.azure_map_project, name='azure_map_project'),
    url(r'^process_loc/$', views.process_loc, name='process_loc'),
  
]
