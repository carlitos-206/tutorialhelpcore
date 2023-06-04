from django.urls import path
from .views import (
    VideoToText
)

urlpatterns = [
    path('to/text/', VideoToText.as_view(), name='VideoToText'),
]