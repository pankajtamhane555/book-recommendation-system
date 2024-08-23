from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FavoriteBooks
from books.serializers import BookSerializer
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class FavoriteBooksSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = FavoriteBooks
        fields = ['id', 'book', 'created_at']