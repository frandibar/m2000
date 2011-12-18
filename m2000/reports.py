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

import datetime
import os
from collections import namedtuple

from jinja import Environment, PackageLoader
from pkg_resources import resource_filename
from camelot.admin.action.base import Action
from camelot.admin.entity_admin import EntityAdmin
from camelot.view.action_steps import PrintHtml #, WordJinjaTemplate
from camelot.view.art import Icon

from helpers import nro_en_letras, mes_en_letras

def spacer(field):
    if not field:
        return '_' * 10 
    return field

def money_fmt(value):
    return '$ %.1f' % value

def float_fmt(value, dec=2):
    return ('%.' + '%df' % dec) % value

class ContratoMutuo(Action):
    verbose_name = 'Contrato Mutuo'
    icon = Icon('tango/16x16/actions/document-print.png')

    def model_run(self, model_context):
        obj = model_context.get_object()

        monto_cuota = obj.monto_cheque * (1 + obj.tasa_interes) / obj.cuotas
        # la 1era semana no paga cuota. Recien a los 14 dias de recibido el cheque tiene que pagar la primer cuota.
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
            'tasa_interes': 'TODO',
            'cuotas': obj.cuotas,
            'cuotas_letras': nro_en_letras(obj.cuotas),
            'monto_prestamo': obj.prestamo,
            'monto_prestamo_letras': nro_en_letras(obj.prestamo),
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
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('contrato_mutuo.html')
        yield PrintHtml(t.render(context))
        # TODO probar en windows
        # yield WordJinjaTemplate(t.render(context))

class PlanillaPagos(Action):
    verbose_name = 'Planilla de Pagos'
    icon = Icon('tango/16x16/actions/document-print.png')

    def _detalle_planilla(self, obj, cuota_calculada, deuda_final):
        Linea = namedtuple('Linea', ['nro_cuota',
                                     'fecha',
                                     'pagado_a_fecha',
                                     'saldo'])
        detalle = []
        fecha = obj.fecha_entrega + datetime.timedelta(weeks=2)
        saldo = deuda_final
        for i in range(1, obj.cuotas + 1):
            nro_cuota = i
            pagado_a_fecha = min(cuota_calculada * i, deuda_final)
            saldo = max(saldo - cuota_calculada, 0)
            linea = Linea(nro_cuota,
                          fecha,
                          money_fmt(pagado_a_fecha),
                          money_fmt(saldo))
            detalle.append(linea)
            fecha += datetime.timedelta(weeks=1)
        return detalle

    # comentado porque aun no esta en uso
    # def _detalle_planilla_aleman(self, obj):
    #     Linea = namedtuple('Linea', ['nro_cuota',
    #                                  'fecha_cuota',
    #                                  'saldo_deudor',
    #                                  'cuota_m2000',
    #                                  'cuota_habitat',
    #                                  'cuota_total',
    #                                  'pagado_a_fecha',
    #                                  'saldo_restante'])
    #     detalle = []
    #     fecha_cuota = obj.fecha_entrega + datetime.timedelta(weeks=2)
    #     cuota_capital = obj.prestamo / obj.cuotas
    #     saldo_deudor = obj.prestamo - cuota_capital
    #     cuota_interes = obj.prestamo * obj.tasa_interes / 24
    #     cuota_habitat = obj.gastos_arq / obj.cuotas
    #     pagado_a_fecha = cuota_capital + cuota_interes + cuota_habitat
    #     saldo_restante = obj.deuda_total - pagado_a_fecha
    #     for i in range(1, obj.cuotas + 1):
    #         nro_cuota = i
    #         cuota_m2000 = cuota_capital + cuota_interes
    #         cuota_total = cuota_m2000 + cuota_habitat
    #         linea = Linea(nro_cuota,
    #                       fecha_cuota,
    #                       money_fmt(saldo_deudor),
    #                       money_fmt(cuota_m2000),
    #                       money_fmt(cuota_habitat),
    #                       money_fmt(cuota_total),
    #                       money_fmt(pagado_a_fecha),
    #                       money_fmt(saldo_restante))
    #         detalle.append(linea)
    #         fecha_cuota += datetime.timedelta(weeks=2)
    #         saldo_deudor -= cuota_capital
    #         cuota_interes = saldo_deudor * obj.tasa_interes / 24
    #         saldo_restante -= cuota_total
    #         pagado_a_fecha += cuota_total
    #     return detalle

    def model_run(self, model_context):
        obj = model_context.get_object()

        deuda_inicial = obj.monto_cheque + obj.saldo_anterior
        deuda_final = deuda_inicial + deuda_inicial * .0487
        redondeo = 0.5
        cuota_sin_redondeo = round(deuda_final / obj.cuotas)
        if deuda_final - (obj.cuotas - 1) * cuota_sin_redondeo > cuota_sin_redondeo:
            cuota_calculada = cuota_sin_redondeo + redondeo
        else:
            cuota_calculada = cuota_sin_redondeo
        monto_ultima_cuota = deuda_final - cuota_calculada * (obj.cuotas - 1)

        # generar la planilla
        detalle = []
        if obj.para_construccion:
            detalle = [] #self._detalle_planilla_aleman(obj)
            template = 'planilla_pagos_aleman.html'
        else:
            detalle = self._detalle_planilla(obj, cuota_calculada, deuda_final)
            template = 'planilla_pagos.html'

        context = {
            'anio': datetime.date.today().year,
            'comentarios': obj.beneficiaria.comentarios,
            'saldo_anterior': money_fmt(obj.saldo_anterior),
            'monto_cheque': money_fmt(obj.monto_cheque),
            'fecha_entrega': obj.fecha_entrega,
            'deuda_inicial': money_fmt(deuda_inicial),
            'deuda_final': money_fmt(deuda_final),
            'nro_credito': obj.nro_credito,
            'cuotas': obj.cuotas,
            'cuota_calculada': money_fmt(cuota_calculada),
            'monto_ultima_cuota': money_fmt(monto_ultima_cuota),
            'beneficiaria': '%s %s' % (obj.beneficiaria.nombre, obj.beneficiaria.apellido),
            'dni': obj.beneficiaria.dni,
            'telefono': obj.beneficiaria.telefono,
            'domicilio': obj.beneficiaria.domicilio,
            'grupo': obj.beneficiaria.grupo,
            'detalle': detalle,

        }
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template(template)
        yield PrintHtml(t.render(context))
