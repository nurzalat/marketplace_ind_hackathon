from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, permissions
from product.models import Product, Category, Review, StarredProducts, Likes
from product.serializers import ProductSerializer, CategorySerializer
from product import serializers

from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from product.permissions import IsAuthor


class StandardPaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProductViewSet(ModelViewSet):
    class Meta:
        model = Product
        fields = '__all__'
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    pagination_class = StandardPaginationClass

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        days_count = int(self.request.query_params.get('day', 0))
        if days_count > 0:
            start_date = timezone.now() - timedelta(days=days_count)
            queryset = queryset.filter(created_at__gte=start_date)
        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request, pk=None):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q))
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['GET'], detail=True)
    def reviews(self, request, pk):
        product = self.get_object()
        comments = product.comments.all()
        serializer = serializers.ReviewSerializer(comments, many=True)
        return Response(serializer.data)

    @action(['POST'],detail=True)
    def add_to_starred(self, request, pk):
        product = self.get_object()
        if request.user.starred.filter(product=product).exists():
            return Response('You have already starred this product!', status=status.HTTP_400_BAD_REQUEST)
        StarredProducts.objects.create(product=product, user=request.user)
        return Response('You starred this product!', status=status.HTTP_201_CREATED)

    @action(['POST'], detail=True)
    def remove_from_starred(self, request, pk):
        product = self.get_object()
        if not request.user.starred.filter(product=product).exists():
            return Response('You haven\'t starred this product yet!', status=status.HTTP_400_BAD_REQUEST)
        request.user.starred.filter(product=product).delete()
        return Response('Product successfully removed from your starred product list!',
                        status=status.HTTP_204_NO_CONTENT)

    @action(['POST'], detail=True)
    def add_to_liked(self, request, pk):
        product = self.get_object()
        if request.user != product.owner:
            if request.user.liked.filter(product=product).exists():
                return Response('You have already liked this product!', status=status.HTTP_400_BAD_REQUEST)
            Likes.objects.create(product=product, user=request.user)
            return Response('You liked this product!', status=status.HTTP_201_CREATED)
        else:
            return Response('Owner can\'t like own Products!', status=status.HTTP_403_FORBIDDEN)

    @action(['POST'], detail=True)
    def remove_from_liked(self, request, pk):
        product = self.get_object()
        if not request.user.liked.filter(product=product).exists():
            return Response('You haven\'t liked this product yet!', status=status.HTTP_400_BAD_REQUEST)
        request.user.liked.filter(product=product).delete()
        return Response('Your like has been successfully removed!', status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ('create',):
            return [permissions.IsAuthenticated(),]
        elif self.action in ('update', 'partial_update', 'destroy',):
            return [IsAuthor(),]
        else:
            return [permissions.AllowAny(),]


class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        print(self.request.user)
        return serializer.save(owner=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthor,)


class StarredProductListView(generics.ListAPIView):
    serializer_class = serializers.StarredProductSerializer

    def get_queryset(self):
        user = self.request.user
        return StarredProducts.objects.filter(user=user)
    pagination_class = StandardPaginationClass
