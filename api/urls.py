
from django.urls import path
from .views import RecommendView, RecommendTopView

urlpatterns = [
    path('recommend/', RecommendView.as_view(), name='recommend'),
    path("recommend/top/", RecommendTopView.as_view(), name="recommend-top"),
]
