from django.contrib.auth.models import AbstractUser
from django.db import models

from books.models import Book

class User(AbstractUser):
    # Extend the default user model if needed
    pass



class FavoriteBooks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a user can favorite a book only once
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"