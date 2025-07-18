from django.urls import path
from .views import (
    AddPropertyView,
    SearchPropertyView,
    RecommendView,
    RegisterView,
    LoginView,
    SearchHistoryView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('search-history/', SearchHistoryView.as_view(), name='search-history'),
    path('add-property/', AddPropertyView.as_view(), name='add-property'),
    path('search/', SearchPropertyView.as_view(), name='search'),
    path('recommend/', RecommendView.as_view(), name='recommend'),
]
