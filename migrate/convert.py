#!/usr/bin/env python

# Convert data from msaccess to mysql

from collections import OrderedDict
import re
import os

# def load_ciudades():
#     ciudades = {}
#     data = open('ciudad.sql', 'r').readlines()
#     for row in data[1:]:
#         id, nombre, prov = split_fields(row.strip())
#         ciudades[id] = (nombre, prov)
#     return ciudades

def load_domicilios_pago():
    dom = {}
    # dom[nombre] = (id, id_ciudad)
    dom['"Capilla San Cayetano"'] = (1,3)
    dom['"Capilla San Paul"'] = (2,2)
    dom['"Capilla San Lorenzo"'] = (3 ,3)
    dom['"Capilla San Francisco"'] = (4 ,3)
    dom['"INCOMPLETO"'] = (5 ,3)
    return dom

class SistAmortizacion:
    def __init__(self):
        self.rows = OrderedDict()

    def convert(self):
        data = open('tSistAmortizacion.txt', 'r').readlines()
        for row in data[1:]:
            id, descripcion = split_fields(row.strip())
            self.rows[id] = descripcion
        
        out = open('amortizacion.sql', 'w')
        out.write('TRUNCATE TABLE amortizacion;\n')
        for id, desc in self.rows.items():
            out.write("INSERT INTO amortizacion VALUES (%s, %s);\n" % (id, desc))
        out.close()

class Actividad:
    def __init__(self):
        self.rows = []

    def convert(self, amortizacion):
        data = open('tActividades.txt', 'r').readlines()
        for row in data[1:]:
            id, nombre, id_amort = split_fields(row.strip())
            self.rows.append((id, nombre, id_amort))

        out = open('actividad.sql', 'w')
        out.write('TRUNCATE TABLE actividad;\n')
        for id, nombre, id_amort in self.rows:
            out.write("INSERT INTO actividad VALUES (%s, %s, %s);\n" % (id, nombre, id_amort))
        out.close()

class Rubro:
    def __init__(self):
        self.rows = OrderedDict()

    def convert(self, actividad):
        data = open('tRubros.txt', 'r').readlines()
        for row in data[1:]:
            id, nombre, id_act = split_fields(row.strip())
            self.rows[id] = (id, nombre, id_act)

        out = open('rubro.sql', 'w')
        out.write('TRUNCATE TABLE rubro;\n')
        for id, nombre, id_act in self.rows.values():
            out.write("INSERT INTO rubro VALUES (%s, %s, %s);\n" % (id, nombre, id_act))
        out.close()

class Asistencia:
    def __init__(self):
        self.rows = OrderedDict()

    def convert(self):
        data = open('tTiposAsistencia.txt', 'r').readlines()
        for row in data[1:]:
            id, desc, coment = split_fields(row.strip())
            self.rows[id] = (desc, coment)

        out = open('asistencia.sql', 'w')
        out.write('TRUNCATE TABLE asistencia;\n')
        for desc, coment in self.rows.values():
            out.write("INSERT INTO asistencia VALUES (%s, %s);\n" % (desc, coment))
        out.close()

class Barrio:
    def __init__(self):
        self.rows = []

    def convert(self, domicilios_pago):
        data = open('tBarrios.txt', 'r').readlines()
        for row in data[1:]:
            id, nombre, ciudad, prov, domic = split_fields(row.strip())
            self.rows.append((id, nombre, domicilios_pago[domic][0]))

        out = open('barrio.sql', 'w')
        out.write('TRUNCATE TABLE barrio;\n')
        for id, nombre, domic_pago in self.rows:
            out.write("INSERT INTO barrio VALUES (%s, %s, %s);\n" % (id, nombre, domic_pago))
        out.close()

class Cartera:
    def __init__(self):
        self.rows = OrderedDict()

    def convert(self):
        data = open('tCarteras.txt', 'r').readlines()
        for row in data[1:]:
            id, nombre = split_fields(row.strip())
            self.rows[id] = nombre

        out = open('cartera.sql', 'w')
        out.write('TRUNCATE TABLE cartera;\n')
        for id, nombre in self.rows.items():
            out.write("INSERT INTO cartera VALUES (%s, %s);\n" % (id, nombre))
        out.close()

