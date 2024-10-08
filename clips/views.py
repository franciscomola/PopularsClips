
from django.shortcuts import render
from .models import Clip, Streamer

def clip_list(request):
    """
    Vista que muestra una lista de clips.
    """
    clips = Clip.objects.all()  # Obtener todos los clips de la base de datos
    return render(request, 'clips/clip_list.html', {'clips': clips})

def streamer_clips(request, streamer_id):
    """
    Vista que muestra clips de un streamer específico.
    """
    try:
        streamer = Streamer.objects.get(id=streamer_id)  # Obtener el streamer por su ID
        clips = Clip.objects.filter(streamer=streamer)  # Obtener clips del streamer
    except Streamer.DoesNotExist:
        clips = []  # Si el streamer no existe, no hay clips

    return render(request, 'clips/streamer_clips.html', {'clips': clips, 'streamer': streamer})

