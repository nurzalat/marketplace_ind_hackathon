import generics as generics
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import serializers
from .models import Cart
from .permissions import IsOwner


class CartViewSet(ModelViewSet):
    class Meta:
        model = Cart
        fields = '__all__'
    queryset = Cart.objects.all()
    permission_classes = [IsOwner, ]
    serializer_class = serializers.CartSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        # only authenticated user can create a post
        if self.action in ('create',):
            return [permissions.IsAuthenticated()]
        # only owner of post can update/delete post/s
        else:
            return [IsOwner()]

    def destroy(self, request, *args, **kwargs):
        # instance = self.get_object()
        instance = Cart.objects.get(product=kwargs['pk'], user=request.user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    def list(self, request, *args, **kwargs):
        user = request.user
        products = Cart.objects.filter(user=user)
        serializer = serializers.CartSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
