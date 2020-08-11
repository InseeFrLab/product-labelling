from django import forms
from apps.endpoints.models import Author, Label, labellingByHand, labellingDone

class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ('name',)

class LabelForm(forms.ModelForm):

    class Meta:
        model = Label
        fields = ('label_in',)

class labellingByHandForm(forms.ModelForm):
    class Meta:
        model = labellingByHand
        fields = '__all__'

class labellingForm(forms.ModelForm):
    class Meta:
        model = labellingDone
        fields = '__all__'
