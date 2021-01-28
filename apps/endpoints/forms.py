from django import forms
from apps.endpoints.models import Author, Label, labellingByHand, labellingDone

class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ('name',)
        labels = {'name': 'Nom ',}

class LabelForm(forms.ModelForm):

    class Meta:
        model = Label
        fields = ('label_in',)
        labels = {'label_in': 'Libellé ',}
        widgets = {'label_in': forms.TextInput(attrs={'placeholder': 'cahier grands carreaux'}),}

class labellingByHandForm(forms.ModelForm):
    class Meta:
        model = labellingByHand
        fields = '__all__'

class labellingForm(forms.ModelForm):
    class Meta:
        model = labellingDone
        fields = '__all__'
