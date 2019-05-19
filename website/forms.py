from django.contrib.auth.models import User
from django import forms
from website.models import medication
# form for new users to fill out.
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name',)

#  form for the add medications functionality
class add_medication(forms.ModelForm):

    class Meta:
        model = medication
        fields = ('name', 'dosage',)