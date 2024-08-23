from rest_framework import serializers
from .models import Book, Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'biography', 'birth_date']


class BookSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    author_detail = AuthorSerializer(source='author', read_only=True)  # Nesting AuthorSerializer for read operations

    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'published_date', 'author', 'author_detail']
