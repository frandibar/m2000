#!/bin/bash

set -x 

insert() {
    mysql --user=root --password=root m2000 < "$1"
}

# execute() {
#     mysql --user=root --password=root m2000 -e "$1"
# }

insert "provincia.sql"
insert "ciudad.sql"
insert "domicilio_pago.sql"
insert "amortizacion.sql"
insert "actividad.sql"
insert "rubro.sql"
insert "asistencia.sql"
insert "barrio.sql"
insert "cartera.sql"
insert "estado_credito.sql"
insert "beneficiaria.sql"
insert "credito.sql"
insert "pago.sql"
