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
import time

from camelot.admin.action import application_action
from camelot.admin.action.base import Action
from camelot.admin.entity_admin import EntityAdmin
# from camelot.admin.not_editable_admin import notEditableAdmin
from camelot.admin.object_admin import ObjectAdmin
from camelot.admin.validator.object_validator import ObjectValidator
from camelot.view.action_steps import ChangeObject, FlushSession, UpdateProgress, Refresh
from camelot.view.art import ColorScheme, Icon
from camelot.view.controls.delegates import DateDelegate, FloatDelegate, CurrencyDelegate, IntegerDelegate
from camelot.view.filters import ComboBoxFilter, ValidDateFilter
from sqlalchemy.orm import mapper
from sqlalchemy.sql import select, func, and_, or_

from camelot.model import metadata
__metadata__ = metadata

from model import Beneficiaria, Cartera, Credito, Barrio, Pago, EstadoCredito, Parametro
import config
import reports

def min_fecha():
    tbl_parametro = Parametro.mapper.mapped_table
    return select([func.min(tbl_parametro.c.fecha)], from_obj=tbl_parametro).alias('min_fecha')

def max_fecha():
    tbl_parametro = Parametro.mapper.mapped_table
    return select([func.max(tbl_parametro.c.fecha)], from_obj=tbl_parametro).alias('max_fecha')

class ChequesEntregados(object):
    class Admin(EntityAdmin):
        verbose_name = u'Cartera - Préstamos / Cheques Entregados'
        verbose_name_plural = u'Préstamos / Cheques Entregados'
        list_display = ['beneficiaria',
                        'barrio',
                        'cartera',
                        'nro_credito',
                        'fecha_entrega',
                        'prestamo',
                        'monto_cheque',
                        ]
        list_actions = [reports.ReporteChequesEntregados()]
        list_action = None
        list_filter = [ComboBoxFilter('barrio'),
                       ComboBoxFilter('cartera'),
                       ]
        field_attributes = dict(beneficiaria = dict(minimal_column_width = 25),
                                nro_credito = dict(name = u'Nro. Crédito'),
                                fecha_entrega = dict(delegate = DateDelegate),
                                prestamo = dict(name = u'Préstamo',
                                                delegate = CurrencyDelegate,
                                                prefix = '$'),
                                monto_cheque = dict(delegate = CurrencyDelegate,
                                                    prefix = '$'),
                                )

def cheques_entregados():
    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    tbl_cartera = Cartera.mapper.mapped_table

    stmt = select([tbl_credito.c.id.label('credito_id'),
                   func.concat(tbl_benef.c.nombre, ' ', tbl_benef.c.apellido).label('beneficiaria'),
                   tbl_barrio.c.nombre.label('barrio'),
                   tbl_cartera.c.nombre.label('cartera'),
                   tbl_credito.c.nro_credito,
                   tbl_credito.c.fecha_entrega,
                   tbl_credito.c.prestamo,
                   tbl_credito.c.monto_cheque,
                   ],
                  from_obj=tbl_credito.join(tbl_cartera).join(tbl_benef).join(tbl_barrio),
                  )
    return stmt.alias('cheques_entregados')

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

def creditos_activos():
    tpc = total_pagos_x_credito()

    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    
    stmt = select([tbl_credito.c.id.label('credito_id'),
                   func.concat(tbl_benef.c.nombre, ' ', tbl_benef.c.apellido).label('beneficiaria'),
                   tbl_benef.c.comentarios,
                   tbl_barrio.c.nombre.label('barrio'),
                   tbl_credito.c.nro_credito,
                   tbl_credito.c.prestamo,
                   tbl_credito.c.fecha_entrega,
                   (tbl_credito.c.deuda_total - tpc.c.monto).label('saldo'),
                   ],
                  from_obj=tbl_credito.join(tbl_benef).join(tbl_barrio),
                  whereclause=and_(tbl_credito.c.fecha_finalizacion == None,
                                   tpc.c.credito_id == tbl_credito.c.id,
                                   ),
                  )
    return stmt.alias('creditos_activos')
        
