from django.urls import path
from .views import ClipListView, ClipDetailView, RegisterView, UserSettingsView

urlpatterns = [
    path('', ClipListView.as_view(), name='clip_list'),  # Lista de clips
    path('clip/<int:pk>/', ClipDetailView.as_view(), name='clip_detail'),  # Detalles del clip
    path('register/', RegisterView.as_view(), name='register'),
    path('user/settings/', UserSettingsView.as_view(), name='user_settings'),
]


