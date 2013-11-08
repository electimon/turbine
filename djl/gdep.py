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

'''Interface cliente/serveur pour la gestion des dépendances'''

import os
import urllib
import threading
import socket
from variables import variables  # , home
import interface
from config import config
import i18n

socket.setdefaulttimeout(10)


class VarsDep:
    init = False
    instance = 0
    liste = []


class thRecupLib(threading.Thread):

    '''Lance la le module de récupération des librairies sous forme de Thread (non utilisé)'''

    def __init__(self, nom_lib):
        self.nom_lib = nom_lib
        threading.Thread.__init__(self)

    def run(self):
        RecupLib(self.nom_lib)


class RecupLib():

    '''Si il manque une lib, ce module l'installera'''

    def __init__(self, nom_lib):
        self.nom_lib = nom_lib
        self.recup()

    def creer_liste(self):
        VarsDep.liste = VarsDep.instance.Rliste()

    def recup(self):
        if not VarsDep.init:  # Si c'est le premier lancement de la classe...
            VarsDep.init = True
            VarsDep.instance = GestionLibs()
            self.creer_liste()

        # Récupère la librairie:
        trouve = False
        for i in range(len(VarsDep.liste)):
            if VarsDep.liste[i] == self.nom_lib:
                trouve = True
                VarsDep.instance.Telecharge(self.nom_lib)
                break

        if trouve:
            #interface.info_box(i18n.traduc("Librairie manquante trouvé:") + ' ' + self.nom_lib)
            # Si la librairie manquante a été installée, on tente de relancer le jeu:
            variables.instance.lance()
        else:
            interface.info_box(
                i18n.traduc(
                    "La librairie n'a pas ete trouvee") +
                ': ' +
                self.nom_lib +
                '\n' +
                i18n.traduc(
                    "Merci de rapporter le probleme au developpeur."))


class GestionLibs(object):

    '''Interface avec le serveur pour gérer la liste des librairies'''

    def __init__(self):
        '''Initialisation'''
        self.repertoire = config(info=2) + "/libs"  # Répertoire d'installation des librairies
        self.f_liste = self.repertoire + "/liste"  # Fichier contenant la liste des librairies
        # Serveur pour télécharger les librairies
        self.serveur = variables.SERVEUR_LIBRAIRIES + "/maj_djl/libs"

    def Repertoire(self):
        '''Renvoi le répertoire contenant les librairies'''
        return self.repertoire

    def Rliste(self):
        '''Renvoi la liste des librairies'''
        # On s'assure que le dossier pour contenir les librairies existe:
        if not os.path.exists(self.repertoire):
            os.mkdir(self.repertoire)

        # Télécharge la liste
        try:
            urllib.urlretrieve(self.serveur + "/liste.php", self.f_liste, reporthook=False)
        except IOError:
            return []  # Si on a pas pu acceder à la liste sur le réseau, on renvoi une liste vide.

        # Après avoir téléchargé la liste, on la lit:
        fichier = open(self.f_liste, 'r')
        liste = fichier.readlines()
        fichier.close()

        # Parcours la liste pour virer les sauts à la ligne
        for i in range(len(liste)):
            liste[i] = liste[i].replace('\n', '')

        return liste

    def Telecharge(self, nom_lib):
        '''Télécharge la librairie donné en argument'''
        urllib.urlretrieve(self.Lien(nom_lib), self.repertoire + "/" + nom_lib, reporthook=False)

    def Lien(self, nom_lib):
        '''Renvoi le lien de téléchargement pour la librairie donné en argument'''
        return self.serveur + '/' + nom_lib
