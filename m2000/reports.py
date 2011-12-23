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
import model
import settings

def header_image_filename():
    return os.path.join(settings.CAMELOT_MEDIA_ROOT, 'header.jpg')

def spacer(field, width=10):
    if not field:
        return '_' * width
    return field

def fix_decimal_sep(str_num):
    # warning: forzando separador decimal a ','
    tmp = str_num.replace('.', ';')
    tmp = tmp.replace(',', '.')
    tmp = tmp.replace(';', ',')
    return tmp

def money_fmt(value, dec=1):
    # incluir separador de miles y signo de pesos
    fmtstring = '{:,.%df}' % dec
    ret = '$ %s' % fmtstring.format(value)
    return fix_decimal_sep(ret)

def float_fmt(value, dec=2):
    ret = ('%.' + '%df' % dec) % value
    return fix_decimal_sep(ret)

# TODO: rehacer esto con min y max
def fecha_desde():
    return model.Fecha.query.first().fecha

def fecha_hasta():
    return model.Fecha.query.order_by(model.Fecha.fecha.desc()).first().fecha

class ReportePagos(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['credito',
                                     'fecha',
                                     'monto',
                                     'asistencia',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_monto = 0
        for row in iterator:
            linea = Linea(row.credito,
                          row.fecha,
                          money_fmt(row.monto),
                          row.asistencia)
            total_monto += row.monto
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'detalle': detalle,
            'total_monto': money_fmt(total_monto),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('pagos.html')
        yield PrintHtml(t.render(context))

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
            'header_image_filename': header_image_filename(),
            'beneficiaria': '%s %s' % (obj.beneficiaria.nombre, obj.beneficiaria.apellido),
            'dni': spacer(obj.beneficiaria.dni),
            'fecha_nac': spacer(obj.beneficiaria.fecha_nac),
            'estado_civil': spacer(obj.beneficiaria.estado_civil),
            'domicilio': spacer(obj.beneficiaria.domicilio),
            'ciudad': obj.beneficiaria.barrio.domicilio_pago.ciudad.nombre,
            'provincia': obj.beneficiaria.barrio.domicilio_pago.ciudad.provincia.nombre,
            'emprendimiento': obj.rubro.actividad,
            'tasa_interes_mensual': float_fmt(obj.tasa_interes * 100 * 4 / obj.cuotas),  # 4 -> semanas en un mes
            'cuotas': obj.cuotas,
            'cuotas_letras': nro_en_letras(obj.cuotas),
            'monto_prestamo': money_fmt(obj.prestamo, 2),
            'monto_prestamo_letras': nro_en_letras(obj.prestamo),
            'monto_cuota_letras': nro_en_letras(monto_cuota),
            'monto_cuota': money_fmt(monto_cuota, 2),
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
                                     'saldo',
                                     'monto',
                                     'a_favor',
                                     'fecha_efectiva_pago',
                                     'asistencia',
                                     ])
        detalle = []
        fecha = obj.fecha_entrega + datetime.timedelta(weeks=2)
        saldo = deuda_final
        suma_pagos = 0
        for i in range(1, obj.cuotas + 1):
            nro_cuota = i
            pagado_a_fecha = min(cuota_calculada * i, deuda_final)
            saldo = max(saldo - cuota_calculada, 0)

            # obtener el pago para la fecha correspondiente, si es que hubo
            # ATENCION: si hay pagos fuera del periodo comprendido entre la 1 y ultima cuota,
            # no aparecen listados.
            row = model.Pago.query.filter(model.Pago.credito_id == obj.id).filter(model.Pago.fecha >= fecha).filter(model.Pago.fecha < fecha + datetime.timedelta(weeks=1)).first()
            if row:
                suma_pagos += row.monto
                monto = money_fmt(row.monto)
                a_favor = money_fmt(suma_pagos - pagado_a_fecha)
                fecha_efectiva_pago = row.fecha
                asistencia = row.asistencia
            else:
                monto = a_favor = fecha_efectiva_pago = asistencia = None
            linea = Linea(nro_cuota,
                          fecha,
                          money_fmt(pagado_a_fecha),
                          money_fmt(saldo),
                          monto,
                          a_favor,
                          fecha_efectiva_pago,
                          asistencia,
                          )
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

        deuda_final = obj.prestamo * (1 + obj.tasa_interes)
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
            'header_image_filename': header_image_filename(),
            'anio': datetime.date.today().year,
            'comentarios': obj.beneficiaria.comentarios,
            'saldo_anterior': money_fmt(obj.saldo_anterior),
            'monto_cheque': money_fmt(obj.monto_cheque),
            'fecha_entrega': obj.fecha_entrega,
            'deuda_inicial': money_fmt(obj.prestamo),
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

