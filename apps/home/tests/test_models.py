#apps/home/tests/test_models.py

from django.test import TestCase

from ..models import Calculo_Repasse

class Calculo_RepasseTestCase(TestCase):
    def setUp(self):
        antonio1 = Calculo_Repasse.objects.create(
            taxas=0,
            adi="NÂO",
            vl_pago=257,
            op=0.39
        )
        antonio2 = Calculo_Repasse.objects.create(
            taxas=0,
            adi="NÂO",
            vl_pago=257,
            op=0.39
        )
        
    def test_calculo_repasse_valores_calculos(self):
        self.assertNotEqual(self.antonio1, self.antonio2)