from django import forms

class StudentRegisterForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15)
    college = forms.CharField(max_length=150)
    branch = forms.CharField(max_length=100)
    year_of_passing = forms.IntegerField()
