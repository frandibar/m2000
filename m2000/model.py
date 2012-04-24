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

# meta data setup
from camelot.model import metadata
__metadata__ = metadata

import datetime

from camelot.admin.action import Action
from camelot.admin.entity_admin import EntityAdmin
from camelot.admin.validator.entity_validator import EntityValidator
from camelot.core.files.storage import Storage, StoredImage
from camelot.view.action_steps import FlushSession, UpdateProgress, MessageBox, UpdateObject
from camelot.view.controls.delegates import DateDelegate, FloatDelegate, BoolDelegate, NoteDelegate, CurrencyDelegate, IntegerDelegate
from camelot.view.filters import ComboBoxFilter, ValidDateFilter, GroupBoxFilter
from camelot.view.forms import Form, TabForm, WidgetOnlyForm, HBoxForm
from elixir import Entity, Field, using_options, ManyToOne, OneToMany
from elixir.properties import ColumnProperty
from sqlalchemy import Unicode, Date, Boolean, Integer, Float
from sqlalchemy import sql, and_, desc
from PyQt4.QtGui import QMessageBox
import camelot
import sqlalchemy

import reports
from constants import PKEY_UNDEFINED, ID_ACTIVIDAD_CONSTRUCCION

class RubroAdminEmbedded(EntityAdmin):
    verbose_name = 'Rubro'
    list_display = ['nombre']
    list_action = None
    delete_mode = 'on_confirm'

class Actividad(Entity):
    using_options(tablename='actividad')
    nombre = Field(Unicode(200), unique=True, required=True)
    amortizacion = ManyToOne('Amortizacion', ondelete='cascade', onupdate='cascade', required=True)
    rubros = OneToMany('Rubro')

    class Admin(EntityAdmin):
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        list_display = ['nombre', 'amortizacion', 'rubros']
        field_attributes = dict(amortizacion = dict(name = u'Amortización'),
                                rubros = dict(admin = RubroAdminEmbedded))
        list_search = ['nombre', 'amortizacion.nombre', 'rubros.nombre']
        delete_mode = 'on_confirm'

    def __unicode__(self):
        return self.nombre or UNDEFINED

class Rubro(Entity):
    using_options(tablename='rubro')
    nombre = Field(Unicode(200), required=True)
    actividad = ManyToOne('Actividad', ondelete='cascade', onupdate='cascade', required=True)

    class Admin(EntityAdmin):
        verbose_name = 'Rubro'
        list_display = ['nombre', 'actividad']
        list_search = ['nombre', 'actividad.nombre']
        list_action = None
        delete_mode = 'on_confirm'
        form_size = (450,150)

    def __unicode__(self):
        return self.nombre or UNDEFINED

class Asistencia(Entity):
    using_options(tablename='asistencia')
    codigo = Field(Unicode(5), primary_key=True)
    descripcion = Field(Unicode(200), nullable=True)

    class Admin(EntityAdmin):
        verbose_name = 'Asistencia'
        list_display = ['codigo', 'descripcion']
        field_attributes = { 'codigo': { 'name': u'Código' },
                             'descripcion': { 'name': u'Descripción' } }
        list_action = None
        delete_mode = 'on_confirm'
        form_size = (450,150)

    def __unicode__(self):
        return self.descripcion or UNDEFINED

class Provincia(Entity):
    using_options(tablename='provincia')
    nombre = Field(Unicode(200), unique=True, required=True)

    class Admin(EntityAdmin):
        verbose_name = 'Provincia'
        list_display = ['nombre']
        list_action = None
        delete_mode = 'on_confirm'
        form_size = (450,100)

    def __unicode__(self):
        return self.nombre or UNDEFINED

class Ciudad(Entity):
    using_options(tablename='ciudad')
    nombre = Field(Unicode(200), required=True)
    provincia = ManyToOne('Provincia', ondelete='cascade', onupdate='cascade', required=True)

    class Admin(EntityAdmin):
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        list_display = ['nombre', 'provincia']
        list_action = None
        delete_mode = 'on_confirm'
        form_size = (450,150)

    def __unicode__(self):
        return self.nombre or UNDEFINED

