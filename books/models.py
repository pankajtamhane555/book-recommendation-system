from django.db import models
from authors.models import Author


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    published_date = models.DateField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