def credito_pagos():
    # Todos los pagos para cada credito.
    # Aquellos creditos que no tienen pago, muestran la fecha de entrega como fecha de pago y el monto en 0

    tbl_credito = Credito.mapper.mapped_table
    tbl_pago = Pago.mapper.mapped_table
    
    stmt = select([tbl_credito.c.id.label('credito_id'),
                   func.ifnull(tbl_pago.c.fecha, tbl_credito.c.fecha_entrega).label('fecha_pago_o_entrega'),
                   func.ifnull(tbl_pago.c.monto, 0).label('monto'),
                   tbl_credito.c.fecha_finalizacion,
                   ],
                  from_obj=tbl_credito.outerjoin(tbl_pago),
                  )
    return stmt.alias('credito_pagos')

def total_pagos_x_credito():
    cp = credito_pagos()
    stmt = select([cp.c.credito_id,
                   func.sum(cp.c.monto).label('monto'),
                   ],
                  group_by=cp.c.credito_id,
                  )
    return stmt.alias('total_pagos_x_credito')

def total_pagos_x_credito_activo_a_fecha():
    tbl_parametro = Parametro.mapper.mapped_table
    cp = credito_pagos()
    stmt = select([tbl_parametro.c.fecha,
                   cp.c.credito_id,
                   func.sum(cp.c.monto).label('total_pagos'),
                   ],
                  from_obj=[tbl_parametro,
                            cp,
                            ],
                  whereclause=and_(cp.c.fecha_pago_o_entrega <= tbl_parametro.c.fecha,
                                   or_(cp.c.fecha_finalizacion > tbl_parametro.c.fecha,
                                       cp.c.fecha_finalizacion == None)),
                  group_by=[cp.c.credito_id,
                            tbl_parametro.c.fecha,
                            ],
                  correlate=False,
                  )
    return stmt.alias('total_pagos_x_credito_activo_a_fecha')