class DomicilioPago(Entity):
    using_options(tablename='domicilio_pago')
    nombre = Field(Unicode(200), required=True)
    ciudad = ManyToOne('Ciudad', ondelete='cascade', onupdate='cascade', required=True)

    class Admin(EntityAdmin):
        verbose_name = 'Domicilio de Pago'
        verbose_name_plural = 'Domicilios de Pago'
        list_display = ['nombre', 'ciudad']
        list_action = None
        delete_mode = 'on_confirm'
        form_size = (450,150)

    def __unicode__(self):
        return self.nombre or UNDEFINED

class Barrio(Entity):
    using_options(tablename='barrio')
    nombre = Field(Unicode(200), unique=True, required=True)
    domicilio_pago = ManyToOne('DomicilioPago', ondelete='cascade', onupdate='cascade', required=True)

    class Admin(EntityAdmin):
        verbose_name = 'Barrio'
        list_display = ['nombre', 'domicilio_pago']
        field_attributes = { 'domicilio_pago': { 'name': u'Domicilio de Pago' } }
        list_action = None
        delete_mode = 'on_confirm'
        form_size = (450,150)

    def __unicode__(self):
        return self.nombre or UNDEFINED

class PagoAdminBase(EntityAdmin):
    verbose_name = 'Pago'
    field_attributes = dict(credito = dict(name = u'Crédito'),
                            monto = dict(prefix = '$'),
                            nro_credito = dict(name = u'Nro. crédito',
                                               editable = False),
                            beneficiaria = dict(editable = False),
                            barrio = dict(editable = False),
                            )
    search_all_fields = True
    expanded_list_search = ['beneficiaria',
                            'nro_credito',
                            'fecha',
                            'monto',
                            'asistencia.codigo',
                            'barrio',
                            ]
    list_actions = [reports.ReportePagos()]
    delete_mode = 'on_confirm'

    # esto es para que se refresque el campo total_pagos de credito
    def get_depending_objects(self, obj):
        yield obj.credito

    def get_query(self):
        """Redefino para devolver ordenado por fecha desc"""
        return EntityAdmin.get_query(self).order_by(desc('fecha'))

class PagoAdminEmbedded(PagoAdminBase):
    list_display = ['fecha',
                    'monto',
                    'asistencia']
    list_action = None

class CreditoValidator(EntityValidator):
    def objectValidity(self, entity_instance):
        messages = super(CreditoValidator, self).objectValidity(entity_instance)
        # TODO chequear que no hayan creditos activos con la misma amortizacion
        # creditos_activos_rubro = sql.select([sql.func.count(Credito.id)],
        #                                     sql.where(rubro.actividad.amortizacion.id == entity_instance.rubro.actividad.amortizacion.id),
        #                                     sql.group_by(Credito.id))
        # if creditos_activos_rubro > 0:
        #     messages.append('Ya existe un crédito activo con dicha amortización')
        return messages

