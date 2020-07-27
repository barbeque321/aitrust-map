from django.shortcuts import render

# Create your views here.
def azure_map_project(request):
    return render(request, 'aitrust_map.html', {})