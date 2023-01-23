from django.urls import path, include

from ..views import *

urlpatterns = [
    path('predict', PredictView.as_view(), name='predict'),
    path('train', TrainingView.as_view(), name='train'),
    path('validate', ValidateView.as_view(), name='validate'),
    path('convert', ConvertView.as_view(), name='convert'),
    path('statistics/', include('api.urls.statistics'))
]