class CreditoAdminBase(EntityAdmin):
    verbose_name = u'Crédito'
    list_columns_frozen = 1
    list_display = ['beneficiaria_prop',
                    'nro_credito',
                    'rubro_prop',
                    'fecha_entrega',    # en vez de _fecha_entrega para poder ordenar
                    'fecha_cobro',
                    'prestamo',        # en vez de _prestamo para poder ordenar
                    'saldo_anterior',  # en vez de _saldo_anterior para poder ordenar
                    'monto_cheque',
                    'tasa_interes',     # en vez de _tasa_interes para poder ordenar
                    'deuda_total',
                    'cartera',
                    'cuotas',
                    'fecha_finalizacion',
                    'comentarios',
                    'barrio',
                    # 'gastos_arq',
                    ]
    delete_mode = 'on_confirm'
    search_all_fields = True
    expanded_list_search = ['beneficiaria_prop',
                            'nro_credito',
                            'rubro_prop',
                            'fecha_entrega',
                            'fecha_cobro',
                            'prestamo',
                            'fecha_finalizacion',
                            'cartera.nombre']
    list_filter = [GroupBoxFilter('activo', default=True),
                   ComboBoxFilter('cartera.nombre'),
                   ComboBoxFilter('barrio'),
                   ValidDateFilter('_fecha_entrega', 'fecha_finalizacion', u'Período e/entrega~fin', default=lambda:'')]

    def _use_gastos_arq(obj):
        try:
            if obj.rubro:
                return obj.rubro.actividad.id == ID_ACTIVIDAD_CONSTRUCCION
        except Exception, e:
            pass
        return True

    field_attributes = dict(beneficiaria_prop = dict(name = 'Beneficiaria',
                                                     minimal_column_width = 25,
                                                     editable = False),
                            nro_credito = dict(name = u'Nro. Crédito',
                                               calculator = False),
                            rubro_prop = dict(name = 'Rubro',
                                              minimal_column_width = 20,
                                              editable = False),
                            _fecha_entrega = dict(delegate = DateDelegate,
                                                  name = 'Fecha entrega',
                                                  minimal_column_width = 17,
                                                  editable = True),
                            fecha_entrega = dict(name = 'Fecha entrega',
                                                 minimal_column_width = 17,
                                                 editable = False),
                            fecha_cobro = dict(minimal_column_width = 17,
                                               tooltip = u'Se incializa en: Fecha entrega + 2 días.'),
                            _prestamo = dict(name = u'Préstamo',
                                             prefix = '$',
                                             delegate = CurrencyDelegate,
                                             editable = True),
                            prestamo = dict(name = u'Préstamo',
                                            prefix = '$',),
                            _saldo_anterior = dict(name = 'Saldo Anterior',
                                                   prefix = '$',
                                                   delegate = CurrencyDelegate,
                                                   editable = True),
                            saldo_anterior = dict(name = 'Saldo Anterior',
                                                   prefix = '$',),
                            monto_cheque = dict(name = 'Monto Cheque/Presup.',
                                                prefix = '$',
                                                tooltip = u'Se inicializa en: Préstamo - Saldo anterior'),
                            _tasa_interes = dict(name = u'Tasa de interés',
                                                 delegate = FloatDelegate,
                                                 editable = True,
                                                 precision = 5),
                            tasa_interes = dict(name = u'Tasa de interés',
                                                editable = True,
                                                precision = 5),
                            deuda_total = dict(prefix = '$',
                                               tooltip = u'Se inicializa en: Préstamo x (1 + Tasa de interés)'),
                            fecha_finalizacion = dict(minimal_column_width = 20,
                                                      name = u'Fecha finalización'),
                            gastos_arq = dict(name = 'Gastos HAB + Arq.',
                                              minimal_column_width = 22,
                                              prefix = '$',
                                              editable = _use_gastos_arq),
                            total_pagos = dict(delegate = CurrencyDelegate,
                                               prefix = '$',
                                               editable = False),
                            saldo = dict(delegate = CurrencyDelegate,
                                         prefix = '$'),
                            activo = dict(delegate = BoolDelegate,
                                          to_string = lambda x:{1:'Si', 0:'No'}[x]),
                            pagos = dict(admin = PagoAdminEmbedded,
                                         #create_inline = True,  # no funciona como se espera
                                         ),
                            # TODO por el momento el name es estatico, no se puede cambiar en funcion de otros valores
                            # monto_cheque = dict(name = lambda o: 'Monto Presupuesto' if o.rubro.actividad.id == ID_ACTIVIDAD_CONSTRUCCION else 'Monto Cheque'),
                            )

    form_display = TabForm([(u'Crédito', Form([HBoxForm([['beneficiaria',
                                                          'rubro',
                                                          'cartera',
                                                          'nro_credito',
                                                          'cuotas']]),
                                               HBoxForm([['_fecha_entrega',
                                                          'fecha_cobro',
                                                          '_prestamo',
                                                          '_saldo_anterior',
                                                          'monto_cheque'],
                                                         ['_tasa_interes',
                                                          'deuda_total',
                                                          'fecha_finalizacion',
                                                          'comentarios',
                                                          'gastos_arq']])])),
                             (u'Pagos', Form([WidgetOnlyForm('pagos'),
                                             'deuda_total',
                                             'total_pagos',
                                             'saldo'])),
                            ])

    form_actions = [reports.ContratoMutuo(),
                    reports.PlanillaPagos(),
                    ]

    form_size = (900,600)
    validator = CreditoValidator

