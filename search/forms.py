from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='zoeken', max_length=100)
    tags = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    auteurs = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )