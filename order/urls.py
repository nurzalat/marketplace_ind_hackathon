from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateOrderView.as_view()),
    path('activate/<uuid:activation_code>', views.OrderActivationView.as_view()),
    path('own/', views.UserOrderList.as_view()),
    path('upd/<int:pk>/', views.UpdateOrderStatusView.as_view()),
    path('process-payment/<int:pk>/', views.process_payment, name='process_payment'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_canceled, name='payment_cancelled'),
]
