from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.endpoints.views import post_author, post_libelle, post_listprediction, post_labellisation
from apps.endpoints.views import post_author_labellisation, post_groupChoice_labellisation, post_bilanlabellisation, post_final

urlpatterns = [
    path('post/author/', post_author, name='post_author'),
    path('post/prediction/', post_listprediction, name='post_listprediction'),
    path('post/libelle/', post_libelle, name='post_libelle'),
    path('labellisation', post_labellisation, name='post_labellisation'),
    path('author', post_author_labellisation, name='post_author_labellisation'),
    path('groupchoice', post_groupChoice_labellisation, name='post_groupChoice_labellisation'),
    path('bilan', post_bilanlabellisation, name='post_bilanlabellisation'),
    path('final', post_final, name='post_final')
]
