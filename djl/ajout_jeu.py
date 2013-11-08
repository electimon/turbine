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

'''Boite de dialogue pour créer un raccourci .desktop vers un jeu déjà installé sur le système'''

import os

from PyQt4 import QtCore, QtGui
from variables import variables, home
from config import config
import i18n

#dossier_racine = os.getcwd()
#home = os.path.expanduser('~')


class Ui_ajout_jeu(QtGui.QWidget):

    def __init__(self, parent=None, _fichier="", _nom="", _icone="", _cmd="", _repertoire=home):
        '''Ajout d'un jeu déjà installé sur le système via un raccourci'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)

        self.fichier = _fichier

        self.setupUi(self, parent, _nom, _icone, _cmd, _repertoire)

        self.font = QtGui.QFont()
        self.font.setPointSize(config(info=15))
        self.setFont(self.font)

        self.bouton_sauver.connect(self.bouton_sauver, QtCore.SIGNAL("clicked()"), self.sauver)
        self.bouton_parcourir_cmd.connect(
            self.bouton_parcourir_cmd,
            QtCore.SIGNAL("clicked()"),
            self.parcours_cmd)
        self.bouton_parcourir_ico.connect(
            self.bouton_parcourir_ico,
            QtCore.SIGNAL("clicked()"),
            self.parcours_ico)
        self.bouton_parcourir_rep.connect(
            self.bouton_parcourir_rep,
            QtCore.SIGNAL("clicked()"),
            self.parcours_rep)

        # Raccourcis clavier pour fermer la fenêtre quand l'on appuis sur la touche echapement:
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.close)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self, self.sauver)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter), self, self.sauver)

    def sauver(self):
        '''Sauvegarde le raccourci'''
        # Si l'utilisateur ne donne pas un nom de jeu, on ne sauvegarde pas:
        if self.nom_jeu.text() == '':
            self.close()
        # Sinon, on sauvegarde
        else:
            # Enregistre les données dans un fichier .desktop standard:
            if self.fichier == "":
                fichier = open(
                    config(info=2) + '/raccourcis/' +
                    unicode(self.nom_jeu.text()).encode('utf-8').lower() + '.desktop',
                    'w')
            else:
                # Si le raccourci existe déjà, on réécrit par dessus, plutot que créer un
                # nouveau fichier
                fichier = open(config(info=2) + '/raccourcis/' + self.fichier, 'w')

            fichier.write('[Desktop Entry]' + '\n')
            fichier.write('Name=' + self.nom_jeu.text() + '\n')
            fichier.write('Icon=' + self.icone.text() + '\n')
            fichier.write('Exec=' + self.cmd_jeu.text() + '\n')
            fichier.write('Path=' + self.rep_jeu.text() + '\n')
            fichier.write('Type=Application')
            fichier.close()

            # Créé le fichier temporaire pour demander le rafraichissement de
            # l'interface principale:
            self.creer_fichier_maj()
            # Ferme la fenêtre:
            self.ferme()

    def ferme(self):
        '''Ferme la fenêtre'''
        variables.maj_listejeux = True
        self.close()

    def creer_fichier_maj(self):
        '''Créé un fichier temporaire pour demander le rafraichissement de l'interface principale'''
        fichier = home + '/.djl/maj_liste'
        fichier = open(fichier, 'w')
        fichier.close()

    def parcours_cmd(self):
        '''Affiche une boite de dialogue pour choisir le chemin vers le binaire'''
        if self.cmd_jeu.text() == "":
            commande = QtGui.QFileDialog.getOpenFileName(self, "", home)
        else:
            if "C:\\" in self.cmd_jeu.text():
                addresse = home + "/.wine"
            else:
                fichier = self.cmd_jeu.text().split('/')[-1]
                addresse = self.cmd_jeu.text().replace(fichier, "")
            commande = QtGui.QFileDialog.getOpenFileName(self, "", addresse)

        if commande == "":
            return
        else:
            self.cmd_jeu.setText(commande)

    def parcours_ico(self):
        '''Affiche une boite de dialogue pour choisir le chemin vers l'icone'''
        if self.icone.text() == "":
            icone = QtGui.QFileDialog.getOpenFileName(self, "", home)
        else:
            if "C:\\" in self.icone.text():
                addresse = home + "/.wine"
            else:
                fichier = self.icone.text().split('/')[-1]
                addresse = self.icone.text().replace(fichier, "")
            icone = QtGui.QFileDialog.getOpenFileName(self, "", addresse)

        if icone == "":
            return
        else:
            self.icone.setText(icone)

    def parcours_rep(self):
        '''Affiche une boite de dialogue pour choisir le chemin vers le répertoire de lancement'''
        if self.rep_jeu.text() == "":
            rep = QtGui.QFileDialog.getExistingDirectory(self, "", home)
        else:
            if "C:\\" in self.rep_jeu.text():
                addresse = home + "/.wine"
            else:
                fichier = self.rep_jeu.text().split('/')[-1]
                addresse = self.rep_jeu.text().replace(fichier, "")
            rep = QtGui.QFileDialog.getExistingDirectory(self, "", addresse)

        if rep == "":
            return
        else:
            self.rep_jeu.setText(rep)

    def setupUi(self, Dialog, parent, _nom, _icone, _cmd, _repertoire):
        '''Envoi le dessin de l'interface'''
        Dialog.setObjectName("Dialog")
        x, y = 370, 150
        Dialog.resize(QtCore.QSize(QtCore.QRect(0, 0, x, y).size())
                      .expandedTo(Dialog.minimumSizeHint()))

        Dialog.setMinimumSize(QtCore.QSize(x, y))
        Dialog.setMaximumSize(QtCore.QSize(x, y))

        # Place de fenêtre au centre de la fenêtre principale
        posx = parent.pos().x() + parent.width() / 2
        posy = parent.pos().y() + parent.height() / 2
        self.move(posx - (x / 2), posy - (y / 2))
        #/

        icone = QtGui.QIcon((os.getcwd() + '/icone.png'))
        Dialog.setWindowIcon(icone)

        self.bouton_parcourir_ico = QtGui.QPushButton(Dialog)
        self.bouton_parcourir_ico.setGeometry(QtCore.QRect(270, 30, 100, 27))
        self.bouton_parcourir_ico.setObjectName("bouton_parcourir_ico")

        l = 120
        self.nom_jeu = QtGui.QLineEdit(Dialog)
        self.nom_jeu.setGeometry(QtCore.QRect(120, 0, 251, 28))
        self.nom_jeu.setObjectName("nom_jeu")
        self.nom_jeu.setText(_nom)

        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(0, 0, l, 31))
        self.label.setObjectName("label")

        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(0, 30, l, 31))
        self.label_3.setObjectName("label_3")

        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(0, 60, l, 31))
        self.label_4.setObjectName("label_4")

        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(0, 90, l, 31))
        self.label_5.setObjectName("label_5")

        self.rep_jeu = QtGui.QLineEdit(Dialog)
        self.rep_jeu.setGeometry(QtCore.QRect(120, 90, 151, 28))
        self.rep_jeu.setObjectName("rep_jeu")
        self.rep_jeu.setText(_repertoire)

        self.bouton_parcourir_rep = QtGui.QPushButton(Dialog)
        self.bouton_parcourir_rep.setGeometry(QtCore.QRect(270, 90, 100, 27))
        self.bouton_parcourir_rep.setObjectName("bouton_parcourir_rep")

        self.icone = QtGui.QLineEdit(Dialog)
        self.icone.setGeometry(QtCore.QRect(120, 30, 151, 28))
        self.icone.setObjectName("icone")
        self.icone.setText(_icone)

        self.cmd_jeu = QtGui.QLineEdit(Dialog)
        self.cmd_jeu.setGeometry(QtCore.QRect(120, 60, 151, 28))
        self.cmd_jeu.setObjectName("cmd_jeu")
        self.cmd_jeu.setText(_cmd)

        self.bouton_parcourir_cmd = QtGui.QPushButton(Dialog)
        self.bouton_parcourir_cmd.setGeometry(QtCore.QRect(270, 60, 100, 27))
        self.bouton_parcourir_cmd.setObjectName("bouton_parcourir_cmd")

        self.bouton_sauver = QtGui.QPushButton(Dialog)
        self.bouton_sauver.setGeometry(QtCore.QRect(50, 120, 270, 27))
        self.bouton_sauver.setObjectName("bouton_sauver")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        '''Affiche le texte dans l'interface'''
        Dialog.setWindowTitle(i18n.traduc("Ajouter un raccourci"))
        self.bouton_parcourir_ico.setText(i18n.traduc("Parcourir..."))
        self.bouton_parcourir_rep.setText(i18n.traduc("Parcourir..."))
        self.label.setText(i18n.traduc("Nom du jeu:"))
        #self.label_2.setText("Version (optionnel):")
        self.label_3.setText(i18n.traduc("Icone:"))
        self.label_4.setText(i18n.traduc("Commande du jeu:"))
        self.label_5.setText(i18n.traduc("Repertoire") + ":")
        self.bouton_parcourir_cmd.setText(i18n.traduc("Parcourir..."))
        self.bouton_sauver.setText(i18n.traduc("Sauvegarder et fermer"))
