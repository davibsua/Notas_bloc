from django import forms

class User(forms.Form): 
    user = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)