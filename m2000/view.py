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

from model import Beneficiaria, Cartera, Credito, Barrio
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

# esta clase corresponde a un VIEW
class CreditosActivos(Entity):
    using_options(tablename='402_creditos_activos', autoload=True, allowcoloverride=True)
    beneficiaria_id = Field(Integer, primary_key=True)
    credito_id = Field(Integer, primary_key=True)

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
        list_filter = [ComboBoxFilter('beneficiaria'),
                       ComboBoxFilter('barrio'),
                       ]
        field_attributes = dict(fecha_entrega = dict(delegate = DateDelegate),
                                prestamo = dict(delegate = CurrencyDelegate,
                                                prefix = '$'),
                                saldo = dict(delegate = CurrencyDelegate,
                                             prefix = '$'),
                                beneficiaria = dict(minimal_column_width = 25),
                                comentarios = dict(name = 'CDI'))
    # Admin = notEditableAdmin(Admin, actions=True)
    

# esta clase corresponde a un VIEW
class PerdidaPorIncobrable(Entity):
    using_options(tablename='901_perdida_x_incobrable', autoload=True, allowcoloverride=True)
    beneficiaria_id = Field(Integer, primary_key=True)
    credito_id = Field(Integer, primary_key=True)
    
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
        # TODO no se muestran los campos de busqueda
        search_all_fields = False
        list_search = ['beneficiaria',
                       'fecha_baja',
                       'barrio'
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

# esta clase corresponde a un VIEW
class CreditosFinalizadosSinSaldar(Entity):
    using_options(tablename='creditos_finalizados_sin_saldar', autoload=True, allowcoloverride=True)
    beneficiaria_id = Field(Integer, primary_key=True)
    credito_id = Field(Integer, primary_key=True)
    
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
        # TODO no se muestran los campos de busqueda
        search_all_fields = False
        list_search = ['beneficiaria',
                       'barrio'
                       'nro_credito',
                       'fecha_finalizacion',
                       'fecha_entrega',
                       'prestamo',
                       'deuda_total',
                       'saldo',
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
                        'monto_cheque']
        list_actions = [reports.ReporteChequesEntregados()]
        list_action = None
        list_filter = [ComboBoxFilter('barrio'),
                       ComboBoxFilter('cartera')]
        search_all_fields = True
        list_search = ['beneficiaria', 
                       'fecha_entrega']
        expanded_list_search = ['beneficiaria',
                                'fecha_entrega',
                                ]
        field_attributes = dict(fecha_entrega = dict(delegate = DateDelegate),
                                monto_prestamo = dict(delegate = CurrencyDelegate,
                                                      prefix = '$'),
                                monto_cheque = dict(delegate = CurrencyDelegate,
                                                    prefix = '$'),
                                beneficiaria = dict(minimal_column_width = 25))

def setup_cheques_entregados():
    s = select([Credito.id.label('credito_id'),
                func.concat(Beneficiaria.nombre, ' ', Beneficiaria.apellido).label('beneficiaria'),
                Barrio.nombre.label('barrio'),
                Cartera.nombre.label('cartera'),
                Credito.nro_credito,
                Credito.fecha_entrega,
                func.sum(Credito.prestamo).label('monto_prestamo'),
                func.sum(Credito.monto_cheque).label('monto_cheque'),
                ],
                whereclause = and_(Beneficiaria.barrio_id == Barrio.id,
                                   Credito.beneficiaria_id == Beneficiaria.id,
                                   Credito.cartera_id == Cartera.id),
                group_by = [Credito.id]
               )
                            
    s = s.alias('cheques_entregados')
    mapper(ChequesEntregados, s, always_refresh=True)

def setup_views():
    setup_cheques_entregados()
    
