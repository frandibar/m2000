#!/usr/bin/env python
import unittest
import sys
sys.path.append('../')

from m2000.helpers import nro_en_letras, centavos_en_letras

class TestNroEnLetras(unittest.TestCase):
    def test_nro_en_letras_valid_params(self):
        self.assertEqual(nro_en_letras(0), 'CERO')
        self.assertEqual(nro_en_letras(1), 'UNO')
        self.assertEqual(nro_en_letras(2), 'DOS')
        self.assertEqual(nro_en_letras(3), 'TRES')
        self.assertEqual(nro_en_letras(4), 'CUATRO')
        self.assertEqual(nro_en_letras(5), 'CINCO')
        self.assertEqual(nro_en_letras(6), 'SEIS')
        self.assertEqual(nro_en_letras(7), 'SIETE')
        self.assertEqual(nro_en_letras(8), 'OCHO')
        self.assertEqual(nro_en_letras(9), 'NUEVE')
        self.assertEqual(nro_en_letras(10), 'DIEZ')
        self.assertEqual(nro_en_letras(11), 'ONCE')
        self.assertEqual(nro_en_letras(12), 'DOCE')
        self.assertEqual(nro_en_letras(13), 'TRECE')
        self.assertEqual(nro_en_letras(14), 'CATORCE')
        self.assertEqual(nro_en_letras(15), 'QUINCE')
        self.assertEqual(nro_en_letras(16), 'DIECISEIS')
        self.assertEqual(nro_en_letras(17), 'DIECISIETE')
        self.assertEqual(nro_en_letras(18), 'DIECIOCHO')
        self.assertEqual(nro_en_letras(19), 'DIECINUEVE')
        self.assertEqual(nro_en_letras(20), 'VEINTE')
        # TODO agregar mas tests

    def test_nro_en_letras_with_cents(self):
        self.assertEqual(nro_en_letras(0.2), 'CERO con 20/100')
        self.assertEqual(nro_en_letras(1.2), 'UNO con 20/100')

    def test_centavos_en_letras(self):
        self.assertEqual(centavos_en_letras(12.34), 'con 34/100')
        self.assertEqual(centavos_en_letras(12.01), 'con 1/100')
        self.assertEqual(centavos_en_letras(12.001), '')
        self.assertEqual(centavos_en_letras(12.005), 'con 1/100')
        self.assertEqual(centavos_en_letras(12.999), 'con 100/100')
        self.assertEqual(centavos_en_letras(12.99), 'con 99/100')

if __name__ == '__main__':
    unittest.main()
