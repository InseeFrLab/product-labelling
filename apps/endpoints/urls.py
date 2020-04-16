from django.conf.urls import url, include
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.endpoints.views import post_author, post_new, post_list

urlpatterns = [
    path('post/author/', post_author, name='post_author'),
    path('post/list/', post_list, name='post_list'),
    path('post/new/', post_new, name='post_new'),
]
