from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Author
from users.models import User


class AuthorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.author = Author.objects.create(name="J.K. Rowling", biography="Author of Harry Potter", birth_date="1965-07-31")

    def test_get_authors(self):
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_author(self):
        data = {
            "name": "George R.R. Martin",
            "biography": "Author of A Song of Ice and Fire",
            "birth_date": "1948-09-20"
        }
        response = self.client.post(reverse('author-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 2)

    def test_update_author(self):
        data = {
            "name": "J.K. Rowling Updated",
            "biography": "Updated Biography",
            "birth_date": "1965-07-31"
        }
        response = self.client.put(reverse('author-detail', args=[self.author.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author.refresh_from_db()
        self.assertEqual(self.author.name, "J.K. Rowling Updated")

    def test_delete_author(self):
        response = self.client.delete(reverse('author-detail', args=[self.author.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Author.objects.count(), 0)
