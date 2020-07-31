from django import forms
from apps.endpoints.models import Author, Label, LabelingByHand, LabelingDone

class AuthorForm(forms.ModelForm):

    class Meta:
        model = Author
        fields = ('name',)

class LabelForm(forms.ModelForm):

    class Meta:
        model = Label
        fields = ('label_in',)

class LabelingByHandForm(forms.ModelForm):
    class Meta:
        model = LabelingByHand
        fields = '__all__'

class LabelingForm(forms.ModelForm):
    class Meta:
        model = LabelingDone
        fields = '__all__'
