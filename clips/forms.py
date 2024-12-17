from django import forms
from .models import Comment, Clip

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # Solo incluimos el campo de texto del comentario
        labels = {
            'text': 'Añade tu comentario',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu comentario aquí...'}),
        }

class AddClipForm(forms.Form):
    url = forms.URLField(label="URL del Clip de Twitch", required=True)

    def clean_url(self):
        url = self.cleaned_data['url']
        if "twitch.tv" not in url:
            raise forms.ValidationError("La URL debe ser un clip válido de Twitch.")
        return url