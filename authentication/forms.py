from django import forms
from django.contrib.auth.password_validation import validate_password
class AuthForm(forms.Form):
    name = forms.CharField( label = "name",required=False)
    password = forms.CharField(label = "password", required=False,widget=forms.PasswordInput)

class RegForm(forms.Form):
    name = forms.CharField( label = "name",required=False)
    password1 = forms.CharField(label = "password", required=False,widget=forms.PasswordInput)
    password2 = forms.CharField(label = "password", required=False,widget=forms.PasswordInput)
    def validate(self, value):
        super().validate(value)
        validate_password(value.password1)
        if not password1 == password2:
            raise forms.ValidationError("password dont match")