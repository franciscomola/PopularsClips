from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import (
    ClipListView, ClipDetailView, RankingView, RegisterView, 
    UserSettingsView, UserProfileView, ClipVoteView, edit_comment, delete_comment, 
    ClipList, ClipDetail, StreamerList, ContactUsView, FAQView, AddClipView, DeleteClipView, DeleteAccountView
)

urlpatterns = [
    # Rutas para HTML
    path('', ClipListView.as_view(), name='clip_list'),
    path('clip/<int:pk>/', ClipDetailView.as_view(), name='clip_detail'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(template_name='clips/registration/logout.html'), name='logout'),
    path('user/settings/', UserSettingsView.as_view(), name='user_settings'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    path('profile/delete/', DeleteAccountView.as_view(), name='delete_account'),  # Nueva entrada para eliminar cuenta
    path('clip/<int:pk>/vote/', ClipVoteView.as_view(), name='clip_vote'),
    path('comment/<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('ranking/', RankingView.as_view(), name='clip_ranking'),
    path('contact/', ContactUsView.as_view(), name='contact_us'),  
    path('faq/', FAQView.as_view(), name='faq'), 
    path('add_clip/', AddClipView.as_view(), name='add_clip'), 
    path('clips/delete/<int:pk>/', DeleteClipView.as_view(), name='delete_clip'),



    # Rutas para la API REST
    path('api/clips/', ClipList.as_view(), name='api_clips'),
    path('api/clips/<int:pk>/', ClipDetail.as_view(), name='api_clip_detail'),
    path('api/streamers/', StreamerList.as_view(), name='api_streamers'),  # Nueva ruta para listar streamers
]