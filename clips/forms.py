from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Añade tu comentario',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',  # Clase Bootstrap para estilizar el campo
                'rows': 3,  # Número de líneas visibles en el textarea
                'placeholder': 'Escribe tu comentario aquí...',
                'style': 'resize: none;',  # Evita que el textarea sea redimensionable
            }),
        }

