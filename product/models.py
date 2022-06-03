from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self): return f'{self.name}'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    owner = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='products')
    title = models.CharField(max_length=40)
    description = models.TextField()
    price = models.IntegerField()
    weight = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/', blank=True)
    is_available = models.BooleanField()

    class Meta:
        ordering = ('id',)

    def __str__(self): return f'{self.title} : {self.price}сом'


class Likes(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked')

    class Meta:
        verbose_name = 'like'
        verbose_name_plural = 'likes'
        unique_together = ['product', 'user']


class Review(models.Model):
    owner = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f'{self.owner} -> {self.product} -> {self.text}'


class StarredProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='starred')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='starred')

    class Meta:
        verbose_name = 'Starred Product'
        verbose_name_plural = 'Starred Products'
        unique_together = ['product', 'user']

    def __str__(self): return f'{self.product}'
