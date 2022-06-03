from rest_framework import serializers
from product.models import Product, Category, Review, StarredProducts


class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(
        source='owner.email'
    )

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        user = self.context.get('request').user
        if user.is_staff:
            created_product = Product.objects.create(**validated_data)
            return created_product
        else:
            raise serializers.ValidationError('Only manager accounts can create products.')

    def is_starred(self, product):
        user = self.context.get('request').user
        return user.starred.filter(product=product).exists()

    def is_liked(self, product):
        user = self.context.get('request').user
        return user.liked.filter(product=product).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # print('REPR',representation)
        representation['category'] = CategorySerializer(instance.category).data
        representation['review_count'] = instance.reviews.count()
        representation['reviews_detail'] = ReviewSerializer(instance.reviews.all(), many=True).data
        user = self.context.get('request').user
        if user.is_authenticated:
            representation['is_starred'] = self.is_starred(instance.id)
            representation['is_liked'] = self.is_liked(instance.id)
        representation['likes_count'] = instance.likes.count()
        return representation


class StarredProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = StarredProducts
        fields = ('product',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_title'] = Product.objects.get(pk=representation['product']).title
        representation['product_price'] = Product.objects.get(pk=representation['product']).price
        if Product.objects.get(pk=representation['product']).image:
            representation['product_image'] = Product.objects.get(pk=representation['product']).image
        representation['product_availability'] = Product.objects.get(pk=representation['product']).is_available
        # product = representation.pop('product')
        # print('representation------------->', representation)
        return representation


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Review
        fields = ('id', 'text', 'owner', 'product',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = instance.owner.email
        return representation


