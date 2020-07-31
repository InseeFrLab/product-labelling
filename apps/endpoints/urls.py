from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.endpoints.views import labelingbyhand_author, labelingbyhand_label, labelingbyhand_prediction
from apps.endpoints.views import labeling_author, labeling_groupChoice, labeling_prediction, labeling_summary, labeling_final

urlpatterns = [
    path('labelingbyhand/author/', labelingbyhand_author, name='labelingbyhand_author'),
    path('labelingbyhand/label/', labelingbyhand_label, name='labelingbyhand_label'),
    path('labelingbyhand/prediction/', labelingbyhand_prediction, name='labelingbyhand_prediction'),
    path('labeling/author', labeling_author, name='labeling_author'),
    path('labeling/groupchoice', labeling_groupChoice, name='labeling_groupChoice'),
    path('labeling/prediction', labeling_prediction, name='labeling_prediction'),
    path('labeling/summary', labeling_summary, name='labeling_summary'),
    path('labeling/final', labeling_final, name='labeling_final')
]
