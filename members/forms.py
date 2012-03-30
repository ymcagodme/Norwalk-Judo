from django import forms

class AnnounceForm(forms.Form):
    subject = forms.CharField()
    body = forms.CharField( widget=forms.Textarea )
