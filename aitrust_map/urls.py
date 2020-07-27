from aitrust_map import views
from django.urls import include, path, re_path
from django.conf.urls import url



urlpatterns = [
    path('', views.azure_map_project, name='azure_map_project'),
  
]
