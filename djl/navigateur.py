# -*- coding: utf-8 -*-*

#djl (Dépot jeux Linux)
#Copyright (C) 2008-2009 Florian Joncour - Diablo150 <diablo151@wanadoo.fr
#
#This file is part of djl (Dépot jeux Linux)
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

#Ce fichier contient un mini navigateur (requiert >=qt 4.4) pour afficher certaines pages dans djl
#(n'a pas vocation à remplacer firefox, juste à afficher des pages uniques en html)

'''Mini navigateur internet djlfox, qui se base sur QtWebKit'''

from PyQt4 import QtCore, QtGui
#import threading

try:
    from PyQt4 import QtWebKit
except:
    print "Qt 4.4 requis"

import socket, os

class Ui_navigateur(QtGui.QWidget):
    def __init__(self, parent=None, lien = "www.jeuxlinux.fr"):
        '''Init du navigateur djlfox, qui se base sur QtWebKit'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)

        self.lien=lien
        
        socket.setdefaulttimeout(None)
        self.setupUi(self)
        
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.close)

        #print ">"+lien + "<"
        self.webView.load(QtCore.QUrl(self.lien)) #Charge la page ici

    def setupUi(self, Form):
        '''Envoi l'affichage de l'interface'''
        Form.setObjectName("Form")
        x, y = 980, 700
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,x,y).size()).expandedTo(Form.minimumSizeHint()))

        Form.setMinimumSize(QtCore.QSize(x,y))
        Form.setMaximumSize(QtCore.QSize(x,y))
        
        icone = QtGui.QIcon((os.getcwd() + '/icone.png'))
        Form.setWindowIcon(icone)
        
        self.webView = QtWebKit.QWebView(self)
        self.webView.setGeometry(QtCore.QRect(0,0,x,y))
        self.webView.setWindowModality(QtCore.Qt.NonModal)
        #self.webView.setUrl(QtCore.QUrl(self.lien))
        self.webView.setTextSizeMultiplier(1.0)
        self.webView.setObjectName("webView")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        '''Affiche le texte'''
        Form.setWindowTitle("djlfox")