class Indicadores(object):
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
        expanded_list_search = [
            'comentarios',
            'barrio',
            'beneficiaria',
            'nro_credito',
            'fecha_entrega',
            'cartera',
            'estado',
            ]
        list_filter = [ComboBoxFilter('barrio')]
        list_columns_frozen = 1
        list_action = None
        list_actions = [reports.ReporteIndicadores()]
        field_attributes = dict(fecha_entrega = dict(name = 'F.Entrega',
                                                     delegate = DateDelegate),
                                comentarios = dict(name = 'CDI'),
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

def indicadores():
    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    tbl_cartera = Cartera.mapper.mapped_table
    tbl_estado_credito = EstadoCredito.mapper.mapped_table
    tbl_parametro = Parametro.mapper.mapped_table

    tp = total_pagos_x_credito_activo_a_fecha()

    pre = select([tbl_benef.c.id.label('beneficiaria_id'),
                  tbl_benef.c.comentarios,
                  tbl_barrio.c.nombre.label('barrio'),
                  func.concat(tbl_benef.c.nombre, ' ', tbl_benef.c.apellido).label('beneficiaria'),
                  tbl_credito.c.nro_credito,
                  tbl_credito.c.fecha_entrega,
                  func.adddate(tbl_credito.c.fecha_entrega, 14).label('fecha_inicio'),
                  func.adddate(tbl_credito.c.fecha_entrega, tbl_credito.c.cuotas * 7).label('fecha_cancelacion'),
                  tbl_credito.c.saldo_anterior,
                  (tbl_credito.c.deuda_total / (1 + tbl_credito.c.tasa_interes)).label('capital'),
                  tbl_credito.c.tasa_interes,
                  tbl_cartera.c.nombre.label('cartera'),
                  (tbl_credito.c.deuda_total * tbl_credito.c.tasa_interes / (1 + tbl_credito.c.tasa_interes)).label('monto_aporte'),
                  tbl_credito.c.deuda_total,
                  tbl_credito.c.cuotas,
                  (tbl_credito.c.deuda_total / tbl_credito.c.cuotas).label('cuota_calculada'),
                  (tp.c.total_pagos * tbl_credito.c.cuotas / tbl_credito.c.deuda_total).label('cuotas_pagadas'),
                  (tp.c.total_pagos / tbl_credito.c.deuda_total).label('cuotas_pagadas_porcent'),
                  func.if_(func.datediff(tbl_parametro.c.fecha,
                                        func.adddate(tbl_credito.c.fecha_entrega, 14)) / 7 > tbl_credito.c.cuotas,
                          tbl_credito.c.cuotas,
                          func.datediff(tbl_parametro.c.fecha,
                                        func.adddate(tbl_credito.c.fecha_entrega, 14)) / 7).label('cuotas_teorico'),
                  (tbl_credito.c.deuda_total - tp.c.total_pagos).label('saldo'),
                  tp.c.total_pagos.label('monto_pagado'),
                  ],
                 from_obj=[tbl_credito.join(tbl_benef).join(tbl_barrio).join(tbl_cartera),
                           tp,
                           tbl_parametro,
                           ],
                 whereclause=and_(tp.c.credito_id == tbl_credito.c.id,
                                  tbl_benef.c.activa == True,
                                  tbl_credito.c.deuda_total != 0,
                                  tbl_credito.c.fecha_entrega <= tbl_parametro.c.fecha,
                                  or_(tbl_credito.c.fecha_finalizacion > tbl_parametro.c.fecha,
                                      tbl_credito.c.fecha_finalizacion == None)),
                 ).alias('pre')

    # Para cada beneficiaria activa, el estado de sus creditos.
    stmt = select([pre.c.beneficiaria_id,
                   pre.c.comentarios,
                   pre.c.barrio,
                   pre.c.beneficiaria,
                   pre.c.nro_credito,
                   pre.c.fecha_entrega,
                   pre.c.fecha_inicio,
                   pre.c.fecha_cancelacion,
                   pre.c.saldo_anterior,
                   pre.c.capital,
                   pre.c.tasa_interes,
                   pre.c.cartera,
                   pre.c.monto_aporte,
                   pre.c.deuda_total,
                   pre.c.cuotas,
                   pre.c.cuota_calculada,
                   pre.c.cuotas_pagadas,
                   pre.c.cuotas_pagadas_porcent,
                   pre.c.cuotas_teorico,       
                   (pre.c.cuotas_teorico / pre.c.cuotas).label('cuotas_teorico_porcent'),
                   (pre.c.cuotas_teorico - pre.c.cuotas_pagadas).label('diferencia_cuotas'),
                   pre.c.saldo,
                   pre.c.monto_pagado,
                   (pre.c.deuda_total * pre.c.cuotas_teorico / pre.c.cuotas).label('monto_teorico'),
                   (pre.c.deuda_total * pre.c.cuotas_teorico / pre.c.cuotas - pre.c.monto_pagado).label('diferencia_monto'),
                   tbl_estado_credito.c.descripcion.label('estado'),
                   ],
                  from_obj=[pre,
                            tbl_estado_credito,
                            ],
                  whereclause=and_(pre.c.cuotas_teorico - pre.c.cuotas_pagadas > tbl_estado_credito.c.cuotas_adeudadas_min,
                                   pre.c.cuotas_teorico - pre.c.cuotas_pagadas <= tbl_estado_credito.c.cuotas_adeudadas_max,
                                   ),
                  )
    return stmt.alias('indicadores')

def setup_indicadores():
    stmt = indicadores()
    mapper(Indicadores, stmt, always_refresh=True,
           primary_key=[stmt.c.beneficiaria_id,
                        stmt.c.nro_credito,
                        ])

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
        field_attributes = dict(comentarios = dict(name = 'CDI',
                                                   minimal_column_width = 20),
                                beneficiaria = dict(minimal_column_width = 25),
                                nro_credito = dict(name = u'Nro. Crédito'),
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
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

def creditos_finalizados_sin_saldar():
    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table

    tpc = total_pagos_x_credito()
    
    stmt = select([tbl_credito.c.id.label('credito_id'),
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
                  from_obj=tbl_credito.join(tbl_benef).join(tbl_barrio),
                  whereclause=and_(tbl_credito.c.fecha_finalizacion != None,
                                   tbl_credito.c.deuda_total - tpc.c.monto >= 1, # 1 y no 0 x redondeo
                                   tpc.c.credito_id == tbl_credito.c.id,
                                   ),
                  )
    return stmt.alias('creditos_finalizados_sin_saldar')

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
        field_attributes = dict(comentarios = dict(minimal_column_width = 20,
                                                   name = 'CDI'),
                                beneficiaria = dict(minimal_column_width = 25),
                                fecha_baja = dict(delegate = DateDelegate),
                                nro_credito = dict(name = u'Nro. Crédito'),
                                fecha_finalizacion = dict(delegate = DateDelegate,
                                                          name = u'Fecha finalización',
                                                          minimal_column_width = 15),
                                comentarios_baja = dict(minimal_column_width = 15),
                                fecha_entrega = dict(delegate = DateDelegate),
                                prestamo = dict(delegate = CurrencyDelegate,
                                                prefix = '$',
                                                name = u'Préstamo'),
                                deuda_total = dict(delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                saldo = dict(delegate = CurrencyDelegate,
                                             prefix = '$'),
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

def perdida_x_incobrable():
    tpc = total_pagos_x_credito()

    tbl_credito = Credito.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    
    stmt = select([tbl_credito.c.id.label('credito_id'),
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
                  from_obj=tbl_credito.join(tbl_benef).join(tbl_barrio),
                  whereclause=and_(tbl_credito.c.fecha_finalizacion != None,
                                   tbl_credito.c.comentarios != None,
                                   tbl_benef.c.activa == False,
                                   tbl_credito.c.deuda_total - tpc.c.monto > 0,
                                   tpc.c.credito_id == tbl_credito.c.id,
                                   ),
                  )
    return stmt.alias('perdida_x_incobrable')

class RecaudacionPorCartera(object):
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación por Cartera'
        verbose_name_plural = u'Recaudación por Cartera'
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
        list_actions = [reports.ReporteRecaudacionPorCartera()]

    # Admin = notEditableAdmin(Admin, actions=True)

def recaudacion_x_cartera():
    # Para cada cartera, el total de pagos entre fechas, agrupados por cartera, barrio y tasa de interes
    tbl_credito = Credito.mapper.mapped_table
    tbl_pago = Pago.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table
    tbl_cartera = Cartera.mapper.mapped_table
    
    stmt = select([tbl_cartera.c.nombre.label('cartera'),
                   tbl_credito.c.tasa_interes,
                   func.sum(tbl_pago.c.monto).label('recaudacion'),
                   tbl_barrio.c.nombre.label('barrio'),
                   tbl_cartera.c.id.label('cartera_id'),
                   tbl_barrio.c.id.label('barrio_id'),
                   ],
                  from_obj=[tbl_credito.join(tbl_pago).join(tbl_benef).join(tbl_barrio).join(tbl_cartera),
                            ],
                  whereclause=and_(tbl_pago.c.fecha >= min_fecha(),
                                   tbl_pago.c.fecha <= max_fecha(),
                                   ),
                  group_by=[tbl_cartera.c.id,
                            tbl_credito.c.tasa_interes,
                            tbl_barrio.c.id,
                            ],
                  )
    return stmt.alias('recaudacion_x_cartera')

def setup_recaudacion_x_cartera():
    stmt = recaudacion_x_cartera()
    mapper(RecaudacionPorCartera, stmt, always_refresh=True,
           primary_key=[stmt.c.cartera_id,
                        stmt.c.tasa_interes,
                        stmt.c.recaudacion,
                        stmt.c.barrio_id,
                        ])

def recaudacion_x_barrio():
    # Total de pagos por semana y barrio, entre fechas.
    tbl_credito = Credito.mapper.mapped_table
    tbl_pago = Pago.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_barrio = Barrio.mapper.mapped_table

    stmt = select([func.yearweek(tbl_pago.c.fecha, 0).label('semana'),
                   tbl_barrio.c.id.label('barrio_id'),
                   tbl_barrio.c.nombre.label('barrio_nombre'),
                   func.sum(tbl_pago.c.monto).label('recaudacion'),
                   ],
                  from_obj=[tbl_credito.join(tbl_pago).join(tbl_benef).join(tbl_barrio),
                            ],
                  whereclause=and_(tbl_pago.c.fecha >= min_fecha(),
                                   tbl_pago.c.fecha <= max_fecha(),
                                   ),
                  group_by=[func.yearweek(tbl_pago.c.fecha, 0),
                            tbl_barrio.c.id,
                            ],
                  )
    return stmt.alias('recaudacion_x_barrio')

def recaudacion():
    tbl_pago = Pago.mapper.mapped_table
    tbl_credito = Credito.mapper.mapped_table
    tbl_cartera = Cartera.mapper.mapped_table

    stmt = select([func.yearweek(tbl_pago.c.fecha, 0).label('semana'),
                   tbl_cartera.c.id.label('cartera_id'),
                   tbl_credito.c.tasa_interes,
                   func.sum(tbl_pago.c.monto).label('recaudacion'),
                   ],
                  from_obj=[tbl_credito.join(tbl_pago).join(tbl_cartera),
                            ],
                  whereclause=and_(tbl_pago.c.fecha >= min_fecha(),
                                   tbl_pago.c.fecha <= max_fecha(),
                                   ),
                  group_by=[func.yearweek(tbl_pago.c.fecha, 0),
                            tbl_cartera.c.id,
                            tbl_credito.c.tasa_interes],
                  )
    return stmt.alias('recaudacion')

class RecaudacionRealTotal(object):
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Real Total'
        verbose_name_plural = u'Real Total'
        list_display = ['semana',
                        'cartera',
                        'tasa_interes',
                        'recaudacion',
                        ]
        list_actions = [reports.ReporteRecaudacionRealTotal()]
        list_filter = [ComboBoxFilter('cartera'),
                       ComboBoxFilter('semana'),
                       ]
        list_action = None
        field_attributes = dict(tasa_interes = dict(name = u'Tasa Interés',
                                                    delegate = FloatDelegate),
                                recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

def recaudacion_real_total():
    rec = recaudacion()
    tbl_cartera = Cartera.mapper.mapped_table
    
    stmt = select([func.concat(func.mid(rec.c.semana, 1, 4), '.', func.mid(rec.c.semana, 5, 2)).label('semana'),
                   tbl_cartera.c.nombre.label('cartera'),
                   rec.c.tasa_interes,
                   rec.c.recaudacion,
                   tbl_cartera.c.id,
                   ],
                  from_obj=[tbl_cartera,
                            rec,
                            ],
                  whereclause=tbl_cartera.c.id == rec.c.cartera_id,
                  )
    return stmt.alias('recaudacion_real_total')

def setup_recaudacion_real_total():
    stmt = recaudacion_real_total()
    mapper(RecaudacionRealTotal, stmt, always_refresh=True,
           primary_key=[stmt.c.semana,
                        stmt.c.cartera,
                        stmt.c.tasa_interes,
                        ])

class RecaudacionRealTotalPorBarrio(object):
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Real Total por Barrio'
        verbose_name_plural = u'Real Total por Barrio'
        list_display = ['semana',
                        'barrio',
                        'recaudacion',
                        ]
        list_filter = [ComboBoxFilter('barrio'),
                       ComboBoxFilter('semana'),
                       ]
        list_action = None
        list_actions = [reports.ReporteRecaudacionRealTotalPorBarrio()]
        field_attributes = dict(recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                fecha = dict(delegate = DateDelegate),
                                )
    # Admin = notEditableAdmin(Admin, actions=True)

def recaudacion_real_x_barrio():
    rec = recaudacion_x_barrio()
    stmt = select([func.concat(func.mid(rec.c.semana, 1, 4), '.', func.mid(rec.c.semana, 5, 2)).label('semana'),
                   rec.c.barrio_nombre.label('barrio'),
                   rec.c.recaudacion,
                   rec.c.barrio_id,
                   ],
                  from_obj=rec,
                  )
    return stmt.alias('recaudacion_real_x_barrio')

def setup_recaudacion_real_total_x_barrio():
    stmt = recaudacion_real_x_barrio()
    mapper(RecaudacionRealTotalPorBarrio, stmt, always_refresh=True,
           primary_key=[stmt.c.semana,
                        stmt.c.barrio_id,
                        stmt.c.recaudacion,
                        ])

class RecaudacionPotencialTotal(object):
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Potencial Total'
        verbose_name_plural = u'Potencial Total'
        list_display = ['semana',
                        'recaudacion',
                        'recaudacion_potencial',
                        'porcentaje',
                        ]
        list_filter = [ComboBoxFilter('semana')]
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

def recaudacion_potencial_total():
    tbl_credito = Credito.mapper.mapped_table

    rec_real = recaudacion()
    rec_total_real = select([rec_real.c.semana,
                             func.sum(rec_real.c.recaudacion).label('recaudacion'),
                             ],
                            from_obj=rec_real,
                            group_by=rec_real.c.semana,
                            ).alias('rec_total_real')
    
    rec_pot = select([rec_total_real.c.semana,
                      rec_total_real.c.recaudacion,
                      func.sum(tbl_credito.c.deuda_total / tbl_credito.c.cuotas).label('recaudacion_potencial'),
                      ],
                     from_obj = [tbl_credito,
                                 rec_total_real,
                                 ],
                     whereclause=and_(func.yearweek(func.adddate(tbl_credito.c.fecha_entrega, 14), 0) >= rec_total_real.c.semana,
                                      or_(func.yearweek(tbl_credito.c.fecha_finalizacion, 0) >= rec_total_real.c.semana,
                                          tbl_credito.c.fecha_finalizacion == None)),
                     group_by=rec_total_real.c.semana,
                     ).alias('rec_pot')
    
    stmt = select([func.concat(func.mid(rec_pot.c.semana, 1, 4), '.', func.mid(rec_pot.c.semana, 5, 2)).label('semana'),
                   rec_pot.c.recaudacion,
                   rec_pot.c.recaudacion_potencial,
                   (rec_pot.c.recaudacion / rec_pot.c.recaudacion_potencial).label('porcentaje'),
                   ],
                  from_obj=rec_pot,
                  )
    return stmt.alias('recaudacion_potencial')

def setup_recaudacion_potencial_total():
    stmt = recaudacion_potencial_total()
    mapper(RecaudacionPotencialTotal, stmt, always_refresh=True,
           primary_key=[stmt.c.semana,
                        stmt.c.recaudacion,
                        stmt.c.recaudacion_potencial,
                        stmt.c.porcentaje,
                        ])

class RecaudacionPotencialTotalPorBarrio(object):
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Potencial Total por Barrio'
        verbose_name_plural = u'Potencial Total por Barrio'
        list_display = ['semana',
                        'barrio',
                        'recaudacion',
                        'recaudacion_potencial',
                        'porcentaje',
                        ]
        list_filter = [ComboBoxFilter('barrio'),
                       ComboBoxFilter('semana'),
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

def recaudacion_potencial_total_x_barrio():
    tbl_barrio = Barrio.mapper.mapped_table
    tbl_benef = Beneficiaria.mapper.mapped_table
    tbl_credito = Credito.mapper.mapped_table

    rec_real = recaudacion_x_barrio()
    
    rec_pot = select([rec_real.c.semana,
                      rec_real.c.barrio_id,
                      rec_real.c.barrio_nombre,
                      rec_real.c.recaudacion,
                      func.sum(tbl_credito.c.deuda_total / tbl_credito.c.cuotas).label('recaudacion_potencial'),
                      ],
                     from_obj = [tbl_credito.join(tbl_benef).join(tbl_barrio),
                                 rec_real,
                                 ],
                     whereclause=and_(func.yearweek(func.adddate(tbl_credito.c.fecha_entrega, 14), 0) >= rec_real.c.semana,
                                      rec_real.c.barrio_id == tbl_barrio.c.id,
                                      or_(func.yearweek(tbl_credito.c.fecha_finalizacion, 0) >= rec_real.c.semana,
                                          tbl_credito.c.fecha_finalizacion == None)),
                     group_by=[rec_real.c.semana,
                               rec_real.c.barrio_id,
                               rec_real.c.recaudacion,
                               ]
                     ).alias('rec_pot')
    
    stmt = select([func.concat(func.mid(rec_pot.c.semana, 1, 4), '.', func.mid(rec_pot.c.semana, 5, 2)).label('semana'),
                   rec_pot.c.barrio_nombre.label('barrio'),
                   rec_pot.c.recaudacion,
                   rec_pot.c.recaudacion_potencial,
                   (rec_pot.c.recaudacion / rec_pot.c.recaudacion_potencial).label('porcentaje'),
                   ],
                  from_obj=rec_pot,
                  )

    return stmt.alias('recaudacion_potencial_total_x_barrio')

def setup_recaudacion_potencial_total_x_barrio():
    stmt = recaudacion_potencial_total_x_barrio()
    mapper(RecaudacionPotencialTotalPorBarrio, stmt, always_refresh=True,
           primary_key=[stmt.c.semana,
                        stmt.c.barrio,
                        stmt.c.recaudacion,
                        stmt.c.recaudacion_potencial,
                        stmt.c.porcentaje,
                        ])

def setup_views_indicadores():
    setup_indicadores()

def setup_views_recaudacion():
    setup_recaudacion_x_cartera()
    setup_recaudacion_real_total()
    setup_recaudacion_real_total_x_barrio()
    setup_recaudacion_potencial_total()
    setup_recaudacion_potencial_total_x_barrio()

def setup_views_cartera():
    mappings = {
        ChequesEntregados: cheques_entregados(),
        CreditosActivos: creditos_activos(),
        PerdidaPorIncobrable: perdida_x_incobrable(),
        CreditosFinalizadosSinSaldar: creditos_finalizados_sin_saldar(),
        }

    for cl, v in mappings.items():
        mapper(cl, v, always_refresh=True)

def setup_views():
    setup_views_indicadores()
    setup_views_recaudacion()
    setup_views_cartera()
    
class DatesValidator(ObjectValidator):
    def objectValidity(self, entity_instance):
        messages = super(DatesValidator, self).objectValidity(entity_instance)
        if entity_instance.hasta < entity_instance.desde:
            messages.append("'Fecha hasta' debe ser igual o posterior a a 'Fecha desde'")
        return messages

def get_config_date(key, default):
    conf = config.Config()
    ff = conf.safe_get(key)
    if not ff:
        return default
    tt = time.strptime(ff, '%Y-%m-%d')
    return datetime.date(tt.tm_year, tt.tm_mon, tt.tm_mday)

class FechaCorteDialog(object):
    def __init__(self):
        self.fecha = get_config_date('fecha_corte', datetime.date.today())

    class Admin(ObjectAdmin):
        verbose_name = 'Fecha de corte'
        form_display = ['fecha']
        form_size = (100, 100)
        field_attributes = dict(fecha = dict(name = 'Fecha de Corte',
                                             delegate = DateDelegate,
                                             editable = True))
            
class FechaCorte(Action):
    icon = Icon('tango/16x16/apps/office-calendar.png')
    
    def __init__(self, name, cls):
        self.verbose_name = name
        self._cls = cls
        
    def model_run(self, model_context):
        # ask for date intervals
        fecha = FechaCorteDialog()
        yield ChangeObject(fecha)

        # truncate tables (after ChangeObject since user may cancel)
        Parametro.query.delete()

        corte = fecha.fecha

        # guardar valor para usar por default la proxima vez
        conf = config.Config()
        conf.set('fecha_corte', corte.strftime('%Y-%m-%d'))

        # add to parametro
        p = Parametro()
        p.fecha = corte
        Parametro.query.session.flush()

        yield application_action.OpenTableView(model_context.admin.get_application_admin().get_related_admin(self._cls))
    
class IntervaloFechasDialog(object):
    def __init__(self):
        default = datetime.date.today()
        self.desde = get_config_date('fecha_desde', default)
        self.hasta = get_config_date('fecha_hasta', default)

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
                                             tooltip = 'Debe ser igual o posterior a fecha desde',
                                             background_color = lambda o: ColorScheme.orange_1 if o.hasta < o.desde else None))

class IntervaloFechas(Action):
    icon = Icon('tango/16x16/apps/office-calendar.png')
    
    def __init__(self, name, cls):
        self.verbose_name = name
        self._cls = cls
        
    def model_run(self, model_context):
        # ask for date intervals
        fechas = IntervaloFechasDialog()
        yield ChangeObject(fechas)

        # truncate table (after ChangeObject since user may cancel)
        Parametro.query.delete()        # holds only start and end date

        desde = fechas.desde
        hasta = fechas.hasta
            
        if hasta < desde:
            hasta = desde

        # guardar valores para usar por default la proxima vez
        conf = config.Config()
        conf.set('fecha_desde', desde.strftime('%Y-%m-%d'))
        conf.set('fecha_hasta', hasta.strftime('%Y-%m-%d'))
        
        # add dates
        p1 = Parametro()
        p1.fecha = desde
        p2 = Parametro()
        p2.fecha = hasta
        Parametro.query.session.flush()

        yield application_action.OpenTableView(model_context.admin.get_application_admin().get_related_admin(self._cls))
