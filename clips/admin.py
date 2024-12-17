from django.contrib import admin
from .models import Streamer, Clip, ClipVote, Comment

admin.site.register(Streamer)
admin.site.register(Clip)
admin.site.register(ClipVote)
admin.site.register(Comment)

