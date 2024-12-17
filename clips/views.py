#views.py
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin, FormView
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import requests
import re
from .models import Clip, Streamer, Comment, ClipVote
from .forms import CommentForm, AddClipForm
from .serializers import ClipSerializer, StreamerSerializer
from rest_framework.permissions import AllowAny


class ClipListView(ListView):
    model = Clip
    template_name = 'clips/clip_list.html'
    context_object_name = 'clips'

    def get_queryset(self):
        streamer_id = self.request.GET.get('streamer')
        order_by = self.request.GET.get('order_by', 'date')  # 'date' es el valor predeterminado
        
        # Obtener todos los clips
        clips = super().get_queryset()

        # Filtro por streamer si se pasa el parámetro
        if streamer_id:
            clips = clips.filter(streamer_id=streamer_id)
        
        # Ordenar según el parámetro `order_by`
        if order_by == 'popularity':
            clips = clips.annotate(vote_score=Sum('votes__vote_value')).order_by('-vote_score')
        elif order_by == 'language':
            clips = clips.order_by('streamer__language')  # Ordenar por idioma
        else:
            clips = clips.order_by('-twitch_created_at')  # Ordenar por fecha de subida

        return clips

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ranking: obtener los primeros 3 clips más populares sin afectar el filtro
        ranking_clips = Clip.objects.annotate(vote_score=Sum('votes__vote_value')).order_by('-vote_score')[:3]

        # Pasar tanto los clips del ranking como los clips ordenados según el filtro
        context['clips_data'] = list(self.get_queryset().values('id', 'title', 'url', 'thumbnail_url', 'twitch_created_at'))
        context['ranking_clips'] = ranking_clips
        context['streamers'] = Streamer.objects.all()
        context['ngrok_url'] = settings.NGROK_URL
        return context



class ClipDetailView(FormMixin, DetailView):
    model = Clip
    template_name = 'clips/clip_detail.html'
    context_object_name = 'clip'
    form_class = CommentForm

    def get_success_url(self):
        return reverse('clip_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(clip=self.object).order_by('-created_at')
        context['ngrok_url'] = settings.NGROK_URL
        context['is_authenticated'] = self.request.user.is_authenticated
        context['form'] = self.get_form()
        context['vote_count'] = self.object.votes.aggregate(total=Sum('vote_value'))['total'] or 0
        
        # Verifica si el usuario ha votado
        if self.request.user.is_authenticated:
            user_vote = ClipVote.objects.filter(user=self.request.user, clip=self.object).first()
            context['user_vote'] = user_vote.vote_value if user_vote else None  # Almacena el valor del voto si existe
        else:
            context['user_vote'] = None  # Usuario no autenticado

        # Añadir permiso de eliminación del clip
        context['can_delete_clip'] = self.request.user.is_authenticated and (
            self.request.user == self.object.uploaded_by or self.request.user.is_staff)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.clip = self.object
            comment.user = request.user
            comment.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)



def edit_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)

        # Verificar si el usuario es el autor del comentario
        if comment.user == request.user:
            new_text = request.POST.get('text', '')
            comment.text = new_text
            comment.save()
            return JsonResponse({'success': True, 'comment_text': comment.text})
        
        return JsonResponse({'success': False, 'error': 'No tienes permiso para editar este comentario.'})

def delete_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)

        # Verificar si el usuario es el autor del comentario
        if comment.user == request.user:
            comment.delete()
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'No tienes permiso para eliminar este comentario.'})


class ClipVoteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        clip = get_object_or_404(Clip, pk=pk)
        existing_vote = ClipVote.objects.filter(user=request.user, clip=clip).first()
        
        if existing_vote:
            # Eliminar el voto
            existing_vote.delete()
            # Calcular el nuevo conteo de votos
            vote_count = clip.votes.aggregate(total=Sum('vote_value')).get('total', 0)  # Usar get para evitar KeyError
            user_vote = None  # El usuario ya no vota
        else:
            # Crear un nuevo voto
            ClipVote.objects.create(user=request.user, clip=clip, vote_value=1)
            # Calcular el nuevo conteo de votos
            vote_count = clip.votes.aggregate(total=Sum('vote_value')).get('total', 1)  # Usar get para evitar KeyError
            user_vote = 1  # El usuario ha votado

        return JsonResponse({'vote_count': vote_count, 'user_vote': user_vote})



class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'clips/register.html'
    success_url = reverse_lazy('login')

class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'clips/user_settings.html'

class ContactUsView(TemplateView):
    template_name = 'clips/contact_us.html'


class UserProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'clips/user_profile.html'
    context_object_name = 'profile_user'
    model = User
    form_class = UserChangeForm  # Formulario para editar detalles básicos del perfil

    def get_object(self):
        user_id = self.kwargs.get('pk')  # Obtiene el ID del usuario de la URL
        user = User.objects.get(pk=user_id)  # Devuelve el usuario correspondiente
        if user != self.request.user:
            return None  # No permite editar perfiles ajenos
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadimos el formulario de cambio de contraseña solo si es el usuario correcto
        context['password_change_form'] = PasswordChangeForm(self.request.user)
        return context

    def form_valid(self, form):
        # Antes de guardar los cambios, revisamos si hay cambios sensibles
        if 'is_staff' in form.changed_data:
            if not self.request.user.is_staff:  # Solo si es el admin puede cambiar el campo is_staff
                form.cleaned_data['is_staff'] = False  # Restablece el valor a False para impedir el cambio
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if 'password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('user_profile', pk=request.user.pk)  # Redirige al perfil después de cambiar la contraseña
        else:
            return super().post(request, *args, **kwargs)

#Borrar cuenta

