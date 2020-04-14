from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from apps.endpoints.views import EndpointViewSet
from apps.endpoints.views import MLAlgorithmViewSet
from apps.endpoints.views import MLAlgorithmStatusViewSet
from apps.endpoints.views import MLRequestViewSet
from apps.endpoints.views import PredictView

from django.urls import path 
from apps.endpoints.views import post_author, post_new, post_list

router = DefaultRouter(trailing_slash=False)
router.register(r"endpoints", EndpointViewSet, basename="endpoints")
router.register(r"mlalgorithms", MLAlgorithmViewSet, basename="mlalgorithms")
router.register(r"mlalgorithmstatuses", MLAlgorithmStatusViewSet, basename="mlalgorithmstatuses")
router.register(r"mlrequests", MLRequestViewSet, basename="mlrequests")

urlpatterns = [
    url(r"^api/", include(router.urls)),
    url(
        r"^api/(?P<endpoint_name>.+)/predict$", PredictView.as_view(), name="predict"
    ),
    #path('post/list', PostListView.as_view(), name='post_list'),
    #path('post/<int:pk>/', post_list, name='post_list'),
    path('post/author/', post_author, name='post_author'),
    path('post/list/', post_list, name='post_list'),
    path('post/new/', post_new, name='post_new'),
    #path('post/edit/', post_edit, name='post_edit'),
    #path('post/<int:pk>/edit/', post_edit, name='post_edit'),
]
