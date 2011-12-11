import datetime
import os
from collections import namedtuple

from jinja import Environment, FileSystemLoader
from pkg_resources import resource_filename
from camelot.admin.action.base import Action
from camelot.admin.entity_admin import EntityAdmin
from camelot.view.action_steps import PrintHtml
from camelot.view.art import Icon

from helpers import nro_en_letras, mes_en_letras

def spacer(field):
    if not field:
        return '_' * 10 
    return field

def money_fmt(value):
    return '$ %.2f' % value

def float_fmt(value, dec=2):
    return ('%.' + '%df' % dec) % value

class ContratoMutuo(Action):
    verbose_name = 'Contrato Mutuo'
    icon = Icon('tango/16x16/actions/document-print.png')

    def model_run(self, model_context):
        fileloader = FileSystemLoader('templates')
        env = Environment(loader=fileloader)
        obj = model_context.get_object()
        monto_cuota = obj.monto_cheque * (1 + obj.tasa_interes) / obj.cuotas
        fecha_1ra_cuota = obj.fecha_entrega + datetime.timedelta(weeks=2)
        fecha_ultima_cuota = obj.fecha_entrega + datetime.timedelta(weeks=obj.cuotas + 1)
        context = {
            'beneficiaria': '%s %s' % (obj.beneficiaria.nombre, obj.beneficiaria.apellido),
            'dni': spacer(obj.beneficiaria.dni),
            'fecha_nac': spacer(obj.beneficiaria.fecha_nac),
            'estado_civil': spacer(obj.beneficiaria.estado_civil),
            'domicilio': spacer(obj.beneficiaria.domicilio),
            'ciudad': obj.beneficiaria.barrio.domicilio_pago.ciudad.nombre,
            'provincia': obj.beneficiaria.barrio.domicilio_pago.ciudad.provincia.nombre,
            'emprendimiento': obj.rubro.actividad,
            'cuotas': obj.cuotas,
            'cuotas_letras': nro_en_letras(obj.cuotas),
            'monto_prestamo': obj.monto_prestamo,
            'monto_prestamo_letras': nro_en_letras(obj.monto_prestamo),
            'monto_cuota_letras': nro_en_letras(monto_cuota),
            'monto_cuota': monto_cuota,
            'dia_1ra_cuota': fecha_1ra_cuota.day,
            'mes_1ra_cuota_letras': mes_en_letras(fecha_1ra_cuota.month),
            'anio_1ra_cuota': fecha_1ra_cuota.year,
            'dia_ultima_cuota': fecha_ultima_cuota.day,
            'mes_ultima_cuota_letras': mes_en_letras(fecha_ultima_cuota.month),
            'anio_ultima_cuota': fecha_ultima_cuota.year,
            'domicilio_pago': obj.beneficiaria.barrio.domicilio_pago.nombre,
        }
        t = env.get_template('contrato_mutuo.html')
        yield PrintHtml(t.render(context))


class PlanillaPagos(Action):
    verbose_name = 'Planilla de Pagos'
    icon = Icon('tango/16x16/actions/document-print.png')

    def _detalle_planilla(self, obj):
        Linea = namedtuple('Linea', ['porcentaje', 
                                     'nro_cuota',
                                     'fecha',
                                     'aporte',
                                     'capital',
                                     'saldo_semana',
                                     'interes_pagado',
                                     'pagado_a_fecha',
                                     'saldo'])
        detalle = []
        cuota_calculada = obj.deuda_total / obj.cuotas
        aporte = obj.prestamo * obj.tasa_interes / obj.cuotas
        capital = cuota_calculada - aporte
        saldo_semana = obj.prestamo
        interes_pagado = aporte
        fecha = obj.fecha_entrega + datetime.timedelta(weeks=2)
        saldo = obj.deuda_total
        for i in range(1, obj.cuotas + 1):
            porcentaje = i * 100 / obj.cuotas
            nro_cuota = i
            saldo_semana -= capital
            pagado_a_fecha = cuota_calculada * i
            saldo -= cuota_calculada
            linea = Linea(float_fmt(porcentaje, 1),
                          nro_cuota,
                          fecha,
                          money_fmt(aporte),
                          money_fmt(capital),
                          money_fmt(saldo_semana),
                          float_fmt(interes_pagado),
                          money_fmt(pagado_a_fecha),
                          money_fmt(saldo))
            detalle.append(linea)
            fecha += datetime.timedelta(weeks=1)
            interes_pagado += aporte
        return detalle

    def _detalle_planilla_aleman(self, obj):
        Linea = namedtuple('Linea', ['nro_cuota',
                                     'fecha_cuota',
                                     'saldo_deudor',
                                     'cuota_m2000',
                                     'cuota_habitat',
                                     'cuota_total',
                                     'pagado_a_fecha',
                                     'saldo_restante'])
        detalle = []
        fecha_cuota = obj.fecha_entrega + datetime.timedelta(weeks=2)
        cuota_capital = obj.prestamo / obj.cuotas
        saldo_deudor = obj.prestamo - cuota_capital
        cuota_interes = obj.prestamo * obj.tasa_interes / 24
        cuota_habitat = obj.gastos_arq / obj.cuotas
        pagado_a_fecha = cuota_capital + cuota_interes + cuota_habitat
        saldo_restante = obj.deuda_total - pagado_a_fecha
        for i in range(1, obj.cuotas + 1):
            nro_cuota = i
            cuota_m2000 = cuota_capital + cuota_interes
            cuota_total = cuota_m2000 + cuota_habitat
            linea = Linea(nro_cuota,
                          fecha_cuota,
                          money_fmt(saldo_deudor),
                          money_fmt(cuota_m2000),
                          money_fmt(cuota_habitat),
                          money_fmt(cuota_total),
                          money_fmt(pagado_a_fecha),
                          money_fmt(saldo_restante))
            detalle.append(linea)
            fecha_cuota += datetime.timedelta(weeks=2)
            saldo_deudor -= cuota_capital
            cuota_interes = saldo_deudor * obj.tasa_interes / 24
            saldo_restante -= cuota_total
            pagado_a_fecha += cuota_total
        return detalle

    def model_run(self, model_context):
        obj = model_context.get_object()
        detalle = []
        # generar la planilla
        if obj.para_construccion:
            detalle = self._detalle_planilla_aleman(obj)
            template = 'planilla_pagos_aleman.html'
        else:
            detalle = self._detalle_planilla(obj)
            template = 'planilla_pagos.html'

        # mostrar el reporte
        fileloader = FileSystemLoader('templates')
        env = Environment(loader=fileloader)
        context = {
            'anio': datetime.date.today().year,
            'comentarios': obj.beneficiaria.comentarios,
            'saldo_anterior': money_fmt(obj.saldo_anterior),
            'monto_cheque': money_fmt(obj.monto_cheque),
            'fecha_entrega': obj.fecha_entrega,
            'deuda_inicial': 'TODO',
            'deuda_final': 'TODO',
            'nro_credito': obj.nro_credito,
            'cuotas': obj.cuotas,
            'cuota_calculada': 'TODO',
            'monto_ultima_cuota': 'TODO',
            'beneficiaria': '%s %s' % (obj.beneficiaria.nombre, obj.beneficiaria.apellido),
            'dni': obj.beneficiaria.dni,
            'telefono': obj.beneficiaria.telefono,
            'domicilio': obj.beneficiaria.domicilio,
            'grupo': obj.beneficiaria.grupo,
            'detalle': detalle,

        }
        t = env.get_template(template)
        yield PrintHtml(t.render(context))

