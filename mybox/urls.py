"""
URL settings for Tunel
@author: LP
"""
from django.urls import path

from mybox.views import *
# from . import views

# app_name = 'mybox'

urlpatterns = [
    path('chart/<int:id>/<str:gte>/<str:lte>/', chart_data),
]