class CreditoAdminEmbedded(CreditoAdminBase):
    list_display = filter(lambda x: x not in ['beneficiaria'], CreditoAdminBase.list_display)

class Beneficiaria(Entity):
    using_options(tablename='beneficiaria')
    barrio = ManyToOne('Barrio', ondelete='cascade', onupdate='cascade', required=True)
    nombre = Field(Unicode(200), required=True)
    apellido = Field(Unicode(200), required=True)
    grupo = Field(Unicode(200), required=True)
    fecha_alta = Field(Date, default=datetime.date.today)
    activa = Field(Boolean, default=True)
    fecha_baja = Field(Date, nullable=True)
    comentarios = Field(Unicode(1000), nullable=True)
    dni = Field(Unicode(10))
    fecha_nac = Field(Date)
    domicilio = Field(Unicode(50))
    estado_civil = Field(camelot.types.Enumeration([(0,''),
                                                    (1,'soltera'),
                                                    (2,'concubina'),
                                                    (3,'casada'),
                                                    (4,'separada'),
                                                    (5,'divorciada'),
                                                    (6,'viuda')]))
    telefono = Field(Unicode(50))
    email = Field(camelot.types.VirtualAddress(256))
    default_foto = StoredImage(Storage('fotos', StoredImage), 'sin-foto.jpg')
    foto = Field(camelot.types.Image(upload_to='fotos'), default=default_foto)
    creditos = OneToMany('Credito')

    def _get_activa(self):
        return self.activa

    def _set_activa(self, value):
        # impedir la baja si tiene creditos activos
        if not value:
            if self.creditos_activos == 0:
                fecha_ultimo_pago = sql.select([sql.func.max(Pago.fecha)],
                                               and_(Pago.credito_id == Credito.id,
                                                    Credito.beneficiaria_id == Beneficiaria.id))
                self.fecha_baja = fecha_ultimo_pago
                self.activa = False
        else:
            self.fecha_baja = None
            self.activa = True

    _activa = property(_get_activa, _set_activa)

    @ColumnProperty
    def creditos_activos(self):
        return sql.select([sql.func.count(Credito.id)],
                          and_(Credito.beneficiaria_id == Beneficiaria.id,
                               sql.column('fecha_finalizacion') == sql.null()))
    @ColumnProperty
    def nombre_completo(self):
        return self.nombre + ' ' + self.apellido

    def __unicode__(self):
        if self.nombre and self.apellido:
            return '%s %s' % (self.nombre, self.apellido)
        return UNDEFINED

    class Admin(EntityAdmin):
        verbose_name = 'Beneficiaria'
        delete_mode = 'on_confirm'
        list_columns_frozen = 1
        lines_per_row = 1               # lo especifico por la foto
        delete_mode = 'on_confirm'
        list_display = ['nombre',
                        'apellido',
                        'grupo',
                        'fecha_alta',
                        '_activa',
                        'fecha_baja',
                        'comentarios',
                        'dni',
                        'fecha_nac',
                        'domicilio',
                        'estado_civil',
                        'telefono',
                        'email',
                        'barrio',
                        ]
        form_display = TabForm([('Beneficiaria', Form([HBoxForm([['nombre',
                                                                  'apellido',
                                                                  'barrio',
                                                                  'grupo',
                                                                  '_activa',
                                                                  'fecha_alta',
                                                                  'fecha_baja',
                                                                  'comentarios',
                                                                  'dni',
                                                                  'fecha_nac',
                                                                  ],
                                                                 [WidgetOnlyForm('foto'),
                                                                  'estado_civil',
                                                                  'domicilio',
                                                                  'telefono',
                                                                  'email',
                                                                  'creditos_activos'
                                                                  ]])])),
                                (u'Créditos', WidgetOnlyForm('creditos')),
                                ])
        list_filter = [GroupBoxFilter('activa', default=True),
                       ComboBoxFilter('barrio.nombre'),
                       ]
        search_all_fields = False
        list_search = ['id',
                       'nombre_completo',
                       'comentarios',
                       'dni',
                       'grupo',
                       'barrio.nombre',
                       ]
        expanded_list_search = ['nombre',
                                'apellido',
                                'grupo',
                                'fecha_alta',
                                'fecha_baja',
                                'comentarios',
                                'dni',
                                'fecha_nac',
                                'barrio.nombre',
                                ]
        field_attributes = dict(fecha_alta = dict(name = 'Fecha Alta'),
                                _activa = dict(name = 'Activa',
                                               delegate = BoolDelegate,
                                               # to_string = lambda x:{True:'Si', False:'No'}[x], # TODO no lo toma
                                               editable = True,
                                               tooltip = u'No se puede dar de baja una beneficiaria si tiene créditos activos.'),
                                fecha_baja = dict(name = 'Fecha Baja',
                                                  tooltip = u'Al desactivar la beneficiaria, este campo toma la última fecha de pago'),
                                dni = dict(name = 'DNI'),
                                fecha_nac = dict(name = 'Fecha Nac.'),
                                estado_civil = dict(name = 'Estado Civil'),
                                telefono = dict(name = u'Teléfono'),
                                email = dict(address_type = 'email'),
                                creditos = dict(admin = CreditoAdminEmbedded),
                                creditos_activos = dict(name = u'Créditos activos',
                                                        editable = False),
                               )
        form_size = (850,400)

