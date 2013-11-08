# -*- coding: utf-8 -*-

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

'''Fenêtre d'import de raccourcis .desktop existants'''

from PyQt4 import QtCore, QtGui
import sys
import os
from stat import ST_MODE, S_ISDIR, S_ISREG
import threading
import shutil

from installe import variables
from config import config

home = os.path.expanduser('~')
dossier_racine = os.getcwd()


class Signal:
    signal = 0
    liste = []

import i18n
# i18n.i18n_init()

try:
    _
except NameError:
    def _(s):
        return s


class Ui_Import_Raccourcis(QtGui.QWidget):

    def __init__(self, parent=None, destination=home + "/.djl/raccourcis/"):
        '''Fenêtre d'import des raccourcis existants'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)

        self.destination = destination
        self.setupUi(self, parent)

        self.liens()
        self.affiche_jeux()
        self.lineEdit.setEnabled(True)

        self.font = QtGui.QFont()
        self.font.setPointSize(config(info=15))
        self.setFont(self.font)

    def timerEvent(self, event):
        '''Une fois la première itération du timer terminé, on vérifi si on a terminé de récupérer la liste des raccourcis,
        Si c'est le cas, on l'affiche et on termine le chrono, sinon on continue de vérifier jusqu'a ce que ça se termine'''
        if Signal.signal == 1:
            liste = Signal.liste
            self.liste_raccourcis_copie = liste
            for i in range(len(liste)):
                item = QtGui.QListWidgetItem(self.listWidget)
                item.setIcon(QtGui.QIcon(Signal.liste[i][2]))

                t_ico = 24  # Taille des icones
                self.listWidget.setIconSize(QtCore.QSize(t_ico, t_ico))
                item.setText(Signal.liste[i][1])

                self.listWidget.addItem(item)
            self.timer.stop()

    def setupUi(self, MainWindow, parent):
        '''Envoi l'affichage de la fenêtre'''
        MainWindow.setObjectName("MainWindow")
        x, y = 321, 536
        MainWindow.resize(x, y)
        MainWindow.setMinimumSize(QtCore.QSize(x, y))
        MainWindow.setMaximumSize(QtCore.QSize(x, y))

        # Place de fenêtre au centre de la fenêtre principale
        posx = parent.pos().x() + parent.width() / 2
        posy = parent.pos().y() + parent.height() / 2
        self.move(posx - (x / 2), posy - (y / 2))
        #/

        icone = QtGui.QIcon(dossier_racine + '/icone.png')
        MainWindow.setWindowIcon(icone)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setGeometry(QtCore.QRect(0, 0, 321, 536))
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(30, 505, 121, 27))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(170, 505, 121, 27))
        self.pushButton_2.setObjectName("pushButton_2")
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(0, 60, 321, 441))
        self.listWidget.setObjectName("listWidget")
        self.checkBox = QtGui.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(10, 2, 311, 31))
        self.checkBox.setObjectName("checkBox")
        self.lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(66, 30, 253, 28))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setEnabled(False)

        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(3, 30, 60, 28))
        self.label.setObjectName("label")
        self.label.setText(i18n.traduc("Chercher") + ":")

        # Etat par défaut que la checkbox (Doit on ou non n'afficher que les jeux ?)
        self.checkBox.setChecked(True)

        # MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        '''Envoi le texte de la fenêtre'''
        MainWindow.setWindowTitle(i18n.traduc("Importer un raccourci"))
        self.pushButton.setText(i18n.traduc("Ajouter"))
        self.pushButton_2.setText(i18n.traduc("Fermer"))
        self.checkBox.setText(i18n.traduc("N'afficher que les jeux"))

    def liens(self):
        '''Créé les liens des objets Qt vers les fonctions'''
        self.pushButton.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.ajouter)
        self.pushButton_2.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), self.fermer)
        self.listWidget.connect(
            self.listWidget,
            QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
            self.ajouter)
        self.checkBox.connect(self.checkBox, QtCore.SIGNAL("stateChanged(int)"), self.affiche_jeux)
        self.lineEdit.connect(
            self.lineEdit,
            QtCore.SIGNAL("textEdited(const QString &)"),
            self.filtre_liste)

        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.close)

        #self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.test)

    # def test_import(self):
        # print "---"
        # print "Fichier:", Signal.liste[self.listWidget.currentRow()][0]
        # print "Nom:", Signal.liste[self.listWidget.currentRow()][1]
        # print "Icone:", Signal.liste[self.listWidget.currentRow()][2]
        # print "Commande:", Signal.liste[self.listWidget.currentRow()][3]
        # print "Est ce un jeu ?:", Signal.liste[self.listWidget.currentRow()][4]
        # print "Répertoire:", Signal.liste[self.listWidget.currentRow()][5]
        # print "Destination:",  self.destination
        # print "---"

    def filtre_liste(self):
        '''Filtre la liste des raccourcis à chaque fois que l'on change le texte de la ligne'''
        try:
            Signal.liste = self.liste_raccourcis_copie
        except:
            print "Liste incomplete"
            return

        filtre = str(unicode(self.lineEdit.text()).encode('utf-8'))
        self.listWidget.clear()

        nb_boucle = len(Signal.liste)
        liste_temp = []

        for i in range(nb_boucle):
            if filtre.lower() in Signal.liste[i][1] or filtre.capitalize() in Signal.liste[i][1] or filtre.lower() in Signal.liste[i][0] or filtre.capitalize() in Signal.liste[i][0]:
                item = QtGui.QListWidgetItem(self.listWidget)
                item.setIcon(QtGui.QIcon(Signal.liste[i][2]))

                t_ico = 24  # Taille des icones
                self.listWidget.setIconSize(QtCore.QSize(t_ico, t_ico))
                item.setText(Signal.liste[i][1])

                self.listWidget.addItem(item)

                liste_temp.append(
                    (Signal.liste[i][0],
                     Signal.liste[i][1],
                        Signal.liste[i][2],
                        Signal.liste[i][3],
                        Signal.liste[i][4],
                        Signal.liste[i][5]))
        Signal.liste = liste_temp

    def affiche_jeux(self):
        '''Quand on clique sur la checkbox, on créé une nouvelle liste de raccourcis, avec ou sans filtre de jeux.'''
        self.listWidget.clear()

        self.th_liste = Th_liste_raccourcis(self.checkBox.checkState())
        self.th_liste.start()

        self.timer = QtCore.QBasicTimer()
        self.timer.start(200, self)

    def ajouter(self):
        '''Quand on double clique sur une ligne de la listbox ou quand on clique sur le bouton "Ajouter",
        On copie le raccourcis dans  ~/.djl/config (par defaut) et on met à jour l'interface principale'''

        fichier = Signal.liste[self.listWidget.currentRow()][0]
        # try:
            #fichier = unicode(fichier).encode('utf-8')
        # except:
            # pass

        # Récupère le nom du fichier uniquement:
        nom_fichier = fichier.split('/')
        nom_fichier = nom_fichier[len(nom_fichier) - 1]

        # Copie le raccourcis:
        try:
            try:
                shutil.copyfile(str(fichier), self.destination + str(nom_fichier).lower())
            except UnicodeEncodeError:
                shutil.copyfile(fichier, self.destination + nom_fichier)
        except:
            print "Le fichier .desktop n'a pas été copié"

        # Rafraichi l'interface principale
        variables.maj_listejeux = True

    def fermer(self):
        '''Quand on clique sur fermer'''
        self.close()


