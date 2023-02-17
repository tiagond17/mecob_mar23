from django import forms

from .models import CAD_Cliente, Calculo_Repasse


class CAD_ClienteForm(forms.ModelForm):

    class Meta:
        model = CAD_Cliente
        fields = '__all__'


class Calculo_RepasseForm(forms.ModelForm):

    class Meta:
        model = Calculo_Repasse
        fields = ("deposito", "taxas", "adi", "me", "op", "vl_pago")
