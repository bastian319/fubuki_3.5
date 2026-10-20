from django import forms

from .models import Resena


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['nombre', 'calificacion', 'comentario']
        labels = {
            'nombre': 'Tu nombre',
            'calificacion': 'Calificación',
            'comentario': 'Tu reseña',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '¿Cómo te llamas?',
                'autocomplete': 'name',
            }),
            'calificacion': forms.Select(attrs={'class': 'form-select'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos cómo fue tu experiencia',
            }),
        }
