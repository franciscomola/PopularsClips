# clips/views.py

from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormMixin
from .models import Clip, Streamer, Comment
from django.urls import reverse
from .forms import CommentForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

class ClipListView(ListView):
    model = Clip
    template_name = 'clips/clip_list.html'
    context_object_name = 'clips'

    def get_queryset(self):
        # Captura el streamer_id de los parámetros GET
        streamer_id = self.request.GET.get('streamer')  # Cambiado a GET para URL
        clips = super().get_queryset()

        # Filtra los clips si se ha seleccionado un streamer
        if streamer_id:
            clips = clips.filter(streamer_id=streamer_id)
        
        return clips

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clips_data'] = list(self.get_queryset().values(
            'id', 'title', 'url', 'thumbnail_url', 'twitch_created_at'
        ))
        context['streamers'] = Streamer.objects.all()
        context['ngrok_url'] = settings.NGROK_URL  # Añade NGROK_URL al contexto
        return context

# Vista para mostrar los detalles de un clip y manejar comentarios
class ClipDetailView(FormMixin, DetailView):
    model = Clip  # Modelo que se va a utilizar
    template_name = 'clips/clip_detail.html'  # Plantilla que se va a utilizar
    context_object_name = 'clip'  # Nombre del objeto en el contexto
    form_class = CommentForm  # Formulario que se va a utilizar

    def get_success_url(self):
        # Redirigir a la misma página después de enviar un comentario
        return reverse('clip_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir los comentarios al contexto
        context['comments'] = Comment.objects.filter(clip=self.object)
        context['ngrok_url'] = settings.NGROK_URL  # Añade NGROK_URL al contexto
        context['is_authenticated'] = self.request.user.is_authenticated  # Para saber si el usuario está login
        context['form'] = self.get_form()  # Incluye el formulario en el contexto
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Obtiene el clip actual
        form = self.get_form()  # Obtiene el formulario
        if form.is_valid():
            comment = form.save(commit=False)  # No guardar todavía
            comment.clip = self.object  # Asigna el clip actual
            comment.user = request.user  # Asigna el usuario actual
            comment.save()  # Guarda el comentario en la base de datos
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

# Vista para registro de usuarios
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'clips/register.html'
    success_url = reverse_lazy('login')

class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'clips/user_settings.html'   

