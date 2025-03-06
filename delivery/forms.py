from django import forms
from .models import Restaurants, Menu

class ResForm(forms.ModelForm):
    class Meta:
        model = Restaurants
        fields = ['resname','foodcat','rating','img','address']

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['res','item_name','description','price','is_available','category']