class Th_liste_raccourcis(threading.Thread):

    def __init__(self, etat_chbx):
        '''Créé la liste des raccourcis dans un Thread séparé (Ce permet de pas bloquer le dessin de l'interface'''
        threading.Thread.__init__(self)
        self.etat_chbx = etat_chbx

    def run(self):
        '''Au lancement du Thread, on créé la liste...'''
        self.creer_liste_raccourcis()

    def liste_recursive(self, rep):
        '''Parcours récursivement les répertoires pour trouver les icones'''
        for i in os.listdir(rep):
            addr = os.path.join(rep, i)
            mode = os.stat(addr)[ST_MODE]
            if S_ISDIR(mode):  # Si c'est un répertoire, on le parcours récursivement
                self.liste_recursive(addr)
            elif S_ISREG(mode):  # Si c'est un fichier
                # print addr
                if ".desktop" in addr:
                    self.liste_fichier.append(addr)

    def creer_liste_raccourcis(self):
        '''Créé la liste des raccourcis, ils seront affiché dans la listbox'''
        #self.liste_raccourcis = []
        Signal.liste = []
        self.liste_fichier = []

        self.liste_recursive("/usr/share/applications")
        if os.path.exists(home + "/.local/share/applications") == True:
            self.liste_recursive(home + "/.local/share/applications")

        self.liste_fichier.sort()  # Tri la liste

        # Parcours la liste des raccourcis et affiche dans la listwidget:
        for i in range(len(self.liste_fichier)):
            liste_infos = self.lit_fichier_desktop(self.liste_fichier[i])

            if liste_infos is not None:
                # if liste_infos[1] == None: #Si l'icone est Nulle...
                    #liste_infos[1] = 'nul'

                if int(self.etat_chbx) == 2 and liste_infos[3] == 1 or int(self.etat_chbx == 0):
                    Signal.liste.append(
                        (self.liste_fichier[i],
                         liste_infos[0],
                            liste_infos[1],
                            liste_infos[2],
                            liste_infos[3],
                            liste_infos[4]))

        print str(len(Signal.liste)), "Raccourcis."
        Signal.signal = 1

    def lit_fichier_desktop(self, fichier):
        '''Lit le fichier .desktop et récupère les informations nécessaires'''

        # 0=nom, 1, icone, 2=commande, 3=Est ce un jeu ? (type MIME Game), 4=Répertoire (Path)
        liste_infos = ["", "", "", 0, ""]
        fichier = open(fichier, 'r')

        txt_raccourcis = fichier.readlines()

        # Parcours de la liste du fichier:
        for index in range(len(txt_raccourcis)):
            # Si il y a l'information que l'on cherche dans le ligne en cours de lecture...

            # Pour la recherche du nom du jeu, Ne prend pas en compte les lignes qui contiennent 'Generic', ainsi que celles qui contiennent [
            # Ce sont des fichiers .desktop générés par KDE ou autre, qui contiennent
            # trop d'informations pour djl.
            if 'Generic' in txt_raccourcis[index] or '[' in txt_raccourcis[index]:
                pass
            else:
                if 'Name' in txt_raccourcis[index]:
                    # Partie nom du jeu:
                    nom = txt_raccourcis[index]
                    nom = nom.replace("Name" + '=', '')
                    nom = nom.replace('\n', '')
                    liste_infos[0] = nom

            if 'Icon' in txt_raccourcis[index]:
                info = txt_raccourcis[index]
                info = info.replace("Icon" + '=', '')
                info = info.replace('\n', '')

                if info == "":
                    info = dossier_racine + '/icone.png'
                else:
                    info = trouve_ico(info)

                liste_infos[1] = info

            # Partie commande
            if "Exec" in txt_raccourcis[index]:
                    # Si il y a des [] dans la ligne contenant la commande (typique à KDE), on
                    # les vires.
                if ']' in txt_raccourcis[index]:
                    info = txt_raccourcis[index].split('=')[-1]

                if 'TryExec' in txt_raccourcis[index]:
                    txt_raccourcis[index] = txt_raccourcis[index].replace('TryExec', 'Exec')

                liste_infos[2] = txt_raccourcis[index]

            # Partie MIME (Si il y a 'game' dans le fichier)
            if 'Game' in txt_raccourcis[index] or 'game' in txt_raccourcis[index]:
                liste_infos[3] = 1

            # Partie répertoire de lancement du jeu:
            if 'Path' in txt_raccourcis[index]:
                if '$HOME' in txt_raccourcis[index]:
                    txt_raccourcis[index] = txt_raccourcis[index].replace('$HOME', home)
                liste_infos[4] = txt_raccourcis[index]

        # Si il n'y a aucune variable "Icon" dans le fichier .desktop, on utilise l'icone de djl:
        if liste_infos[1] == "":
            liste_infos[1] = dossier_racine + '/icone.png'

        # Fais le ménage pour être sûr de ne pas avoir des variables erronés.
        for i in range(len(liste_infos)):
            if i != 3:  # On ne cherche pas si il s'agit du type MIME (c'est un entier)
                if ']=' in liste_infos[i]:  # Si il reste un nom de variable, on l'enlève
                    liste_infos[i] = liste_infos[i].split(']=')
                    liste_infos[i] = liste_infos[i][len(liste_infos[i]) - 1]

                if '=' in liste_infos[i]:
                    liste_infos[i] = liste_infos[i].split('=')
                    liste_infos[i] = liste_infos[i][len(liste_infos[i]) - 1]

                if '\n' in liste_infos[i]:
                    liste_infos[i] = liste_infos[i].replace("\n", "")

        # On a parcouru tout le fichier, on peut fermer la fonction
        fichier.close()
        # print liste_infos
        return liste_infos


