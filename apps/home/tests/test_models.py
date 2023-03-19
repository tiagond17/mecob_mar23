#apps/home/tests/test_models.py

from django.test import TestCase

from ..models import Calculo_Repasse, Dado

class Calculo_Repasse_TestCase(TestCase):
    def setUp(self):
        self.antonio1 = Calculo_Repasse.objects.create(
            taxas=0,
            adi="NÂO",
            vl_pago=257,
            op=0.39
        )
        self.antonio2 = Calculo_Repasse.objects.create(
            taxas=0,
            adi="NÂO",
            vl_pago=257,
            op=0.39
        )
        return super().setUp()
        
    def test_calculo_repasse_valores_calculos(self):
        self.assertNotEqual(self.antonio1, self.antonio2)
        
class Dado_TestCase(TestCase):
    def setUp(self) -> None:
        self.dado = Dado.objects.create(
            
        )
        return super().setUp()
    
    def test_existe(self):
        self.assertTrue(self.dado)