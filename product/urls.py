from django.urls import path, include
from product import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', views.CategoryView.as_view()),
    path('reviews/', views.ReviewListCreateView.as_view()),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view()),
    path('starred/', views.StarredProductListView.as_view()),
]
