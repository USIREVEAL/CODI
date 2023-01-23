from django.urls import path

from ..views import *

urlpatterns = [
    path('validation', StatisticsValidationView.as_view(), name='validation statistics'),
    path('prediction', StatisticsPredictionView.as_view(), name='prediction statistics')
]