def trouve_ico(nom):
    '''Tente de trouver l'icone pour un raccourci .desktop, grace au contenu de la variable "icon"'''
    retour = dossier_racine + '/icone.png'  # Sera modifié si on trouve une icone.
    nom = str(nom)
    if os.path.exists(nom):
        retour = nom

    elif os.path.exists('/usr/share/pixmaps/' + nom):
        retour = '/usr/share/pixmaps/' + nom
    elif os.path.exists('/usr/share/icons/' + nom):
        retour = '/usr/share/icons/' + nom
    elif os.path.exists(home + '/.local/share/icons/' + nom):
        retour = home + '/.local/share/icons/' + nom

    else:
        # Nouvelle méthode:
        sous_repertoires = [
            "/pixmaps/",
            "/icons/",
            "/icons/hicolor/48x48/apps/",
            "/icons/oxygen/48x48/apps/",
            "/icons/nuvola/48x48/apps/",
            "icons/crystalsvg/48x48/apps"]
        liste_repertoires = os.getenv("XDG_DATA_DIRS")
        if liste_repertoires is None:
            liste_repertoires = "/usr/share:/usr/local/share:/opt/kde/share"

        liste_repertoires = liste_repertoires.split(":")
        liste_repertoires.append(home + '/.local/share')
        for id in range(len(liste_repertoires)):
            for i in range(len(sous_repertoires)):
                ret = liste_repertoires[id] + sous_repertoires[i] + nom
                if os.path.exists(ret + ".png"):
                    return ret + ".png"
                elif os.path.exists(ret + ".xpm"):
                    return ret + ".xpm"
    return retour