class EstadoCredito:
    def __init__(self):
        self.rows = []

    def convert(self):
        data = open('tEstadosCredito.txt', 'r').readlines()
        for row in data[1:]:
            id, desc, cmin, cmax = split_fields(row.strip())
            self.rows.append((id, desc, cmax))

        out = open('estado_credito.sql', 'w')
        out.write('TRUNCATE TABLE estado_credito;\n')
        for id, desc, cmax in self.rows:
            out.write("INSERT INTO estado_credito VALUES (%s, %s, %s);\n" % (id, desc, cmax))
        out.close()

def unquote(field):
    if field[0] == field[-1] == '"':
        return field[1:-1]
    return field

class Beneficiaria:
    estado_civil = { '"soltera"': '1',
                     '"concubina"': '2',
                     '"concubinato"': '2',
                     '"casada"': '3',
                     '"separada"': '4',
                     '"divorciada"': '5',
                     '"viuda"': '6',
                     '\\n': '\\n'
                   }

    def __init__(self):
        self.rows = OrderedDict()

    def convert(self, barrios):
        data = open('tBeneficiarias.txt', 'r').readlines()
        for row in data[1:]:
            fields = split_fields(row.strip())
            fields[12] = self.estado_civil[fields[12].lower()]  # reemplazar estado_civil por su id
            fields = map(lambda x: unquote(x), fields)
            self.rows[fields[0]] = fields

        out = open('beneficiaria.sql', 'w')
        out.write('TRUNCATE TABLE beneficiaria;\n')
        out.write("LOAD DATA LOCAL INFILE '%s/beneficiaria.dat' REPLACE INTO TABLE beneficiaria (id,barrio_id,nombre,apellido,grupo,fecha_alta,activa,fecha_baja,comentarios,dni,fecha_nac,domicilio,estado_civil,telefono);\n" % os.getcwd())
        out.close()
        
        out = open('beneficiaria.dat', 'w')
        for fields in self.rows.values():
            new = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\n".format(*fields)
            out.write(new)
        out.close()

class Credito:
    def __init__(self):
        self.rows = OrderedDict()

    def convert(self, cartera):
        data = open('tCreditos.txt', 'r').readlines()
        for row in data[1:]:
            fields = split_fields(row.strip())
            fields = map(lambda x: unquote(x), fields)
            self.rows[fields[0]] = fields

        out = open('credito.sql', 'w')
        out.write('TRUNCATE TABLE credito;\n')
        out.write("LOAD DATA LOCAL INFILE '%s/credito.dat' REPLACE INTO TABLE credito;\n" % os.getcwd())
        out.close()
        
        out = open('credito.dat', 'w')
        for fields in self.rows.values():
            new = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\n".format(*fields)
            out.write(new)
        out.close()

class Pago:
    def __init__(self):
        self.rows = []

    def convert(self, asistencia):
        data = open('tPagos.txt', 'r').readlines()
        for row in data[1:]:
            fields = split_fields(row.strip())
            fields[3] = asistencia.rows[fields[3]][0]     # reemplazar el id_asistencia por su nombre
            fields = map(lambda x: unquote(x), fields)
            self.rows.append(fields)

        out = open('pago.sql', 'w')
        out.write('TRUNCATE TABLE pago;\n')
        out.write("LOAD DATA LOCAL INFILE '%s/pago.dat' REPLACE INTO TABLE pago (credito_id, monto, fecha, asistencia_codigo);\n" % os.getcwd())
        out.close()
        
        out = open('pago.dat', 'w')
        for fields in self.rows:
            new = "{0}\t{1}\t{2}\t{3}\n".format(*fields)
            out.write(new)
        out.close()

def convert():
    amortizacion = SistAmortizacion()
    amortizacion.convert()

    actividad = Actividad()
    actividad.convert(amortizacion)

    Rubro().convert(actividad)
    asistencia = Asistencia()
    asistencia.convert()

    # provincias = { '1' : 'Buenos Aires' }
    # lo comente porque el archivo existente ya es valido
    # ciudades = load_ciudades()
    domicilios_pago = load_domicilios_pago()

    barrio = Barrio()
    barrio.convert(domicilios_pago)
    
    cartera = Cartera()
    cartera.convert()
    
    EstadoCredito().convert()
    Beneficiaria().convert(barrio)
    Credito().convert(cartera)
    Pago().convert(asistencia)
    
def split_fields(row):
    # http://stackoverflow.com/questions/2785755/how-to-split-but-ignore-separators-in-quoted-strings-in-python
    # separate fields by comma, but not if comma between quotes
    pattern = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')
    return pattern.split(row)[1::2]
    
if __name__ == '__main__':
    convert()
    
