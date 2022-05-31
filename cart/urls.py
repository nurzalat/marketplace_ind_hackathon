from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('orders', views.CartViewSet, basename='Basket')

urlpatterns = [
    path('', include(router.urls)),
]
