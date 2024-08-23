from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('favorites/', FavoriteBooksView.as_view(), name='favorites'),
    path('favorites/<int:book_id>/', FavoriteBooksView.as_view(), name='delete_favorite'),
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
]
