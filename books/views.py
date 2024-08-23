from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer
from django.db.models import Q
from users.milvus_db import add_book_to_milvus, delete_book_from_milvus

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        author_query = self.request.query_params.get('author', None)
        title_query = self.request.query_params.get('title', None)
 
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__name__icontains=search_query)
            )

        if author_query:
            queryset = queryset.filter(author__name__icontains=author_query)

        if title_query:
            queryset = queryset.filter(title__icontains=title_query)

        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        add_book_to_milvus(instance)


    def perform_destroy(self, instance):
        delete_book_from_milvus(instance)
        instance.delete()