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

from camelot.view.art import Icon
from camelot.admin.action import OpenNewView
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section
import PyQt4
import os

import model
import view
import m2000

class MyApplicationAdmin(ApplicationAdmin):
    name = u'Mujeres 2000 - Gesti�n de Cr�ditos'
    application_url = 'http://www.mujeres2000.org.ar'
    version = m2000.__version__

    def get_about(self):
        html = """<html><b>Mujeres 2000</b><br>
                        Gesti&oacute;n de Cr&eacute;ditos<br><br>
                        versi&oacute;n _version_<br>
                  </html>"""
        return html.replace('_version_', self.version)

    def get_icon(self):
        return Icon('32x32icon.png', m2000).getQIcon()

    def get_splashscreen(self):
        return PyQt4.QtGui.QPixmap('media/splashscreen.png')
        
    def get_sections(self):
        # from camelot.model.memento import Memento
        # from camelot.model.i18n import Translation
        
        return [
                Section(u'D�a a D�a',
                        self,
                        Icon('tango/22x22/actions/appointment-new.png'),
                        items = [
                                 model.Beneficiaria,
                                 model.Credito,
                                 model.Pago,
                            ]),
                Section(u'Indicadores',
                        self,
                        Icon('tango/22x22/mimetypes/x-office-spreadsheet.png'),
                        items = [
                                 view.IntervaloFechas(),
                                 view.Indicadores,
                            ]),
                Section(u'Recaudaci�n',
                        self,
                        Icon('tango/22x22/mimetypes/x-office-spreadsheet.png'),
                        items = [
                                 view.IntervaloFechas(),
                                 view.RecaudacionMensual,
                                 view.RecaudacionRealTotal,
                                 view.RecaudacionPotencialTotal,
                                 view.RecaudacionRealTotalPorBarrio,
                                 view.RecaudacionPotencialTotalPorBarrio,
                            ]),
                Section(u'Cartera',
                        self,
                        Icon('tango/22x22/mimetypes/x-office-spreadsheet.png'),
                        items = [
                                 view.IntervaloFechas(),
                                 view.ChequesEntregados,
                                 view.CreditosActivos,
                                 view.PerdidaPorIncobrable,
                                 view.CreditosFinalizadosSinSaldar,
                            ]),
                Section(u'Configuraci�n',
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
                # Section('configuration',
                #         Icon('tango/22x22/categories/preferences-system.png'),
                #         items = [Memento, Translation]),
                ]

    def get_help_url(self):
        return PyQt4.QtCore.QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), os.path.pardir, 'doc', 'index.html'))

    def get_actions(self):
        new_pago_action = OpenNewView(self.get_related_admin(model.Pago))
        new_pago_action.icon = Icon('tango/32x32/actions/list-add.png')
        return [new_pago_action]
    
    # override this method to get my own main window instead of camelot's
    # def get_main_window():
    #     pass

    def get_translator(self):
        # Camelot-11.11.16 no tiene translations en es_AR, descomentar para la proxima version de camelot
        # camelot_translator = self._load_translator_from_file( 'camelot', 
        #                                                       'camelot',
        #                                                       'art/translations/es_AR/LC_MESSAGES/')
        camelot_translator = self._load_translator_from_file( 'm2000', 
                                                              'camelot',
                                                              'translations/')
        return [camelot_translator]

    # def get_stylesheet(self):
    #     from camelot.view import art
    #     return art.read(os.path.join('stylesheet', 'office2007_blue.qss'))
