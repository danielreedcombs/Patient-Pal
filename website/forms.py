from django.contrib.auth.models import User
from django import forms
from website.models import medication
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name',)

class add_medication(forms.ModelForm):

    class Meta:
        model = medication
        fields = ('name', 'dosage',)