class DeleteAccountView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Si el usuario está logueado, mostramos el perfil
        if request.user == self.request.user:
            return redirect('user_profile', pk=request.user.pk)  # Redirige al perfil del usuario
        else:
            messages.error(request, "No tienes permiso para eliminar esta cuenta.")
            return redirect('user_profile', pk=request.user.pk)

    def post(self, request, *args, **kwargs):
        """Lógica para eliminar la cuenta del usuario"""
        if request.user == self.request.user:
            request.user.delete()  # Eliminar usuario
            messages.success(request, "Tu cuenta ha sido eliminada exitosamente.")
            return redirect('clip_list')  # Retorna una respuesta exitosa
        else:
            messages.error(request, "No tienes permiso para eliminar esta cuenta.")
            return redirect('user_profile')  # Respuesta de error


class RankingView(ListView):
    model = Clip
    template_name = 'clips/clip_ranking.html'
    context_object_name = 'clips'
    paginate_by = 10  # Mostrar 10 clips por página

    def get_queryset(self):
        # Consulta para obtener clips ordenados por su puntuación de votos
        return Clip.objects.annotate(vote_score=Sum('votes__vote_value')).order_by('-vote_score')


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "¡Has cerrado sesión exitosamente!")
        return super().dispatch(request, *args, **kwargs)



class ClipList(generics.ListCreateAPIView):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer
    permission_classes = [AllowAny]

class ClipDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer
    permission_classes = [AllowAny]

class StreamerList(generics.ListAPIView):
    queryset = Streamer.objects.all()
    serializer_class = StreamerSerializer
    permission_classes = [AllowAny]

class ClipList(generics.ListAPIView):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['language', 'streamer__id']  # Filtrar por idioma o streamer
    ordering_fields = ['twitch_created_at', 'title']  # Permitir ordenar

    def get_queryset(self):
        # Filtro personalizado: por título
        queryset = super().get_queryset()
        title = self.request.GET.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset



class FAQView(TemplateView):
    template_name = 'clips/faq.html'


#añadir clips de usuarios

class AddClipView(LoginRequiredMixin, FormView):
    template_name = 'clips/add_clip.html'
    form_class = AddClipForm
    success_url = reverse_lazy('clip_list')  # Redirige a la lista de clips después de añadir
    login_url = '/login/'  # URL para redirigir a usuarios no autenticados

    def form_valid(self, form):
        url = form.cleaned_data['url']
        clip_id = self.extract_clip_id_from_url(url)

        if not clip_id:
            messages.error(self.request, "No se pudo extraer el ID del clip de la URL proporcionada.")
            return redirect('add_clip')

        # Llamada a la API de Twitch para obtener detalles del clip
        clip_data = self.fetch_clip_data(clip_id)
        if not clip_data:
            messages.error(self.request, "No se pudo obtener información del clip de Twitch.")
            return redirect('add_clip')

        # Guardar en la base de datos
        self.save_clip_data(clip_data, url)
        messages.success(self.request, "¡Clip añadido exitosamente!")
        return super().form_valid(form)

    def extract_clip_id_from_url(self, url):
        """Extrae el ID del clip de la URL de Twitch."""
        match = re.search(r"clip/([a-zA-Z0-9_-]+)", url)
        return match.group(1) if match else None

    def fetch_clip_data(self, clip_id):
        """Llama a la API de Twitch para obtener datos del clip."""
        access_token = self.get_twitch_access_token()
        headers = {
            'Client-ID': settings.TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(f"https://api.twitch.tv/helix/clips?id={clip_id}", headers=headers)
        if response.status_code == 200 and response.json().get('data'):
            return response.json()['data'][0]
        return None

    def get_twitch_access_token(self):
        """Obtiene un token de acceso para la API de Twitch."""
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            data={
                'client_id': settings.TWITCH_CLIENT_ID,
                'client_secret': settings.TWITCH_CLIENT_SECRET,
                'grant_type': 'client_credentials',
            }
        )
        return response.json().get('access_token')

    def save_clip_data(self, clip_data, url):
        """Guarda los datos del clip en la base de datos con la URL en formato embed."""
        clip_id = self.extract_clip_id_from_url(url)
        if not clip_id:
            return

        embed_url = f"https://clips.twitch.tv/embed?clip={clip_id}&parent=popularclips.duckdns.org"
        streamer, created = Streamer.objects.get_or_create(
            twitch_id=clip_data['broadcaster_id'],
            defaults={'name': clip_data['broadcaster_name']}
        )

        Clip.objects.create(
            streamer=streamer,
            title=clip_data['title'],
            url=embed_url,
            thumbnail_url=clip_data['thumbnail_url'],
            twitch_created_at=clip_data['created_at'],
            language=clip_data['language'],
            from_twitch=True,
            created_at=timezone.now(),
            uploaded_by=self.request.user,  # Usuario autenticado
        )

#Borrar clips 


class DeleteClipView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Clip
    template_name = 'clips/confirm_delete.html'  # Plantilla de confirmación
    success_url = reverse_lazy('clip_list')  # Redirige a la lista de clips después de eliminar
    login_url = '/login/'  # URL para redirigir a usuarios no autenticados

    def test_func(self):
        """Verifica si el usuario tiene permiso para eliminar el clip."""
        clip = self.get_object()
        # El usuario puede eliminar si es el propietario o un administrador
        return self.request.user == clip.uploaded_by or self.request.user.is_superuser

    def handle_no_permission(self):
        """Maneja el caso donde el usuario no tiene permiso."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "No tienes permiso para eliminar este clip.")
        return redirect('clip_list')

    def delete(self, request, *args, **kwargs):
        """Sobrescribe el método delete para añadir mensajes de éxito."""
        clip = self.get_object()
        messages.success(request, f"El clip '{clip.title}' ha sido eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)
