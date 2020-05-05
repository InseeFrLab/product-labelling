from django import forms
from apps.endpoints.models import Author, Post, LabellisationManuelle 

class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ('name',)

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('libelle',)

class PredictionForm(forms.ModelForm):
    class Meta:
        model = LabellisationManuelle
        fields = ('libelle', 'label', 'prediction',)
