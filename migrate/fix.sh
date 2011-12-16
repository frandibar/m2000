#!/bin/bash

sed -i -f fix.sed tBeneficiarias.txt
sed -i -f fix.sed tCreditos.txt
sed -i -f fix.sed tPagos.txt

# beneficiarias
sed -i 's/Seprada/Separada/g' tBeneficiarias.txt
sed -i 's/"Casada","Alexis Carriel 2776"/"Alexis Carriel 2776","Casada"/g' tBeneficiarias.txt
sed -i 's/Juntada/Concubina/g' tBeneficiarias.txt
sed -i 's/Soltera - Separada/Separada/g' tBeneficiarias.txt
sed -i 's/Soltera \x96 Concubina/Concubina/g' tBeneficiarias.txt

# creditos
sed -i 's/$/,0/g' tCreditos.txt