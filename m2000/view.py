# -*- coding: latin-1 -*-

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

from camelot.admin.action.base import Action
from camelot.admin.entity_admin import EntityAdmin
from camelot.admin.not_editable_admin import notEditableAdmin
from camelot.admin.object_admin import ObjectAdmin
from camelot.admin.validator.object_validator import ObjectValidator
from camelot.view.action_steps import ChangeObject, FlushSession, UpdateProgress, Refresh
from camelot.view.art import ColorScheme, Icon
from camelot.view.controls.delegates import DateDelegate, FloatDelegate, CurrencyDelegate, IntegerDelegate
from camelot.view.filters import ComboBoxFilter, ValidDateFilter
from elixir import Entity, Field, using_options
from sqlalchemy import Unicode, Date, Integer, Float
from sqlalchemy.orm import mapper
from sqlalchemy.sql import select, func, and_

from camelot.model import metadata
__metadata__ = metadata

from model import Beneficiaria, Cartera, Credito, Barrio, Pago
import model
import reports

# esta clase corresponde a un VIEW
class Indicadores(Entity):
    using_options(tablename='102_indicadores', autoload=True, allowcoloverride=True)
    # override columns since a primary must be defined
    beneficiaria_id = Field(Integer, primary_key=True)
    nro_credito = Field(Integer, primary_key=True)                         

    class Admin(EntityAdmin):
        verbose_name = 'Indicadores'
        verbose_name_plural = 'Indicadores'
        list_display = [
            'comentarios',
            'barrio',
            'beneficiaria',
            'nro_credito',
            'fecha_entrega',
            'fecha_inicio',
            'fecha_cancelacion',
            'saldo_anterior',
            'capital',
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
            'estado',
            ]

        list_filter = [ComboBoxFilter('barrio')]
        list_columns_frozen = 1
        list_action = None
        list_actions = [reports.ReporteIndicadores()]
        field_attributes = dict(fecha_entrega = dict(name = 'F.Entrega',
                                                     delegate = DateDelegate),
                                fecha_inicio = dict(name = 'F.Inicio',
                                                    delegate = DateDelegate),
                                fecha_cancelacion = dict(name = u'F.Cancelación',
                                                         delegate = DateDelegate),
                                saldo_anterior = dict(delegate = CurrencyDelegate,
                                                      prefix = '$'),
                                capital = dict(delegate = CurrencyDelegate,
                                               prefix = '$'),
                                tasa_interes = dict(name = u'Tasa Interés',
                                                    minimal_column_width = 15,
                                                    delegate = FloatDelegate),
                                monto_aporte = dict(delegate = CurrencyDelegate,
                                                    prefix = '$'),
                                deuda_total = dict(delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                cuotas = dict(delegate = IntegerDelegate),
                                cuota_calculada = dict(minimal_column_width = 15,
                                                       delegate = CurrencyDelegate,
                                                       prefix = '$'),
                                cuotas_pagadas = dict(minimal_column_width = 15,
                                                      delegate = FloatDelegate),
                                cuotas_pagadas_porcent = dict(delegate = FloatDelegate,
                                                              name = u'%'),
                                cuotas_teorico = dict(name = u'Cuotas teórico',
                                                      delegate = FloatDelegate),
                                cuotas_teorico_porcent = dict(delegate = FloatDelegate,
                                                              name = u'%'),
                                diferencia_cuotas = dict(minimal_column_width = 15,
                                                         delegate = FloatDelegate),
                                saldo = dict(delegate = CurrencyDelegate,
                                             prefix = '$'),
                                monto_pagado = dict(delegate = CurrencyDelegate,
                                                    prefix = '$'),
                                monto_teorico = dict(name = u'Monto teórico',
                                                     delegate = CurrencyDelegate,
                                                     prefix = '$'),
                                diferencia_monto = dict(minimal_column_width = 15,
                                                        delegate = CurrencyDelegate,
                                                        prefix = '$'),
                                beneficiaria = dict(minimal_column_width = 25),
                                )

    # Admin = notEditableAdmin(Admin, actions=True)
    
# esta clase corresponde a un VIEW
class RecaudacionMensual(Entity):
    using_options(tablename='700_recaudacion_x_cartera', autoload=True, allowcoloverride=True)
    cartera = Field(Unicode(200), primary_key=True)
    tasa_interes = Field(Float, primary_key=True)
    recaudacion = Field(Float, primary_key=True)
    barrio = Field(Unicode(200), primary_key=True)
    
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Mensual'
        verbose_name_plural = u'Mensual'
        list_display = ['barrio',
                        'cartera',
                        'tasa_interes',
                        'recaudacion',
                        ]
        
        list_filter = [ComboBoxFilter('barrio'),
                       ComboBoxFilter('cartera'),
                       ]
        list_action = None
        field_attributes = dict(tasa_interes = dict(name = u'Tasa Interés',
                                                    minimal_column_width = 15,
                                                    delegate = FloatDelegate),
                                recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'))
        list_actions = [reports.ReporteRecaudacionMensual()]

    # Admin = notEditableAdmin(Admin, actions=True)

# esta clase corresponde a un VIEW
class RecaudacionRealTotal(Entity):
    using_options(tablename='recaudacion_real_total', autoload=True, allowcoloverride=True)
    fecha = Field(Date, primary_key=True)
    cartera = Field(Unicode(200), primary_key=True)
    tasa_interes = Field(Float, primary_key=True)

    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Real Total'
        verbose_name_plural = u'Real Total'
        list_display = ['fecha',
                        'cartera',
                        'tasa_interes',
                        'recaudacion',
                        ]
        list_actions = [reports.ReporteRecaudacionRealTotal()]
        list_filter = [ValidDateFilter('fecha', 'fecha', 'Fecha', default=lambda:''),
                       ComboBoxFilter('cartera'),
                       ]
        list_action = None
        field_attributes = dict(recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                fecha = dict(delegate = DateDelegate),
                                tasa_interes = dict(name = u'Tasa Interés',
                                                    delegate = FloatDelegate)
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

# esta clase corresponde a un VIEW
class RecaudacionRealTotalPorBarrio(Entity):
    using_options(tablename='recaudacion_real_x_barrio', autoload=True, allowcoloverride=True)
    fecha = Field(Date, primary_key=True)
    barrio = Field(Unicode(200), primary_key=True)
    recaudacion = Field(Float)
    
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Real Total por Barrio'
        verbose_name_plural = u'Real Total por Barrio'
        list_display = ['fecha',
                        'barrio',
                        'recaudacion',
                        ]
        
        list_filter = [ValidDateFilter('fecha', 'fecha', 'Fecha', default=lambda:''),
                       ComboBoxFilter('barrio'),
                       ]
        list_action = None
        list_actions = [reports.ReporteRecaudacionRealTotalPorBarrio()]
        field_attributes = dict(recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                fecha = dict(delegate = DateDelegate),
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

# esta clase corresponde a un VIEW
class RecaudacionPotencialTotalPorBarrio(Entity):
    using_options(tablename='702_recaudacion_potencial_x_barrio', autoload=True, allowcoloverride=True)
    fecha = Field(Date, primary_key=True)
    barrio = Field(Unicode(200), primary_key=True)
    recaudacion = Field(Float)
    recaudacion_potencial = Field(Float)
    porcentaje = Field(Float)
    
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Potencial Total por Barrio'
        verbose_name_plural = u'Potencial Total por Barrio'
        list_display = ['fecha',
                        'barrio',
                        'recaudacion',
                        'recaudacion_potencial',
                        'porcentaje',
                        ]
        
        list_filter = [ValidDateFilter('fecha', 'fecha', 'Fecha', default=lambda:''),
                       ComboBoxFilter('barrio'),
                       ]
        list_action = None
        list_actions = [reports.ReporteRecaudacionPotencialTotalPorBarrio()]
        field_attributes = dict(recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                recaudacion_potencial = dict(name = 'Rec. Potencial',
                                                             delegate = CurrencyDelegate,
                                                             prefix = '$'),
                                porcentaje = dict(name = '%',
                                                  delegate = FloatDelegate),
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

# esta clase corresponde a un VIEW
class RecaudacionPotencialTotal(Entity):
    using_options(tablename='702_recaudacion_potencial', autoload=True, allowcoloverride=True)
    fecha = Field(Date, primary_key=True)
    recaudacion = Field(Float, primary_key=True)
    recaudacion_potencial = Field(Float, primary_key=True)
    porcentaje = Field(Float, primary_key=True)
    
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Potencial Total'
        verbose_name_plural = u'Potencial Total'
        list_display = ['fecha',
                        'recaudacion',
                        'recaudacion_potencial',
                        'porcentaje',
                        ]
        
        list_filter = [ValidDateFilter('fecha', 'fecha', 'Fecha', default=lambda:''),
                       ]
        list_actions = [reports.ReporteRecaudacionPotencialTotal()]
        list_action = None
        field_attributes = dict(recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                recaudacion_potencial = dict(name = 'Rec. Potencial',
                                                             delegate = CurrencyDelegate,
                                                             prefix = '$'),
                                porcentaje = dict(name = '%',
                                                  delegate = FloatDelegate),
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

class PerdidaPorIncobrable(object):
    class Admin(EntityAdmin):
        verbose_name = u'Pérdida por Incobrable'
        verbose_name_plural = u'Pérdida por Incobrable'
        list_display = ['comentarios',
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
                        ]
        list_filter = [ComboBoxFilter('barrio'),
                       ]
        expanded_list_search = ['comentarios',
                        'beneficiaria',
                        'fecha_baja',
                        'barrio',
                        'nro_credito',
                        'fecha_finalizacion',
                        'fecha_entrega',
                        'prestamo',
                        'deuda_total',
                        'saldo',
                        ]
        list_actions = [reports.ReportePerdidaPorIncobrable()]
        list_action = None
        field_attributes = dict(fecha_baja = dict(delegate = DateDelegate),
                                fecha_finalizacion = dict(delegate = DateDelegate,
                                                          name = u'Fecha finalización',
                                                          minimal_column_width = 15),
                                fecha_entrega = dict(delegate = DateDelegate),
                                prestamo = dict(delegate = CurrencyDelegate,
                                                prefix = '$',
                                                name = u'Préstamo'),
                                deuda_total = dict(delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                saldo = dict(delegate = CurrencyDelegate,
                                             prefix = '$'),
                                comentarios = dict(minimal_column_width = 20),
                                comentarios_baja = dict(minimal_column_width = 15),
                                beneficiaria = dict(minimal_column_width = 25),
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

class CreditosFinalizadosSinSaldar(object):
    class Admin(EntityAdmin):
        verbose_name = u'Créditos finalizados sin saldar'
        verbose_name_plural = u'Créditos finalizados sin saldar'
        list_display = ['comentarios',
                        'beneficiaria',
                        'barrio',
                        'nro_credito',
                        'fecha_finalizacion',
                        'fecha_entrega',
                        'prestamo',
                        'deuda_total',
                        'saldo',
                        ]
        
        list_filter = [ComboBoxFilter('barrio'),
                       ]
        list_action = None
        list_actions = [reports.ReporteCreditosFinalizadosSinSaldar()]
        field_attributes = dict(fecha_finalizacion = dict(delegate = DateDelegate,
                                                          name = u'Fecha finalización',
                                                          minimal_column_width = 15),
                                fecha_entrega = dict(delegate = DateDelegate),
                                prestamo = dict(delegate = CurrencyDelegate,
                                                prefix = '$',
                                                name = u'Préstamo'),
                                deuda_total = dict(delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                saldo = dict(delegate = CurrencyDelegate,
                                             prefix = '$'),
                                comentarios = dict(name = 'CDI',
                                                   minimal_column_width = 20),
                                beneficiaria = dict(minimal_column_width = 25),
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

class DatesValidator(ObjectValidator):
    def objectValidity(self, entity_instance):
        messages = super(DatesValidator, self).objectValidity(entity_instance)
        if entity_instance.hasta < entity_instance.desde:
            messages.append("'Fecha hasta' debe ser igual o posterior a a 'Fecha desde'")
        return messages

class IntervaloFechasDialog(object):
    def __init__(self):
        self.desde = datetime.date.today()
        self.hasta = datetime.date.today()

    def _get_desde(self):
        return self.desde

    def _set_desde(self, value):
        self.desde = value
        if self.hasta < value:
            self.hasta = value

    _desde = property(_get_desde, _set_desde)

    class Admin(ObjectAdmin):
        verbose_name = 'Intervalo de fechas'
        form_display = ['_desde', 'hasta']
        validator = DatesValidator
        form_size = (100, 100)
        field_attributes = dict(_desde = dict(name = 'Fecha desde',
                                              delegate = DateDelegate,
                                              editable = True),
                                hasta = dict(name = 'Fecha hasta',
                                             delegate = DateDelegate,
                                             editable = True,
                                             tooltip = 'Debe ser mayor o igual que fecha desde',
                                             background_color = lambda o: ColorScheme.orange_1 if o.hasta < o.desde else None))
        
class IntervaloFechas(Action):
    verbose_name = 'Definir Intervalo de fechas'
    icon = Icon('tango/16x16/apps/office-calendar.png')

    def find_friday(self, date, inc):
        day = datetime.timedelta(days=inc)
        while date.weekday() != 4:      # friday is weekday 4
            date += day
        return date

    def model_run(self, model_context):
        # ask for date intervals
        fechas = IntervaloFechasDialog()
        yield ChangeObject(fechas)

        # truncate tables (after ChangeObject since user may cancel)
        model.Parametro.query.delete()
        model.Fecha.query.delete()

        desde = self.find_friday(fechas.desde, 1)
        hasta = self.find_friday(fechas.hasta, -1)
        if hasta < desde:
            hasta = desde

        # add to parametro
        p = model.Parametro()
        p.fecha = desde
        model.Parametro.query.session.flush()

        # add dates
        week = datetime.timedelta(weeks=1)
        while desde <= hasta:
            f = model.Fecha()
            f.fecha = desde
            desde += week
            yield UpdateProgress()

        model.Fecha.query.session.flush()
        yield Refresh()

class ChequesEntregados(object):
    class Admin(EntityAdmin):
        verbose_name = u'Cartera - Préstamos / Cheques Entregados'
        verbose_name_plural = u'Préstamos / Cheques Entregados'
        list_display = ['beneficiaria',
                        'barrio',
                        'cartera',
                        'nro_credito',
                        'fecha_entrega',
                        'monto_prestamo',
                        'monto_cheque',
                        ]
        list_actions = [reports.ReporteChequesEntregados()]
        list_action = None
        list_filter = [ComboBoxFilter('barrio'),
                       ComboBoxFilter('cartera'),
                       ]
        field_attributes = dict(fecha_entrega = dict(delegate = DateDelegate),
                                monto_prestamo = dict(delegate = CurrencyDelegate,
                                                      prefix = '$'),
                                monto_cheque = dict(delegate = CurrencyDelegate,
                                                    prefix = '$'),
                                beneficiaria = dict(minimal_column_width = 25),
                                )

def setup_cheques_entregados():
    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    tbl_cartera = Cartera.mapper.mapped_table

    s = select([tbl_credito.c.id.label('credito_id'),
                func.concat(tbl_benef.c.nombre, ' ', tbl_benef.c.apellido).label('beneficiaria'),
                tbl_barrio.c.nombre.label('barrio'),
                tbl_cartera.c.nombre.label('cartera'),
                tbl_credito.c.nro_credito,
                tbl_credito.c.fecha_entrega,
                func.sum(tbl_credito.c.prestamo).label('monto_prestamo'),
                func.sum(tbl_credito.c.monto_cheque).label('monto_cheque'),
                ],
               from_obj = tbl_credito.join(tbl_cartera).join(tbl_benef).join(tbl_barrio),
               group_by = tbl_credito.c.id
               )
                            
    s = s.alias('cheques_entregados')
    mapper(ChequesEntregados, s, always_refresh=True)

class CreditosActivos(object):
    class Admin(EntityAdmin):
        verbose_name = u'Cartera - Créditos Activos'
        verbose_name_plural = u'Créditos Activos'
        list_display = ['comentarios',
                        'beneficiaria',
                        'barrio',
                        'nro_credito',
                        'fecha_entrega',
                        'prestamo',
                        'saldo']
        list_actions = [reports.ReporteCreditosActivos()]
        list_action = None
        list_filter = [ComboBoxFilter('barrio')]
        field_attributes = dict(fecha_entrega = dict(delegate = DateDelegate),
                                prestamo = dict(delegate = CurrencyDelegate,
                                                prefix = '$'),
                                saldo = dict(delegate = CurrencyDelegate,
                                             prefix = '$'),
                                beneficiaria = dict(minimal_column_width = 25),
                                comentarios = dict(name = 'CDI'))
    # Admin = notEditableAdmin(Admin, actions=True)

def setup_creditos_activos():
    tpc = total_pagos_x_credito()

    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    
    s = select([tbl_credito.c.id.label('credito_id'),
                func.concat(tbl_benef.c.nombre, ' ', tbl_benef.c.apellido).label('beneficiaria'),
                tbl_benef.c.comentarios,
                tbl_barrio.c.nombre.label('barrio'),
                tbl_credito.c.nro_credito,
                tbl_credito.c.prestamo,
                tbl_credito.c.fecha_entrega,
                (tbl_credito.c.deuda_total - tpc.c.monto).label('saldo'),
                ],
               from_obj = tbl_credito.join(tbl_benef).join(tbl_barrio),
               whereclause = and_(tbl_credito.c.fecha_finalizacion == None,
                                  tpc.c.credito_id == tbl_credito.c.id,
                                  ),
               )
                            
    s = s.alias('creditos_activos')
    mapper(CreditosActivos, s, always_refresh=True)
        
def credito_pagos():
    tbl_credito = Credito.mapper.mapped_table
    tbl_pago = Pago.mapper.mapped_table
    
    s = select([tbl_credito.c.id.label('credito_id'),
                func.ifnull(tbl_pago.c.fecha, tbl_credito.c.fecha_entrega).label('fecha_pago_o_entrega'),
                func.ifnull(tbl_pago.c.monto, 0).label('monto'),
                tbl_credito.c.fecha_finalizacion,
                ],
               from_obj = tbl_credito.outerjoin(tbl_pago),
               )
    s = s.alias('credito_pagos')
    return s

def total_pagos_x_credito():
    cp = credito_pagos()
    s = select([cp.c.credito_id,
                func.sum(cp.c.monto).label('monto'),
                ],
               group_by = cp.c.credito_id,
               )
    s = s.alias('total_pagos_x_credito')
    return s

def setup_creditos_finalizados_sin_saldar():
    tpc = total_pagos_x_credito()

    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    
    s = select([tbl_credito.c.id.label('credito_id'),
                func.concat(tbl_benef.c.nombre, ' ', tbl_benef.c.apellido).label('beneficiaria'),
                tbl_benef.c.comentarios,
                tbl_barrio.c.nombre.label('barrio'),
                tbl_credito.c.nro_credito,
                tbl_credito.c.fecha_finalizacion,
                tbl_credito.c.fecha_entrega,
                tbl_credito.c.prestamo,
                tbl_credito.c.deuda_total,
                (tbl_credito.c.deuda_total - tpc.c.monto).label('saldo'),
                ],
               from_obj = tbl_credito.join(tbl_benef).join(tbl_barrio),
               whereclause = and_(tbl_credito.c.fecha_finalizacion == None,
                                  tbl_credito.c.deuda_total - tpc.c.monto > 1, # 1 y no 0 x redondeo
                                  tpc.c.credito_id == tbl_credito.c.id,
                                  ),
               )
                            
    s = s.alias('creditos_finalizados_sin_saldar')
    mapper(CreditosFinalizadosSinSaldar, s, always_refresh=True)

def setup_perdida_x_incobrable():
    tpc = total_pagos_x_credito()

    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    
    s = select([tbl_credito.c.id.label('credito_id'),
                tbl_benef.c.comentarios,
                func.concat(tbl_benef.c.nombre, ' ', tbl_benef.c.apellido).label('beneficiaria'),
                tbl_benef.c.fecha_baja,
                tbl_barrio.c.nombre.label('barrio'),
                tbl_credito.c.nro_credito,
                tbl_credito.c.fecha_finalizacion,
                tbl_credito.c.comentarios.label('comentarios_baja'),
                tbl_credito.c.fecha_entrega,
                tbl_credito.c.prestamo,
                tbl_credito.c.deuda_total,
                (tbl_credito.c.deuda_total - tpc.c.monto).label('saldo'),
                ],
               from_obj = tbl_credito.join(tbl_benef).join(tbl_barrio),
               whereclause = and_(tbl_credito.c.fecha_finalizacion != None,
                                  tbl_credito.c.comentarios != None,
                                  tpc.c.credito_id == tbl_credito.c.id,
                                  ),
               )
                            
    s = s.alias('perdida_x_incobrable')
    mapper(PerdidaPorIncobrable, s, always_refresh=True)

def setup_views_cartera():
    setup_cheques_entregados()
    setup_creditos_activos()
    setup_perdida_x_incobrable()
    setup_creditos_finalizados_sin_saldar()

def setup_views():
    setup_views_cartera()