class Cartera(Entity):
    using_options(tablename='cartera')
    nombre = Field(Unicode(200), unique=True, required=True)
    tasa_interes_anual = Field(Float(precision=5))

    class Admin(EntityAdmin):
        verbose_name = 'Cartera'
        list_display = ['nombre', 'tasa_interes_anual']
        list_action = None
        form_size = (450,150)

    def __unicode__(self):
        return self.nombre or UNDEFINED

class Credito(Entity):
    using_options(tablename='credito')
    beneficiaria = ManyToOne('Beneficiaria', ondelete='cascade', onupdate='cascade', required=True)
    rubro = ManyToOne('Rubro', ondelete='cascade', onupdate='cascade', required=True)
    fecha_entrega = Field(Date, required=True)
    fecha_cobro = Field(Date, required=True)
    prestamo = Field(Float)
    saldo_anterior = Field(Float)
    monto_cheque = Field(Float)
    tasa_interes = Field(Float(precision=5))
    deuda_total = Field(Float)
    cartera = ManyToOne('Cartera', ondelete='cascade', onupdate='cascade', required=True)
    cuotas = Field(Integer, required=True)
    nro_credito = Field(Integer, default=0, required=True)
    fecha_finalizacion = Field(Date)
    comentarios = Field(Unicode(1000))
    gastos_arq = Field(Float)
    pagos = OneToMany('Pago')

    def _get_fecha_entrega(self):
        return self.fecha_entrega

    def _set_fecha_entrega(self, fecha):
        self.fecha_entrega = fecha
        self.fecha_cobro = fecha + datetime.timedelta(days=2)

    _fecha_entrega = property(_get_fecha_entrega, _set_fecha_entrega)

    def _deuda_aleman(self):
        factor = self.tasa_interes / 24
        cuota = self.prestamo / self.cuotas
        deuda_ant = self.prestamo
        deuda = 0
        for i in range(1, self.cuotas):
            deuda += cuota + factor * deuda_ant
            deuda_ant -= cuota
        return deuda + self.gastos_arq

    def _update_deuda_total(self):
        if self.para_construccion:
            self.deuda_total = self._deuda_aleman()
        else:
            self.deuda_total = self.prestamo * (1 + self.tasa_interes)

    def _update_monto_cheque(self):
        self.monto_cheque = self.prestamo - self.saldo_anterior

    def _get_prestamo(self):
        return self.prestamo

    def _set_prestamo(self, value):
        self.prestamo = value
        self._update_monto_cheque()
        self._update_deuda_total()

    _prestamo = property(_get_prestamo, _set_prestamo)

    def _get_saldo_anterior(self):
        return self.saldo_anterior

    def _set_saldo_anterior(self, value):
        self.saldo_anterior = value
        self._update_monto_cheque()

    _saldo_anterior = property(_get_saldo_anterior, _set_saldo_anterior)

    def _get_tasa_interes(self):
        return self.tasa_interes

    def _set_tasa_interes(self, value):
        self.tasa_interes = value
        self._update_deuda_total()

    _tasa_interes = property(_get_tasa_interes, _set_tasa_interes)

    @ColumnProperty
    def barrio(self):
        return sql.select([Barrio.nombre],
                          and_(Credito.beneficiaria_id == Beneficiaria.id,
                               Beneficiaria.barrio_id == Barrio.id))
        # tbl_credito = Credito.mapper.mapped_table
        # tbl_barrio = Barrio.mapper.mapped_table
        # tbl_benef = Beneficiaria.mapper.mapped_table
        # return sql.select([tbl_barrio.c.nombre],
        #                   from_obj = tbl_credito.join(tbl_benef).join(tbl_barrio),
        #                   whereclause = tbl_credito.c.id == self.id)

    @ColumnProperty
    def activo(self):
        return sql.select([sql.column('fecha_finalizacion') == sql.null()])

    # No uso ColumnProperty para que se refresque automaticamente cuando se modifican los totales
    @property
    def total_pagos(self):
        total = 0
        for i in self.pagos:
            total += i.monto
        return total

    # agrego esta property para poder ordenar y filtrar por este campo
    @ColumnProperty
    def beneficiaria_prop(self):
        return sql.select([sql.func.concat(Beneficiaria.nombre, ' ', Beneficiaria.apellido)],
                          Credito.beneficiaria_id == Beneficiaria.id)

    # agrego esta property para poder ordenar y filtrar por este campo
    @ColumnProperty
    def rubro_prop(self):
        return sql.select([Rubro.nombre],
                          Credito.rubro_id == Rubro.id)

    @property
    def para_construccion(self):
        if self.rubro:
            return self.rubro.actividad_id == ID_ACTIVIDAD_CONSTRUCCION
        return False

    @property
    def saldo(self):
        if self.total_pagos:
            return self.deuda_total - self.total_pagos
        else:
            return self.deuda_total

    def __unicode__(self):
        if self.beneficiaria or self.nro_credito:
            return '%s %s (cred. #%s)' % (self.beneficiaria.nombre, self.beneficiaria.apellido, self.nro_credito)
        return UNDEFINED

    class Admin(CreditoAdminBase):
        pass

        # # # TODO: comentado porque rompe los filtros y pierdo los delegates
        # # mostrar el campo gastos_arq editable o no en funcion de la actividad
        # def get_field_attributes(self, field_name):
        #     field_attributes = super(EntityAdmin, self).get_field_attributes(field_name)
        #     # if field_name == 'gastos_arq':
        #     #     field_attributes['editable'] = lambda x: x.rubro.actividad == 8   # 8 -> id construccion
        #     # else:
        #     #     field_attributes['editable'] = True
        #     return field_attributes

