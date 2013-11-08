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

'''Agrégateur RSS'''

from PyQt4 import QtGui, QtCore
import sys
sys.path.append("libs")

import feedparser
import threading
import time
from variables import variables, dossier_racine
from config import config
import i18n


class var:
    pass


class UiRSS(object):

    '''Tout ce qui concerne l'interface des flux RSS uniquement (Hérité sur le client djl)'''

    def SetupUi_RSS(self):
        '''Dessin et connexion des Objets de l'onglet des flux RSS'''
        QtCore.QMetaObject.connectSlotsByName(self)
        self.gridlayout_4 = QtGui.QVBoxLayout(self.tab_4)
        self.gridlayout_4.setObjectName("gridlayout_4")

        self.liste_w_rss = QtGui.QListWidget(self.tab_4)
        self.liste_w_rss.setObjectName("liste_w_rss")

#        self.obj_RSS = QtGui.QWidget()
#        self.obj_RSS.timerEvent = self.timerEventRss

        self.liste_w_rss.contextMenuEvent = self.MenuContextRss

        self.gridlayout_4.addWidget(self.liste_w_rss)

        # Definition du menu contextuel
        self.menuRss = QtGui.QMenu(self)
        self.menuRss.setFont(self.font)

        self.act_rafraichi_rss = QtGui.QAction((i18n.traduc("Rafraichir")), self)
        self.act_rafraichi_rss.connect(
            self.act_rafraichi_rss,
            QtCore.SIGNAL("triggered()"),
            self.maj_RSS)
        self.menuRss.addAction(self.act_rafraichi_rss)
        icone = QtGui.QIcon(dossier_racine + '/res/redemarre_oxygen.png')
        self.act_rafraichi_rss.setIcon(icone)
        # /

        # Quand on double clique sur un des fil du flux RSS:
        self.liste_w_rss.connect(
            self.liste_w_rss,
            QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
            self.navigateur_RSS)

    def maj_RSS(self):
        '''Récupère et affiche la liste des flux RSS'''
        self.liste_w_rss.clear()
        self.liste_w_rss.addItem(i18n.traduc("En cours de telechargement...") + "\n")
        self.liens_RSS = []
        # Lance le timer, il vérifiera quand le téléchargement des flux RSS sera terminé
        var.rss_ok = False

#        self.timer_rss = QtCore.QBasicTimer()
#        self.timer_rss.start(0, self.obj_RSS)

        self.timer_rss = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer_rss, QtCore.SIGNAL("timeout()"), self.timerEventRss)
        self.timer_rss.start(200)

        self.parse_rss = parse_rss()
        self.parse_rss.start()

    def MenuContextRss(self, event):
        '''Affiche le menu contextuel (Onglet RSS uniquement)'''
        self.menuRss.exec_(event.globalPos())

    def timerEventRss(self):
        '''Un chrono qui vérifi régulièrement si le télécharger des flux RSS est terminé, si c'est le cas on les affichent, sinon la boucle continue'''
        if var.rss_ok:
            # Supprime le message 'connection en cours...'
            self.liste_w_rss.takeItem(0)
            nb = self.parse_rss.nb_flux()  # Récupère le nom de flux RSS disponibles
            for i in range(nb):
                self.affiche_RSS(i)  # Envoi l'affichage ques flux
            var.rss_ok = False
            self.timer_rss.stop()

#    def timerRss(self):
#        '''Un chrono qui vérifi régulièrement si le télécharger des flux RSS est terminé, si c'est le cas on les affichent, sinon la boucle continue'''
# Supprime le message 'connection en cours...'
#        self.liste_w_rss.takeItem(0)
# nb = self.parse_rss.nb_flux() #Récupère le nom de flux RSS disponibles
#        for i in range(nb):
# self.affiche_RSS(i) #Envoi l'affichage ques flux
#        variables.rss_ok = False

    def affiche_RSS(self, no=1):
        '''Ajoute les entrées des flux RSS dans la liste de l'onglet "Actualités"'''
        nb_entres = self.parse_rss.nb_entres(no)
        boucle = 0
        # Si il y a au moins une entrée dans le flux RSS:
        if nb_entres > 0:
            # self.liste_w_rss.addItem(self.parse_rss.titre_source(no)+':')
            # Affiche le titre du flux RSS:
            if len(self.liens_RSS) > 1:
                self.liste_w_rss.addItem('')
            self.liste_w_rss.addItem(self.parse_rss.titre_source(no) + ':')
            self.liens_RSS.append('nul')
            self.liens_RSS.append('nul')

            img_b = QtGui.QPixmap(dossier_racine + '/res/b_oxygen.png')

            # Boucle qui ajoute à la liste toutes les entrés du flux RSS:
            # Ici la limite est de 10 éléments.
            while boucle < nb_entres and boucle < 10:
                item = QtGui.QListWidgetItem(self.liste_w_rss)
                item.setIcon(QtGui.QIcon(img_b))
                self.liste_w_rss.setIconSize(QtCore.QSize(8, 8))
                item.setText(self.parse_rss.parse_rss(no, boucle)[0])

                self.liste_w_rss.addItem(item)
                # print self.parse_rss.parse_rss(no, boucle)[1]
                self.liens_RSS.append(self.parse_rss.parse_rss(no, boucle)[1])
                boucle = boucle + 1

    def navigateur_RSS(self):
        '''Quand on double clique sur un lien RSS, on lance le navigateur avec le lien'''
        try:
            lien = self.liens_RSS[self.liste_w_rss.currentRow() + 1]
            # print lien
            if lien != 'nul' and lien is not None:
                self.lance_navigateur(lien, type=1)
        except:
            pass


