# clips/views.py

from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from .models import Clip, Streamer, Comment
from django.urls import reverse
from .forms import CommentForm

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
        return context