class Pago(Entity):
    using_options(tablename='pago')
    credito = ManyToOne('Credito', primary_key=True, ondelete='cascade', onupdate='cascade')
    monto = Field(Float)
    fecha = Field(Date, primary_key=True)
    asistencia = ManyToOne('Asistencia', ondelete='cascade', onupdate='cascade')

    @ColumnProperty
    def barrio(self):
        return sql.select([Barrio.nombre],
                          and_(Pago.credito_id == Credito.id,
                               Credito.beneficiaria_id == Beneficiaria.id,
                               Beneficiaria.barrio_id == Barrio.id))

    @ColumnProperty
    def beneficiaria(self):
        return sql.select([sql.func.concat(Beneficiaria.nombre, ' ', Beneficiaria.apellido)],
                          and_(Pago.credito_id == Credito.id,
                               Credito.beneficiaria_id == Beneficiaria.id))

    @ColumnProperty
    def nro_credito(self):
        return sql.select([Credito.nro_credito],
                          Pago.credito_id == Credito.id)

    class Admin(PagoAdminBase):
        verbose_name = 'Pago'
        list_display = ['beneficiaria',
                        'nro_credito',
                        'fecha',
                        'monto',
                        'asistencia',
                        'barrio',
                        ]
        list_filter = [ValidDateFilter('fecha', 'fecha', 'Fecha', default=lambda:''),
                       ComboBoxFilter('barrio'),
                       ]
        form_size = (600,200)
        form_display = Form([HBoxForm([['credito',
                                        'fecha',
                                        'monto',
                                        'asistencia',
                                        ]])])

    def __unicode__(self):
        if self.credito:
            return '%s %s (cred. #%s)' % (self.credito.beneficiaria.nombre,
                                          self.credito.beneficiaria.apellido,
                                          self.credito.nro_credito)
        return INDEFINIDO

