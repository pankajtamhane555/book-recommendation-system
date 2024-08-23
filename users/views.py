from rest_framework import status, generics
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FavoriteBooks, Book
from .serializers import FavoriteBooksSerializer, BookSerializer
from .milvus_db import recommend_books

# Get the User model specified in settings
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    View for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class FavoriteBooksView(APIView):
    """
    View for managing user's favorite books.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve user's favorite books.
        """
        user = request.user
        favorites = FavoriteBooks.objects.filter(user=user)
        serializer = FavoriteBooksSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Add a book to user's favorites.
        """
        user = request.user
         # Check if the user already has 20 favorite books
        if FavoriteBooks.objects.filter(user=user).count() >= 20:
            return Response({"message": "You cannot add more than 20 favorite books."}, status=status.HTTP_400_BAD_REQUEST)
    
        book_id = request.data.get('book_id')
        book = Book.objects.get(id=book_id)
        favorite, created = FavoriteBooks.objects.get_or_create(user=user, book=book)
        serializer = FavoriteBooksSerializer(favorite)
        return Response(serializer.data, status=201)

    def delete(self, request, book_id):
        """
        Remove a book from user's favorites.
        """
        print(book_id)
        user = request.user
        favorite = FavoriteBooks.objects.filter(user=user, book_id=book_id).first()
        if favorite:
            favorite.delete()
            return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Book not found in favorites"}, status=404)

class RecommendationView(APIView):
    """
    View for getting book recommendations based on user's favorites.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get book recommendations for the user.
        """
        user = request.user
        favorite_books = FavoriteBooks.objects.filter(user=user).values_list('book', flat=True)
        recommended_books = recommend_books(favorite_books, 5)
        serializer = BookSerializer(recommended_books, many=True)
        return Response(serializer.data)