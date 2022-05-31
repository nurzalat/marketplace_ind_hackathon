from rest_framework import serializers

from .models import Cart
from product.models import Product


class CartSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(
        source='user.username'
    )

    class Meta:
        model = Cart
        fields = ('user', 'product', 'quantity',)

    def create(self, validated_data):
        print('validated_data: ', validated_data)
        # request = self.context.get('request')
        item = Cart.objects.filter(product=validated_data['product'], user=validated_data['user'])
        if not item:
            created_order = Cart.objects.create(**validated_data)
            return created_order
        else:
            raise serializers.ValidationError('Item already in cart!')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product = Product.objects.get(pk=representation['product'])
        representation['product'] = product.title
        user = self.context.get('request').user
        representation['user'] = str(user)
        return representation
