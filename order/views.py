from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from rest_framework import generics, permissions, status as st, status
from rest_framework.decorators import permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# from account.send_email import send_payment_notification
from account.tasks import send_payment_notif
from cart.permissions import IsOwner, IsNotAdmin
from marketeer import settings
from . import serializers
from .models import Order


class CreateOrderView(generics.CreateAPIView):
    serializer_class = serializers.OrderSerializer
    permission_classes = (permissions.IsAuthenticated, )


class OrderActivationView(APIView):
    def get(self, request, activation_code):
        try:
            order = Order.objects.get(activation_code=activation_code)
            order.activation_code = ''
            order.status = 'created'
            order.save()
            return Response({'msg': 'Order confirmed'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'msg': 'Link expired'}, status=status.HTTP_400_BAD_REQUEST)


class UserOrderList(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner, )

    def get(self, request):
        user = request.user
        orders = user.order_to_user.all()
        # orders = Order.objects.filter(user=user)
        serializer = serializers.OrderSerializer(orders, many=True).data
        return Response(serializer)


class UpdateOrderStatusView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def patch(self, request, pk):
        status = request.data['status']
        if status not in ['in_progress', 'closed']:
            return Response('Invalid status', status=st.HTTP_400_BAD_REQUEST)
        order = Order.objects.get(pk=pk)
        order.status = status
        order.save()
        serializer = serializers.OrderSerializer(order).data
        return Response(serializer, status=st.HTTP_206_PARTIAL_CONTENT)


def process_payment(request, pk):
    order = Order.objects.get(pk=pk)
    order_items = order.items.all()
    total_price = 0.0
    for item in order_items:
        total_price += item.product.price * item.quantity
    order_id = pk
    order = get_object_or_404(Order, id=order_id)
    order_detail = {'email': 'test@mail.com', 'address': 'Kyrgyzstan, Bishkek, 3-19', 'postal_code': '720001',
                    'name': 'order', 'order': order}
    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % total_price, # .quantize(Decimal('.01')),
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    request.session['order_id'] = pk
    request.session.modified = True
    return render(request, 'order/process_payment.html', {'order': order_detail, 'form': form})


@csrf_exempt
def payment_done(request):
    order_id = request.session.get('order_id')
    order = Order.objects.get(pk=order_id)
    # send_payment_notification(order.user, order_id)
    send_payment_notif.delay(order.user.email, order_id)
    order.status = 'paid'
    order.save()
    return render(request, 'order/payment_done.html')


@csrf_exempt
def payment_canceled(request):
    return render(request, 'order/payment_cancelled.html')
