# coding=utf8

# working without the default model
# http://downloads.conceptive.be/downloads/camelot/doc/sphinx/build/doc/under_the_hood.html
# copied from /usr/lib/python2.7/dist-packages/camelot/model/__init__.py
# begin session setup
import elixir
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, create_session
elixir.session = scoped_session( create_session )
import settings

metadata = MetaData()
__metadata__ = metadata
__metadata__.bind = settings.ENGINE()
__metadata__.autoflush = False
__metadata__.transactional = False
# end session setup


# begin meta data setup
# from camelot.model import metadata
# __metadata__ = metadata
# end meta data setup

from PyQt4 import QtGui
from camelot.admin.action.base import Action
from camelot.admin.entity_admin import EntityAdmin
from camelot.admin.not_editable_admin import notEditableAdmin
from camelot.admin.object_admin import ObjectAdmin
from camelot.admin.validator.object_validator import ObjectValidator
from camelot.admin.validator.entity_validator import EntityValidator
from camelot.view import forms
from camelot.view.action_steps import ChangeObject, FlushSession, UpdateProgress, Refresh
from camelot.view.art import ColorScheme
from camelot.view.controls.delegates import DateDelegate, FloatDelegate, BoolDelegate, NoteDelegate, CurrencyDelegate, IntegerDelegate
from camelot.view.filters import ComboBoxFilter, ValidDateFilter, GroupBoxFilter
from camelot.view.forms import Form, TabForm, WidgetOnlyForm, HBoxForm, VBoxForm
from elixir import Entity, Field, using_options, ManyToOne, OneToMany, OneToOne
from elixir.properties import ColumnProperty
from sqlalchemy import Unicode, Date, Boolean, Integer, Float
from sqlalchemy import sql, and_
import camelot
import sqlalchemy

import datetime

import reports
import constants

# used in __unicode__()
UNDEFINED = '[indefinido]'

class RubroAdminEmbedded(EntityAdmin):
    verbose_name = 'Rubro'
    list_display = ['nombre']
    list_action = None

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
                                rubros = dict(embedded = True,
                                              admin = RubroAdminEmbedded))
        list_search = ['nombre', 'amortizacion.nombre', 'rubros.nombre']

    def __unicode__(self):
        return self.nombre or UNDEFINED

class Rubro(Entity):
    using_options(tablename='rubro')
    nombre = Field(Unicode(200), required=True)
    actividad = ManyToOne('Actividad', ondelete='cascade', onupdate='cascade')

    class Admin(EntityAdmin):
        verbose_name = 'Rubro'
        list_display = ['nombre', 'actividad']
        list_action = None
        list_search = ['nombre', 'actividad.nombre']
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
        form_size = (450,150)

    def __unicode__(self):
        return self.nombre or UNDEFINED


class PagoAdminBase(EntityAdmin):
    verbose_name = 'Pago'
    list_display = ['credito',
                    'fecha',
                    'monto',
                    'asistencia']
    field_attributes = dict(credito = dict(name = u'Crédito'),
                            monto = dict(prefix = '$'))
    search_all_fields = False
    list_search = ['credito.beneficiaria.nombre',
                   'credito.beneficiaria.apellido',
                   ]
    list_action = None

