from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('shortener', views.UrlShortenerViewSet, basename='shortener')

urlpatterns = [
    path('', include(router.urls))
]
