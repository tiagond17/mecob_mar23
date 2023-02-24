from django import forms

from .models import CadCliente, Calculo_Repasse


class CAD_ClienteForm(forms.ModelForm):

    class Meta:
        model = CadCliente
        fields = '__all__'


class Calculo_RepasseForm(forms.ModelForm):

    class Meta:
        model = Calculo_Repasse
        fields = ("deposito", "taxas", "adi", "me", "op", "vl_pago")