class parse_rss(threading.Thread):

    def __init__(self):
        '''Télécharge les données sur les différents flux RSS'''
        threading.Thread.__init__(self)

    def run(self):
        '''On démarre le Thread, télécharge les donnés pour la langue voulue'''
        langue = config(info=9)
        if langue == 'fr_FR':  # Liste des flux RSS en Français
            self.flux = [
                "http://djl.jeuxlinux.fr/djl_rss_fr.php",
                "http://www.jeuxlinux.fr/backend-breves.php3",
                "http://jeuxlibres.net/rss/games",
                "http://www.playonlinux.com/fr/rss.xml"]
        elif langue == 'ru_RU':  # Russes
            self.flux = [
                "http://djl.jeuxlinux.fr/djl_rss_ru.php",
                "http://www.linux.org.ru/section-rss.jsp?section=1&group=19104",
                "http://linuxgames.com/feed",
                "http://happypenguin.org/html/news.rdf"]
        elif langue == 'it_IT':  # Italiens
            self.flux = [
                "http://djl.jeuxlinux.fr/djl_rss_en.php",
                "http://www.playlinux.net/rss.xml",
                "http://linuxgames.com/feed",
                "http://happypenguin.org/html/news.rdf"]
        elif langue == 'es_ES':  # Espagnols
            self.flux = [
                "http://djl.jeuxlinux.fr/djl_rss_en.php",
                "http://feedproxy.google.com/linuxjuegos",
                "http://linuxgames.com/feed",
                "http://happypenguin.org/html/news.rdf"]
        else:  # Sinon on prend Anglais
            self.flux = [
                "http://djl.jeuxlinux.fr/djl_rss_en.php",
                "http://linuxgames.com/feed",
                "http://happypenguin.org/html/news.rdf",
                "http://www.linux-gamers.net/backend.php"]

        self.txt_flux = []
        # Récupère le texte sur chaque flux RSS (pour une langue):
        for i in range(len(self.flux)):
            try:
                t = feedparser.parse(self.flux[i])
                t['feed']['title']  # Un simple apperl pour vérifier que l'on ait le texte
                self.txt_flux.append(t)
            except KeyError:
                self.txt_flux.append('')
                print "Rss feed error:", self.flux[i]
        var.rss_ok = True  # djl arrichera les flux dès que cette valeur passe à True
        # variables.rss_ok = True #djl arrichera les flux dès que cette valeur passe à True

    def nb_flux(self):
        '''Renvoi le nombre de flux RSS disponible pour la langue actuellement utilisé'''
        return (len(self.flux))

    def titre_source(self, no=1):
        '''Parse le flux RSS donné en argument pour trouver le titre'''
        if self.txt_flux[no] != '':
            return self.txt_flux[no].feed.title

    def nb_entres(self, no=1):
        '''Parse le flux RSS donné en argument pour trouver le nombre d'entrés (pour un flux)'''
        if self.txt_flux[no] != '':
            return len(self.txt_flux[no]['entries'])

    def date_entre_rss(self, no, iteration):
        '''Récupère la date de l'entrée de l'article'''
        if self.txt_flux[no] != '':
            try:
                date = self.txt_flux[no].entries[iteration].updated_parsed
                return "- " + str(date[2]) + '/' + str(date[1]) + '/' + str(date[0]) + ': '
            except(KeyError, AttributeError):  # Si il n'y a pas de date...
                return "- "

    def parse_rss(self, no, iteration):
        '''Récupère le titre de l'entrée sur le flux RSS'''
        if self.txt_flux[no] != '':
            return (
                (self.date_entre_rss(no, iteration) +
                 self.txt_flux[no]['entries'][iteration]['title'], self.lien_rss(no, iteration))
            )

    def lien_rss(self, no, iteration):
        '''Récupère le lien qui pointe vers l'article du flux RSS'''
        if no != 0:  # Le premier flux RSS est celui de djl, il n'y a pas de lien:
            return self.txt_flux[no]['entries'][iteration]['link']
