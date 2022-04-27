# youbee_main/home/forms.py

# System libraries


# Third-party libraries


# Django modules
from django import forms

# Django apps

# Current app modules


class ContactForm(forms.Form):
    email = forms.CharField(required=True)
    firstname = forms.CharField(max_length=150, required=True)
    lastname = forms.CharField(max_length=150, required=True)
    subject = forms.CharField(max_length=150, required=True)
    message = forms.CharField(widget=forms.Textarea(), required=True)
    copy_to = forms.BooleanField(required=False)