class ReporteIndicadores(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['comentarios',
                                     'barrio',
                                     'beneficiaria',
                                     'nro_credito',
                                     'fecha_entrega',
                                     'fecha_inicio',
                                     'fecha_cancelacion',
                                     'saldo_anterior',
                                     'tasa_interes',
                                     'cartera',
                                     'monto_aporte',
                                     'deuda_total',
                                     'cuotas',
                                     'cuota_calculada',
                                     'cuotas_pagadas',
                                     'cuotas_pagadas_porcent',
                                     'cuotas_teorico',
                                     'cuotas_teorico_porcent',
                                     'diferencia_cuotas',
                                     'saldo',
                                     'monto_pagado',
                                     'monto_teorico',
                                     'diferencia_monto', 
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        for row in iterator:
            linea = Linea(row.comentarios,
                          row.barrio,
                          row.beneficiaria,
                          row.nro_credito,
                          row.fecha_entrega,
                          row.fecha_inicio,
                          row.fecha_cancelacion,
                          money_fmt(row.saldo_anterior),
                          float_fmt(row.tasa_interes),
                          row.cartera,
                          money_fmt(row.monto_aporte),
                          money_fmt(row.deuda_total),
                          row.cuotas,
                          money_fmt(row.cuota_calculada),
                          float_fmt(row.cuotas_pagadas),
                          float_fmt(row.cuotas_pagadas_porcent),
                          money_fmt(row.cuotas_teorico),
                          float_fmt(row.cuotas_teorico_porcent),
                          money_fmt(row.diferencia_cuotas),
                          money_fmt(row.saldo),
                          money_fmt(row.monto_pagado),
                          money_fmt(row.monto_teorico),
                          money_fmt(row.diferencia_monto))
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('indicadores.html')
        yield PrintHtml(t.render(context))


class ReporteRecaudacionMensual(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['barrio',
                                     'cartera',
                                     'tasa_interes',
                                     'recaudacion',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_recaudacion = 0
        for row in iterator:
            linea = Linea(row.barrio,
                          row.cartera,
                          float_fmt(row.tasa_interes),
                          money_fmt(row.recaudacion))
            total_recaudacion += row.recaudacion
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_recaudacion': money_fmt(total_recaudacion),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('recaudacion_mensual.html')
        yield PrintHtml(t.render(context))

class ReporteRecaudacionRealTotal(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['fecha',
                                     'cartera',
                                     'tasa_interes',
                                     'recaudacion',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_recaudacion = 0
        for row in iterator:
            linea = Linea(row.fecha,
                          row.cartera,
                          float_fmt(row.tasa_interes),
                          money_fmt(row.recaudacion))
            total_recaudacion += row.recaudacion
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_recaudacion': money_fmt(total_recaudacion),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('recaudacion_real_total.html')
        yield PrintHtml(t.render(context))

class ReporteRecaudacionPotencialTotal(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['fecha',
                                     'recaudacion',
                                     'recaudacion_potencial',
                                     'porcentaje',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_recaudacion = 0
        total_recaudacion_potencial = 0
        for row in iterator:
            linea = Linea(row.fecha,
                          money_fmt(row.recaudacion),
                          money_fmt(row.recaudacion_potencial),
                          float_fmt(row.porcentaje))
            total_recaudacion += row.recaudacion
            total_recaudacion_potencial += row.recaudacion_potencial
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_recaudacion': money_fmt(total_recaudacion),
            'total_recaudacion_potencial': money_fmt(total_recaudacion_potencial),
            'total_porcentaje': float_fmt(total_recaudacion / total_recaudacion_potencial)
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('recaudacion_potencial_total.html')
        yield PrintHtml(t.render(context))


class ReporteRecaudacionRealTotalPorBarrio(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['fecha',
                                     'barrio',
                                     'recaudacion',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_recaudacion = 0
        for row in iterator:
            linea = Linea(row.fecha,
                          row.barrio,
                          money_fmt(row.recaudacion))
            total_recaudacion += row.recaudacion
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_recaudacion': money_fmt(total_recaudacion),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('recaudacion_real_total_x_barrio.html')
        yield PrintHtml(t.render(context))

class ReporteRecaudacionPotencialTotalPorBarrio(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['fecha',
                                     'barrio',
                                     'recaudacion',
                                     'recaudacion_potencial',
                                     'porcentaje',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_recaudacion = 0
        total_recaudacion_potencial = 0
        for row in iterator:
            linea = Linea(row.fecha,
                          row.barrio,
                          money_fmt(row.recaudacion),
                          money_fmt(row.recaudacion_potencial),
                          float_fmt(row.porcentaje),
                          )
            total_recaudacion += row.recaudacion
            total_recaudacion_potencial += row.recaudacion_potencial
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_recaudacion': money_fmt(total_recaudacion),
            'total_recaudacion_potencial': money_fmt(total_recaudacion_potencial),
            'total_porcentaje': float_fmt(total_recaudacion / total_recaudacion_potencial),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('recaudacion_potencial_total_x_barrio.html')
        yield PrintHtml(t.render(context))

class ReporteChequesEntregados(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['beneficiaria',
                                     'barrio',
                                     'cartera',
                                     'nro_credito',
                                     'fecha_entrega',
                                     'monto_prestamo',
                                     'monto_cheque',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_prestamo = 0
        total_cheque = 0
        for row in iterator:
            linea = Linea(row.beneficiaria,
                          row.barrio,
                          row.cartera,
                          row.nro_credito,
                          row.fecha_entrega,
                          money_fmt(row.monto_prestamo),
                          money_fmt(row.monto_cheque),
                          )
            total_prestamo += row.monto_prestamo
            total_cheque += row.monto_cheque
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_prestamo': money_fmt(total_prestamo),
            'total_cheque': money_fmt(total_cheque),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('cartera_cheques_entregados.html')
        yield PrintHtml(t.render(context))

class ReporteCreditosActivos(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['cdi',
                                     'beneficiaria',
                                     'barrio',
                                     'nro_credito',
                                     'fecha_entrega',
                                     'prestamo',
                                     'saldo',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_prestamo = 0
        total_saldo = 0
        for row in iterator:
            linea = Linea(row.comentarios,
                          row.beneficiaria,
                          row.barrio,
                          row.nro_credito,
                          row.fecha_entrega,
                          money_fmt(row.prestamo),
                          money_fmt(row.saldo),
                          )
            total_prestamo += row.prestamo
            total_saldo += row.saldo
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_prestamo': money_fmt(total_prestamo),
            'total_saldo': money_fmt(total_saldo),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('cartera_creditos_activos.html')
        yield PrintHtml(t.render(context))

class ReportePerdidaPorIncobrable(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['cdi',
                                     'beneficiaria',
                                     'fecha_baja',
                                     'barrio',
                                     'nro_credito',
                                     'fecha_finalizacion',
                                     'comentarios_baja',
                                     'fecha_entrega',
                                     'prestamo',
                                     'deuda_total',
                                     'saldo',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_prestamo = 0
        total_deuda = 0
        total_saldo = 0
        for row in iterator:
            linea = Linea(row.comentarios,
                          row.beneficiaria,
                          row.fecha_baja,
                          row.barrio,
                          row.nro_credito,
                          row.fecha_finalizacion,
                          row.comentarios_baja,
                          row.fecha_entrega,
                          money_fmt(row.prestamo),
                          money_fmt(row.deuda_total),
                          money_fmt(row.saldo),
                          )
            total_prestamo += row.prestamo
            total_deuda += row.deuda_total
            total_saldo += row.saldo
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_prestamo': money_fmt(total_prestamo),
            'total_deuda': money_fmt(total_deuda),
            'total_saldo': money_fmt(total_saldo),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('cartera_perdida_x_incobrable.html')
        yield PrintHtml(t.render(context))

class ReporteCreditosFinalizadosSinSaldar(Action):
    verbose_name = ''
    icon = Icon('tango/16x16/actions/document-print.png')

    def _build_context(self, model_context):
        Linea = namedtuple('Linea', ['cdi',
                                     'beneficiaria',
                                     'barrio',
                                     'nro_credito',
                                     'fecha_finalizacion',
                                     'fecha_entrega',
                                     'prestamo',
                                     'deuda_total',
                                     'saldo',
                                     ])
        iterator = model_context.get_collection()
        detalle = []
        total_prestamo = 0
        total_deuda = 0
        total_saldo = 0
        for row in iterator:
            linea = Linea(row.comentarios,
                          row.beneficiaria,
                          row.barrio,
                          row.nro_credito,
                          row.fecha_finalizacion,
                          row.fecha_entrega,
                          money_fmt(row.prestamo),
                          money_fmt(row.deuda_total),
                          money_fmt(row.saldo),
                          )
            total_prestamo += row.prestamo
            total_deuda += row.deuda_total
            total_saldo += row.saldo
            detalle.append(linea)

        context = { 
            'header_image_filename': header_image_filename(),
            'fecha_desde': fecha_desde(),
            'fecha_hasta': fecha_hasta(),
            'detalle': detalle,
            'total_prestamo': money_fmt(total_prestamo),
            'total_deuda': money_fmt(total_deuda),
            'total_saldo': money_fmt(total_saldo),
            }
        return context

    def model_run(self, model_context):
        context = self._build_context(model_context)
        # mostrar el reporte
        fileloader = PackageLoader('m2000', 'templates')
        env = Environment(loader=fileloader)
        t = env.get_template('cartera_finalizados_sin_saldar.html')
        yield PrintHtml(t.render(context))
