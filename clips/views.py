
from django.shortcuts import render
from .models import Clip, Streamer
from django.shortcuts import render
from .models import Clip, Streamer

def clip_list(request):
    # Filtrado de clips por streamer
    streamer_id = request.GET.get('streamer')
    if streamer_id:
        clips = Clip.objects.filter(streamer_id=streamer_id)
    else:
        clips = Clip.objects.all()

    streamers = Streamer.objects.all()  # Obtener todos los streamers

    return render(request, 'clips/clip_list.html', {'clips': clips, 'streamers': streamers, 'request': request})

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

