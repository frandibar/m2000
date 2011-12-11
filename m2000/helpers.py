#-------------------------------------------------------------------------------
# Copyright (C) 2011 Francisco Dibar

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-------------------------------------------------------------------------------

import math

def mes_en_letras(mes):
    meses = { 1: 'enero',
              2: 'febrero',
              3: 'marzo',
              4: 'abril',
              5: 'mayo',
              6: 'junio',
              7: 'julio',
              8: 'agosto',
              9: 'septiembre',
              10: 'octubre',
              11: 'noviembre',
              12: 'diciembre' }
    return meses[mes]

UNIDADES = ('',
            'UN ',
            'DOS ',
            'TRES ',
            'CUATRO ',
            'CINCO ',
            'SEIS ',
            'SIETE ',
            'OCHO ',
            'NUEVE ',
            'DIEZ ',
            'ONCE ',
            'DOCE ',
            'TRECE ',
            'CATORCE ',
            'QUINCE ',
            'DIECISEIS ',
            'DIECISIETE ',
            'DIECIOCHO ',
            'DIECINUEVE ',
            'VEINTE ')

DECENAS = ('VENTI',
           'TREINTA ',
           'CUARENTA ',
           'CINCUENTA ',
           'SESENTA ',
           'SETENTA ',
           'OCHENTA ',
           'NOVENTA ',
           'CIEN ')

CENTENAS = ('CIENTO ',
            'DOSCIENTOS ',
            'TRESCIENTOS ',
            'CUATROCIENTOS ',
            'QUINIENTOS ',
            'SEISCIENTOS ',
            'SETECIENTOS ',
            'OCHOCIENTOS ',
            'NOVECIENTOS ')
 
def nro_en_letras(number):
    cents = centavos_en_letras(number)
    num = int(math.modf(number)[1])
    if num == 0:
        ret = 'CERO %s' % cents
        return ret.strip()
    if num == 1:
        ret = 'UNO %s' % cents
        return ret.strip()

    letras = ''
    num_str = str(num) if (type(num) != 'str') else num
    num_str = num_str.zfill(9)
    millones, miles, cientos = num_str[:3], num_str[3:6], num_str[6:]
    if millones:
        if millones == '001':
            letras += 'UN MILLON '
        elif int(millones) > 0:
            letras += '%sMILLONES ' % convertir(millones)
    if miles:
        if miles == '001':
            letras += 'MIL '
        elif int(miles) > 0:
            letras += '%sMIL ' % convertir(miles)
    if cientos:
        if cientos == '001':
            letras += 'UN '
        elif int(cientos) > 0:
            letras += '%s ' % convertir(cientos)
    ret = '%s %s' % (letras, cents)
    return ret.strip()
 
def convertir(num):
    letras = ''
    if num == '100':
        letras = "CIEN "
    elif num[0] != '0':
        letras = CENTENAS[int(num[0])-1]
    k = int(num[1:])
    if k <= 20:
        letras += UNIDADES[k]
    else:
        if (k > 30) and (num[2] != '0'):
            letras += '%sY %s' % (DECENAS[int(num[1])-2], UNIDADES[int(num[2])])
        else:
            letras += '%s%s' % (DECENAS[int(num[1])-2], UNIDADES[int(num[2])])
    return letras
 

def centavos_en_letras(num):
    letras = ''
    cents = math.modf(num)[0] * 100
    if round(cents) > 0:
        letras = 'con %.0f/100' % cents
    return letras
 
