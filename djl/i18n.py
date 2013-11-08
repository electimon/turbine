# -*- coding: utf-8 -*-*

# djl (Dépot jeux Linux)
# Copyright (C) 2008-2009 Florian Joncour - Diablo150 <diablo151@wanadoo.fr
#
# This file is part of djl (Dépot jeux Linux)
#
# djl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# djl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''Code pour la localisation de djl (i18n)'''

import gettext
import os
import locale
import sys
from config import config
from PyQt4 import QtGui

home = os.path.expanduser('~')
dossier_racine = os.getcwd()

# Si le fichier de configuration n'existe pas (premier lancement de djl)
# On se base sur la langue du système.


def i18n_init():
    if not os.path.exists(home + '/.djl/config'):
        try:
            lang = gettext.translation(
                domain="messages",
                localedir=os.getcwd() + '/i18n',
                languages=[str(locale.getdefaultlocale()[0])])
            lang.install()
        except:
            lang = gettext.translation(
                domain="messages",
                localedir=os.getcwd() + '/i18n',
                languages=['en_US'])
            lang.install()
    else:
    # Sinon, on utilise la langue choisie dans la configuration.
        try:
            langue = str(config(info=9))
            lang = gettext.translation(
                domain="messages",
                localedir=dossier_racine + '/i18n',
                languages=[langue])
            lang.install()
        # Si ça merde, on prend la langue par défaut, l'Anglais
        except:
            try:
                lang = gettext.translation(
                    domain="messages",
                    localedir=dossier_racine + '/i18n',
                    languages=['en_US'])
                lang.install()
            except IOError:
                # Si ça merde encore, on redémarre depuis le début (djl.py s'occupera de
                # télécharger les fichiers manquants):
                os.system('python djl.py')
                sys.exit()

i18n_init()

try:
    _
except NameError:
    def _(s):
        return s


def encode(texte):
    '''Encode une chaine de caractère en unicode avec Qt et la retourne'''
    return QtGui.QApplication.translate("MainWindow", texte, None, QtGui.QApplication.UnicodeUTF8)


def traduc_ascii(s):
    '''Renvoi la traduction d'une chaine sans la conversion en unicode'''
    return _(s)


def traduc(s):
    '''Renvoi la traduction d'une chaine et la converti en utf-8'''
    return encode(_(s))
