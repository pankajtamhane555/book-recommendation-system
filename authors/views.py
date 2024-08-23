from rest_framework import viewsets
from .models import Author
from .serializers import AuthorSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