class EstadoCredito(Entity):
    using_options(tablename='estado_credito')
    descripcion = Field(Unicode(200), unique=True, required=True)
    cuotas_adeudadas_min = Field(Integer, required=True)
    cuotas_adeudadas_max = Field(Integer, required=True)

    class Admin(EntityAdmin):
        verbose_name = u'Estado de Crédito'
        verbose_name_plural = u'Estado de Créditos'
        list_display = ['descripcion',
                        'cuotas_adeudadas_min',
                        'cuotas_adeudadas_max']
        field_attributes = { 'descripcion': { 'name': u'Descripción' } }
        list_action = None
        delete_mode = 'on_confirm'

    def __unicode__(self):
        return self.descripcion or UNDEFINED

class Amortizacion(Entity):
    using_options(tablename='amortizacion')
    nombre = Field(Unicode(25), unique=True, required=True)

    class Admin(EntityAdmin):
        verbose_name = u'Amortización'
        verbose_name_plural = 'Amortizaciones'
        list_display = ['nombre']
        list_action = None
        delete_mode = 'on_confirm'
        form_size = (450,100)

    def __unicode__(self):
        return self.nombre or UNDEFINED

class Parametro(Entity):
    using_options(tablename='parametro')
    fecha = Field(Date)

class BuscarCreditos(Action):
    verbose_name = u"Buscar créditos"

    def get_state(self, model_context):
        """Habilitar la accion solamente si se ingresaron los datos necesarios"""
        state = super(BuscarCreditos, self).get_state(model_context)
        obj = model_context.get_object()
        state.enabled = True if obj and obj.fecha and obj.barrio else False
        return state

    def model_run(self, model_context):
        # Buscar todos aquellos creditos que estan activos y corresponden al barrio
        obj = model_context.get_object()
        from sqlalchemy.sql import select
        tbl_credito = Credito.mapper.mapped_table
        tbl_benef = Beneficiaria.mapper.mapped_table
        tbl_barrio = Barrio.mapper.mapped_table

        stmt = select([tbl_credito.c.id.label('credito_id'),
                       ],
                      from_obj=tbl_credito.join(tbl_benef).join(tbl_barrio),
                      whereclause=and_(tbl_credito.c.fecha_finalizacion == None,
                                       obj.barrio_id == tbl_barrio.c.id),
                      )
        res = model_context.session.execute(stmt)
        for row in res:
            pc = PagoCredito()
            pc.planilla_pagos = obj
            pc.credito = Credito.query.filter_by(id=row["credito_id"]).one()
            yield UpdateProgress()
        yield FlushSession(PagoCredito.query.session)
        yield FlushSession(model_context.session)