class PagoAdminEmbedded(PagoAdminBase):
    list_display = filter(lambda x: x not in ['credito'], PagoAdminBase.list_display)


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
    list_display = ['beneficiaria',
                    'nro_credito',
                    'rubro',
                    '_fecha_entrega',
                    'fecha_cobro',
                    '_prestamo',
                    '_saldo_anterior',
                    'monto_cheque',
                    '_tasa_interes',
                    'deuda_total',
                    'cartera',
                    'cuotas',
                    'fecha_finalizacion',
                    'comentarios',
                    'gastos_arq',
                    ]

    list_search = ['beneficiaria.nombre',
                   'beneficiaria.apellido',
                   'beneficiaria.barrio.nombre',
                   'rubro.nombre',
                   'cartera.nombre',
                   ]
    search_all_fields = False
    # TODO no me toma los campos referenciados
    expanded_list_search = ['beneficiaria.nombre', 
                            'beneficiaria.apellio', 
                            'rubro.nombre', 
                            'nro_credito', 
                            'fecha_entrega',
                            'fecha_cobro', 
                            'fecha_finalizacion', 
                            'prestamo',
                            'cartera.nombre']
    list_filter = ['activo',
                   ComboBoxFilter('cartera.nombre'),
                   ValidDateFilter('_fecha_entrega', 'fecha_finalizacion', u'Período e/entrega-fin', default=lambda:'')]

    # ArgumentError: Can't find any foreign key relationships between 'barrio' and '_FromGrouping object'.
    # Perhaps you meant to convert the right side to a subquery using alias()?
    # list_filter = [ComboBoxFilter('beneficiaria.barrio.id')]  # TODO no anda

    def _use_gastos_arq(obj):
        try:
            if obj.rubro:
                return obj.rubro.actividad.id == constants.ID_ACTIVIDAD_CONSTRUCCION
        except Exception, e:
            pass
        return True

    field_attributes = dict(beneficiaria = dict(minimal_column_width = 25),
                            rubro = dict(minimal_column_width = 20),
                            _prestamo = dict(name = u'Préstamo',
                                             prefix = '$',
                                             delegate = CurrencyDelegate,
                                             editable = True),
                            _tasa_interes = dict(name = u'Tasa de interés',
                                                 delegate = FloatDelegate,
                                                 editable = True),
                            nro_credito = dict(name = u'Crédito #'),
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
                            _saldo_anterior = dict(name = 'Saldo Anterior',
                                                   prefix = '$',
                                                   delegate = CurrencyDelegate,
                                                   editable = True),
                            deuda_total = dict(prefix = '$',
                                               tooltip = u'En principio equivale a: Préstamo . (1 + Tasa de interés)'),
                            activo = dict(delegate = BoolDelegate,
                                          to_string = lambda x:{1:'True', 0:'False'}[x]),
                            pagos = dict(admin = PagoAdminEmbedded),
                            _fecha_entrega = dict(delegate = DateDelegate,
                                                  name = 'Fecha entrega',
                                                  minimal_column_width = 17,
                                                  editable = True),
                            fecha_cobro = dict(minimal_column_width = 17,
                                               tooltip = u'Al modificar la fecha de entrega, este campo toma el valor de la fecha de entrega más 2 dias.'),
                            # TODO por el momento el name es estatico, no se puede cambiar en funcion de otros valores
                            # monto_cheque = dict(name = lambda o: 'Monto Presupuesto' if o.rubro.actividad.id == constants.ID_ACTIVIDAD_CONSTRUCCION else 'Monto Cheque'),
                            monto_cheque = dict(name = 'Monto Cheque/Presup.',
                                                prefix = '$',
                                                tooltip = u'En principio equivale a: Préstamo - Saldo anterior'),
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
    foto = Field(camelot.types.Image(upload_to='fotos')) # TODO no anda con default='sin-foto.jpg')
    # foto = Field(camelot.types.Image(upload_to='fotos'), default='sin-foto.jpg')
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

    class Admin(EntityAdmin):
        verbose_name = 'Beneficiaria'
        list_columns_frozen = 1
        lines_per_row = 1
        list_display = ['apellido',
                        'nombre',
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

        form_display = TabForm([
          ('Beneficiaria', Form([
                HBoxForm([['nombre', 
                           'apellido', 
                           'barrio', 
                           'grupo', 
                           '_activa',
                           'fecha_alta',
                           'fecha_baja',
                           'comentarios',
                           ], 
                          [#WidgetOnlyForm('foto'),
                           'dni',
                           'fecha_nac',
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
                       ComboBoxFilter('grupo')]
        search_all_fields = False
        list_search = ['apellido',
                       'nombre',
                       'comentarios',
                       'dni',
                       'grupo',
                       'barrio.nombre',
                       ]
                       
        expanded_list_search = ['apellido',
                                'nombre',
                                'fecha_alta',
                                'fecha_baja',
                                'comentarios',
                                'dni',
                                'fecha_nac',
                                'barrio.nombre',
                                ]

        field_attributes = dict(fecha_baja = dict(name = 'Fecha Baja',
                                                  tooltip = u'Al desactivar la beneficiaria, este campo toma la última fecha de pago'),
                                dni = dict(name = 'DNI'),
                                fecha_alta = dict(name = 'Fecha Alta'),
                                fecha_nac = dict(name = 'Fecha Nac.'),
                                estado_civil = dict(name = 'Estado Civil'),
                                telefono = dict(name = u'Teléfono'),
                                email = dict(address_type = 'email'),
                                creditos = dict(admin = CreditoAdminEmbedded),
                                _activa = dict(name = 'Activa',
                                               delegate = BoolDelegate,
                                               editable = True,
                                               tooltip = u'No se puede dar de baja una beneficiaria si tiene créditos activos.'),
                                creditos_activos = dict(name = u'Créditos activos',
                                                        editable = False),
                               )

        form_size = (850,400)
        # TODO: comentado porque rompe los filtros y pierdo los delegates
        # def get_field_attributes(self, field_name):
        #     field_attributes = super(EntityAdmin, self).get_field_attributes(field_name)
        #     if field_name == 'fecha_baja':
        #         field_attributes['editable'] = lambda x: not x.activa
        #     else:
        #         field_attributes['editable'] = True
        #     return field_attributes

    @ColumnProperty
    def creditos_activos(self):
        return sql.select([sql.func.count(Credito.id)],
                          and_(Credito.beneficiaria_id == Beneficiaria.id,
                               sql.column('fecha_finalizacion') == sql.null()))

    def __unicode__(self):
        if self.nombre and self.apellido:
            return '%s %s' % (self.nombre, self.apellido)
        return UNDEFINED
    
class Cartera(Entity):
    using_options(tablename='cartera')
    nombre = Field(Unicode(200), unique=True, required=True)

    class Admin(EntityAdmin):
        verbose_name = 'Cartera'
        list_display = ['nombre']
        list_action = None
        form_size = (450,100)

    def __unicode__(self):
        return self.nombre or UNDEFINED
        

class Credito(Entity):
    using_options(tablename='credito')
    beneficiaria = ManyToOne('Beneficiaria', ondelete='cascade', onupdate='cascade', required=True)
    # rubro = ManyToOne('Rubro', ondelete='cascade', onupdate='cascade', required=True)
    fecha_entrega = Field(Date, required=True)
    fecha_cobro = Field(Date, required=True)
    prestamo = Field(Float)
    saldo_anterior = Field(Float)
    monto_cheque = Field(Float)
    tasa_interes = Field(Float)
    deuda_total = Field(Float)
    # cartera = ManyToOne('Cartera', ondelete='cascade', onupdate='cascade', required=True)
    cuotas = Field(Integer, required=True)
    nro_credito = Field(Unicode(15), required=True)
    fecha_finalizacion = Field(Date)
    comentarios = Field(Unicode(1000))
    gastos_arq = Field(Float)
    # pagos = OneToMany('Pago')

    class Admin(EntityAdmin):
        verbose_name = u'Crédito'
        list_display = ['beneficiaria',
                        #'rubro',
                        'nro_credito',
                        'fecha_cobro',
                        #'cartera',
                        'cuotas',
                        ]

class XXXCredito(Entity):
    # using_options(tablename='credito')
    beneficiaria = ManyToOne('Beneficiaria', ondelete='cascade', onupdate='cascade', required=True)
    rubro = ManyToOne('Rubro', ondelete='cascade', onupdate='cascade', required=True)
    fecha_entrega = Field(Date, required=True)
    fecha_cobro = Field(Date, required=True)
    prestamo = Field(Float)
    saldo_anterior = Field(Float)
    monto_cheque = Field(Float)
    tasa_interes = Field(Float)
    deuda_total = Field(Float)
    cartera = ManyToOne('Cartera', ondelete='cascade', onupdate='cascade', required=True)
    cuotas = Field(Integer, required=True)
    nro_credito = Field(Unicode(15), required=True)
    fecha_finalizacion = Field(Date)
    comentarios = Field(Unicode(1000))
    gastos_arq = Field(Float)
    # pagos = OneToMany('Pago')

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

    class Admin(CreditoAdminBase):
        pass

        # # # TODO: comentado porque rompe los filtros y pierdo los delegates
        # def get_field_attributes(self, field_name):
        #     field_attributes = super(EntityAdmin, self).get_field_attributes(field_name)
        #     # if field_name == 'gastos_arq':
        #     #     field_attributes['editable'] = lambda x: x.rubro.actividad == 8   # 8 -> id construccion
        #     # else:
        #     #     field_attributes['editable'] = True
        #     return field_attributes
    
    @ColumnProperty
    def activo(self):
        return sql.select([sql.column('fecha_finalizacion') == sql.null()])

    @ColumnProperty
    def total_pagos(self):
        return sql.select([sql.func.sum(Pago.monto)],
                          and_(Pago.credito_id == self.id))

    @property
    def para_construccion(self):
        if self.rubro:
            return self.rubro.actividad_id == constants.ID_ACTIVIDAD_CONSTRUCCION
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


class EstadoCredito(Entity):
    using_options(tablename='estado_credito')
    descripcion = Field(Unicode(200), unique=True, required=True)
    cuotas_adeudadas = Field(Integer, required=True)

    class Admin(EntityAdmin):
        verbose_name = u'Estado de Crédito'
        verbose_name_plural = u'Estado de Créditos'
        list_display = ['descripcion',
                        'cuotas_adeudadas']
        field_attributes = { 'descripcion': { 'name': u'Descripción' } }
        list_action = None

    def __unicode__(self):
        return self.descripcion or UNDEFINED


class Fecha(Entity):
    using_options(tablename='fecha')
    fecha = Field(Date, primary_key=True)

    def __unicode__(self):
        return self.fecha

class Pago(Entity):
    using_options(tablename='pago')
    credito = ManyToOne('Credito', primary_key=True, ondelete='cascade', onupdate='cascade')
    monto = Field(Float)
    fecha = Field(Date, primary_key=True)
    asistencia = ManyToOne('Asistencia', ondelete='cascade', onupdate='cascade')

    class Admin(PagoAdminBase):
        verbose_name = 'Pago'
        list_display = ['credito',
                        'fecha',
                        'monto',
                        'asistencia']
        field_attributes = dict(credito = dict(name = u'Crédito'),
                                monto = dict(prefix = '$'))
        list_filter = [ValidDateFilter('fecha', 'fecha', 'Fecha', default=lambda:'')]
        
        # list_filter = [ComboBoxFilter('fecha')]

        # field_attributes = dict(credito = dict(name = u'Crédito',
        #                                        editable = False),
        #                         fecha = dict(editable = False),
        #                         monto = dict(editable = False),
        #                         asistencia = dict(editable = False),
        #                         )
    def __unicode__(self):
        if self.credito:
            return '%s %s (cred. #%s)' % (self.credito.beneficiaria.nombre,
                                          self.credito.beneficiaria.apellido,
                                          self.credito.nro_credito)
        return INDEFINIDO


class Parametro(Entity):
    using_options(tablename='parametro')
    fecha = Field(Date, primary_key=True)

class Amortizacion(Entity):
    using_options(tablename='amortizacion')
    nombre = Field(Unicode(25), unique=True, required=True)

    class Admin(EntityAdmin):
        verbose_name = u'Amortización'
        verbose_name_plural = 'Amortizaciones'
        list_display = ['nombre']
        list_action = None
        form_size = (450,100)

    def __unicode__(self):
        return self.nombre or UNDEFINED

# esta clase corresponde a un VIEW
class Indicadores(Entity):
    using_options(tablename='101_indicadores', autoload=True, allowcoloverride=True)
    # override columns since a primary must be defined
    beneficiaria_id = Field(Integer, primary_key=True)
    nro_credito = Field(Unicode(3), primary_key=True)                         

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
            'diferencia_monto'
            ]

        list_filter = [ComboBoxFilter('barrio')]
        list_columns_frozen = 1
        list_action = None
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
                                                      delegate = IntegerDelegate),
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
    Admin = notEditableAdmin(Admin)

# esta clase corresponde a un VIEW
class RecaudacionMensual(Entity):
    using_options(tablename='700_recaudacion_x_cartera', autoload=True, allowcoloverride=True)
    cartera = Field(Unicode(200), primary_key=True)
    tasa_interes = Field(Float, primary_key=True)
    total_pagos = Field(Float, primary_key=True)
    barrio = Field(Unicode(200), primary_key=True)
    
    class Admin(EntityAdmin):
        verbose_name = u'Recaudación Mensual'
        verbose_name_plural = u'Mensual'
        list_display = ['barrio',
                        'cartera',
                        'tasa_interes',
                        'total_pagos',
                        ]
        
        list_filter = [ComboBoxFilter('barrio'),
                       ComboBoxFilter('cartera'),
                       ]
        list_action = None
        field_attributes = dict(tasa_interes = dict(name = u'Tasa Interés',
                                                    minimal_column_width = 15,
                                                    delegate = FloatDelegate),
                                total_pagos = dict(delegate = CurrencyDelegate,
                                                   prefix = '$'))
    Admin = notEditableAdmin(Admin)


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
    Admin = notEditableAdmin(Admin)


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
        field_attributes = dict(recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                fecha = dict(delegate = DateDelegate),
                                )
    Admin = notEditableAdmin(Admin)

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
        field_attributes = dict(recaudacion = dict(name = u'Recaudación',
                                                   delegate = CurrencyDelegate,
                                                   prefix = '$'),
                                recaudacion_potencial = dict(name = 'Rec. Potencial',
                                                             delegate = CurrencyDelegate,
                                                             prefix = '$'),
                                porcentaje = dict(name = '%',
                                                  delegate = FloatDelegate),
                                )
    Admin = notEditableAdmin(Admin)

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
    Admin = notEditableAdmin(Admin)

# esta clase corresponde a un VIEW
class ChequesEntregados(Entity):
    using_options(tablename='403_creditos_entregados', autoload=True, allowcoloverride=True)
    beneficiaria = Field(Unicode(401), primary_key=True)
    nro_credito = Field(Unicode(3), primary_key=True)
    
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
        list_action = None
        list_filter = [ComboBoxFilter('beneficiaria'),
                       ComboBoxFilter('barrio'),
                       ComboBoxFilter('cartera')]
        field_attributes = dict(fecha_entrega = dict(delegate = DateDelegate),
                                monto_prestamo = dict(delegate = CurrencyDelegate,
                                                      prefix = '$'),
                                monto_cheque = dict(delegate = CurrencyDelegate,
                                                    prefix = '$'),
                                beneficiaria = dict(minimal_column_width = 25))
    Admin = notEditableAdmin(Admin)

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
        list_action = None
        list_filter = [ComboBoxFilter('beneficiaria'),
                       ComboBoxFilter('barrio'),
                       ]
        field_attributes = dict(fecha_entrega = dict(delegate = DateDelegate),
                                prestamo = dict(delegate = CurrencyDelegate,
                                                prefix = '$'),
                                saldo = dict(delegate = CurrencyDelegate,
                                             prefix = '$'),
                                beneficiaria = dict(minimal_column_width = 25))
    Admin = notEditableAdmin(Admin)
    

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
    Admin = notEditableAdmin(Admin)

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
                                comentarios = dict(minimal_column_width = 20),
                                beneficiaria = dict(minimal_column_width = 25),
                                )
    Admin = notEditableAdmin(Admin)

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
        # TODO: como hago esto?
        # form_close_action = camelot.admin.action.OpenTableView(self.app_admin.get_entity_admin(Indicadores))
        
class IntervaloFechas(Action):
    verbose_name = 'Intervalo de fechas'

    def find_friday(self, date, inc):
        day = datetime.timedelta(days=inc)
        while date.weekday() != 4:      # friday is weekday 4
            date += day
        return date

    def model_run(self, model_context):
        # truncate tables
        Parametro.query.delete()
        Fecha.query.delete()

        # ask for date intervals
        fechas = IntervaloFechasDialog()
        yield ChangeObject(fechas)

        desde = self.find_friday(fechas.desde, 1)
        hasta = self.find_friday(fechas.hasta, -1)
        if hasta < desde:
            hasta = desde

        # add to parametro
        p = Parametro()
        p.fecha = desde
        Parametro.query.session.flush()

        # add dates
        week = datetime.timedelta(weeks=1)
        while desde <= hasta:
            f = Fecha()
            f.fecha = desde
            desde += week
            yield UpdateProgress()

        Fecha.query.session.flush()
        yield Refresh()
        # camelot.admin.action.application_action.OpenTableView(self.app_admin.get_entity_admin(Beneficiaria))
        # yield FlushSession(model_context.session)
