from rest_framework import serializers

from product.models import Product
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product', 'quantity',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_title'] = Product.objects.get(pk=representation['product']).title
        representation['product_price'] = Product.objects.get(pk=representation['product']).price
        representation['product_weight'] = Product.objects.get(pk=representation['product']).weight
        if Product.objects.get(pk=representation['product']).image:
            representation['product_image'] = Product.objects.get(pk=representation['product']).image
        representation['product_availability'] = Product.objects.get(pk=representation['product']).is_available
        return representation


class OrderSerializer(serializers.ModelSerializer):
    positions = OrderItemSerializer(write_only=True, many=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'created_at', 'positions', 'status',)

    def create(self, validated_data):
        products = validated_data.pop('positions')
        user = self.context.get('request').user

        order = Order.objects.create(user=user, status='created')
        for prod in products:
            product = prod['product']
            quantity = prod['quantity']
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        positions = OrderItemSerializer(instance.items.all(), many=True).data
        representation['positions'] = positions
        ttl_price = 0
        ttl_weight = 0
        for position in positions:
            ttl_price += position['product_price'] * position['quantity']
            ttl_weight += position['product_weight'] * position['quantity']
        print(ttl_weight, ttl_price)
        representation['total_price'] = ttl_price
        representation['total_weight'] = ttl_weight
        return representation