class AplicarPlanilla(Action):
    verbose_name = u"Aplicar pagos"

    def model_run(self, model_context):
        # Volcar todos los pagos en la tabla de pagos.
        obj = model_context.get_object()
        Pago.query.session.begin()
        try:
            for pago in obj.creditos:
                row = Pago()
                row.credito = pago.credito
                row.monto = pago.monto
                row.fecha = obj.fecha
                row.asistencia = pago.asistencia
                yield FlushSession(Pago.query.session)
        except Exception, e:
            Pago.query.session.rollback()
            yield MessageBox("Se ha producido un error:\n\n%s" % e,
                             icon=QMessageBox.Critical,
                             title="Imputar carrito",
                             standard_buttons=QMessageBox.Ok)
            yield UpdateObject(model_context.session)
            return
        Pago.query.session.commit()
        obj.aplicada = True
        yield FlushSession(model_context.session)


    def get_state(self, model_context):
        """Habilitar la accion solamente si nunca fueron aplicados"""
        state = super(AplicarPlanilla, self).get_state(model_context)
        obj = model_context.get_object()
        state.enabled = True if obj and not obj.aplicada else False
        return state

class PagoCredito(Entity):
    using_options(tablename='pago_credito')
    planilla_pagos = ManyToOne('PlanillaPagos', ondelete='cascade', onupdate='cascade', primary_key=True)
    credito = ManyToOne('Credito', ondelete='cascade', onupdate='cascade', primary_key=True)
    monto = Field(Float)
    asistencia = ManyToOne('Asistencia', ondelete='cascade', onupdate='cascade')

    class Admin(EntityAdmin):
        list_display = ['credito', 'monto', 'asistencia']
        field_attributes = dict(credito = dict(name = u'Crédito'))

        # esto es para que se refresque el campo total_pagos
        def get_depending_objects(self, obj):
            yield obj.planilla_pagos

class PlanillaPagos(Entity):
    using_options(tablename='planilla_pagos')
    fecha = Field(Date, primary_key=True)
    barrio = ManyToOne('Barrio', ondelete='cascade', onupdate='cascade', primary_key=True)
    creditos = OneToMany('PagoCredito')
    aplicada = Field(Boolean, default=False)

    def __unicode__(self):
        return "%s %s" % (self.fecha, self.barrio.nombre)

    # No uso ColumnProperty para que se refresque automaticamente cuando se modifican los totales
    @property
    def total_pagos(self):
        total = 0
        for i in self.creditos:
            if i.monto:
                total += i.monto
        return total

    class Admin(EntityAdmin):
        verbose_name = u'Planilla de Pagos'
        verbose_name_plural = u'Planillas de Pagos'
        form_display = ['fecha',
                        'barrio',
                        'creditos',
                        'total_pagos',
                        ]
        list_display = ['fecha', 'barrio', 'aplicada']
        form_actions = [BuscarCreditos(),
                        AplicarPlanilla(),
                        ]
        list_filter = [ValidDateFilter('fecha', 'fecha', 'Fecha', default=lambda:''),
                       ComboBoxFilter('barrio.nombre'),
                       ]
        field_attributes = dict(aplicada = dict(editable = False),
                                creditos = dict(name = u'Créditos'),
                                total_pagos = dict(delegate = CurrencyDelegate,
                                                   prefix = '$',
                                                   editable = False),)

        def get_query(self):
            """Redefino para devolver ordenado por fecha desc"""
            return EntityAdmin.get_query(self).order_by(desc('fecha'))

