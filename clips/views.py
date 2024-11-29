#views.py
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormMixin
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .models import Clip, Streamer, Comment, ClipVote
from .forms import CommentForm
from django.db.models import Sum
from django.contrib.auth.models import User
from rest_framework import generics
from .models import Clip
from .serializers import ClipSerializer, ClipSerializer, StreamerSerializer
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter

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


class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = 'clips/user_profile.html'
    context_object_name = 'profile_user'
    model = User
    
    def get_object(self):
        user_id = self.kwargs.get('pk')  # Obtiene el ID del usuario de la URL
        return User.objects.get(pk=user_id)  # Devuelve el usuario correspondiente

class RankingView(ListView):
    model = Clip
    template_name = 'clips/clip_ranking.html'
    context_object_name = 'clips'

    def get_queryset(self):
        return Clip.objects.annotate(vote_score=Sum('votes__vote_value')).order_by('-vote_score')



from rest_framework.permissions import AllowAny

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