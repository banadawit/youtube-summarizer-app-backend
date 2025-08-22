from django.urls import path
from .views import summarize_video

urlpatterns = [
    path('summarize-video/', summarize_video, name='summarize_video'),
]