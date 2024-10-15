from django.urls import path
from .views import ClipListView, ClipDetailView

urlpatterns = [
    path('', ClipListView.as_view(), name='clip_list'),  # Lista de clips
    path('clip/<int:pk>/', ClipDetailView.as_view(), name='clip_detail'),  # Detalles del clip
]

