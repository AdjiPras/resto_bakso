from django import forms
from .models import MenuBakso

class MenuBaksoForm(forms.ModelForm):
    class Meta:
        model = MenuBakso
        fields = '__all__'