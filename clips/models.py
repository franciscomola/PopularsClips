from django.db import models
from django.contrib.auth.models import User  # Si utilizas el sistema de usuarios por defecto de Django

class Streamer(models.Model):
    name = models.CharField(max_length=100)
    twitch_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Clip(models.Model):
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE, related_name='clips')
    title = models.CharField(max_length=255)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación en la base de datos
    twitch_created_at = models.DateTimeField(null=False)  # Asegúrate de que sea `DateTimeField`
    LANGUAGE_CHOICES = [
        ('es', 'Español'),
        ('en', 'Inglés'),
        ('fr', 'Francés'),
        # Agrega más idiomas según sea necesario
    ]
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    from_twitch = models.BooleanField(default=True)  # True si fue extraído automáticamente

    def __str__(self):
        return self.title

class ClipVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clip = models.ForeignKey(Clip, on_delete=models.CASCADE, related_name='votes')
    vote_value = models.IntegerField()  # Puede ser +1 o -1
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'clip')  # Cada usuario solo puede votar una vez por clip

    def __str__(self):
        return f'Vote by {self.user.username} on {self.clip.title}'

class Comment(models.Model):
    clip = models.ForeignKey(Clip, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),  # Mejora en las consultas ordenadas por fecha
        ]

    def __str__(self):
        return f'Comment by {self.user.username} on {self.clip.title}: {self.content[:20]}...'

