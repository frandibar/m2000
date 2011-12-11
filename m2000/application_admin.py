# coding=utf8

from camelot.view.art import Icon
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section
import PyQt4

import model
import reports

class MyApplicationAdmin(ApplicationAdmin):
    name = u'Mujeres 2000 - Gestión de Créditos'
    application_url = 'http://www.mujeres2000.org.ar'
    version = '0.1'

    def get_about(self):
        html = """<html><b>Mujeres 2000</b><br>
                        Gesti&oacute;n de Cr&eacute;ditos<br><br>
                        versi&oacute;n _version_<br>
                  </html>"""
        return html.replace('_version_', self.version)

    # FIXME no anda
    # def get_icon(self):
    #     return Icon('media/32x32icon.png')

    # FIXME transparencia
    # TODO agrandar para dar lugar a los mensajes
    def get_splashscreen(self):
        return PyQt4.QtGui.QPixmap('media/splashscreen.png')
        
    def get_sections(self):
        # from camelot.model.memento import Memento
        # from camelot.model.authentication import Person, Organization
        # from camelot.model.i18n import Translation
        
        return [
                # Section('relation',
                #         Icon('tango/22x22/apps/system-users.png'),
                #         items = [Person, Organization]),
                # Section('configuration',
                #         Icon('tango/22x22/categories/preferences-system.png'),
                #         items = [Memento, Translation]),

                Section(u'Día a Día',
                        self,
                        Icon('tango/22x22/actions/appointment-new.png'),
                        items = [
                                 model.Beneficiaria,
                                 # model.CargaSemanal,
                                 model.Credito,
                                 model.Pago,
                            ]),
                Section(u'Reportes...',
                        self,
                        Icon('tango/22x22/mimetypes/x-office-spreadsheet.png'),
                        items = [
                                 model.IntervaloFechas(),
                                 model.Indicadores,
                                 model.PerdidaPorIncobrable,
                                 model.CreditosFinalizadosSinSaldar,
                            ]),
                Section(u'Recaudación',
                        self,
                        Icon('tango/22x22/mimetypes/x-office-spreadsheet.png'),
                        items = [
                                 model.RecaudacionMensual,
                                 model.RecaudacionRealTotal,
                                 model.RecaudacionPotencialTotal,
                                 model.RecaudacionRealTotalPorBarrio,
                                 model.RecaudacionPotencialTotalPorBarrio,
                            ]),
                Section(u'Cartera',
                        self,
                        Icon('tango/22x22/mimetypes/x-office-spreadsheet.png'),
                        items = [
                                 model.ChequesEntregados,
                                 model.CreditosActivos,
                            ]),
                Section(u'Configuración',
                        self,
                        Icon('tango/22x22/categories/preferences-system.png'),
                        items = [
                                 model.Actividad,
                                 model.Amortizacion,
                                 model.Asistencia,
                                 model.Barrio,
                                 model.Cartera,
                                 model.Ciudad,
                                 model.DomicilioPago,
                                 model.EstadoCredito,
                                 model.Provincia,
                                 model.Rubro,
                            ]),
                # Section('Vistas',
                #         Icon('tango/22x22/categories/preferences-system.png'),
                #         items = [view.Formulario(), view.Coordinate]),
                ]

    # override this method to get my own main window instead of camelot's
    # def get_main_window():
    #     pass

    # def get_translator(self):
    #     trans = ApplicationAdmin.get_translator(self)
    #     return trans
