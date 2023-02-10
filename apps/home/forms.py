from django import forms

from .models import CAD_Cliente

class CAD_ClienteForm(forms.ModelForm):
    
    class Meta:
        model = CAD_Cliente
        fields = '__all__'