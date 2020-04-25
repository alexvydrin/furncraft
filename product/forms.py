from django import forms
from .models import Product


class ProductPassportfileForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('passport_file',)
