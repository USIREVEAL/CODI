"""
codi URL Configuration
"""

from django.urls import path, include

urlpatterns = [
    path('', include('client.urls.urls')),
    path('api/', include('api.urls.urls'))
]
