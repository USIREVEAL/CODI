from django.urls import path

from ..views import *


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('annotate', Annotate.as_view(), name='annotate'),
    path('statistics/<str:operation>', Stats.as_view(), name='stats'),
]
