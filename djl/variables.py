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

import os
import config

#Repère le répertoire racine dans l'arborescence:
dossier_racine = os.getcwd()
home = os.path.expanduser('~')

#Défini les variable publiques:
class variables:
    instance = None #Instance de la classe principale de djl.
    
    maj_listejeux = False #Si passe à True, met à jour la liste des jeux
    
    #Défini le jeu en cours d'execution
    nom_jeu = ""
    
    #Défini l'état lors de l'installation de jeux:
    installe = {}
    
    #Affiche un message d'erreur quand le jeu est lancé, si la variable vaut 1
    erreur=0
    
    #Permet ou non l'affichage de l'éditeur de fichiers texte (débogage, journal.txt, historique de djl...) (tout dépend si il est déjà ouvert), avec la classe Ui_journal:
    journal = 0
    
    #Défini si l'on utilise une version de développement:
    version_dev = 0
    
    #Défini le lien vers le site dans le menu de la liste de jeux doit être activé (si on a put se connecter ou non)
    lien_site = 1

    #etat_RSS = 0
    
    ###Variables dédiés à IRC:
    connecte = 0 #Défini l'état, si l'on est connecté ou pas
    recoi_irc = ["", "",  ""] #texte, canal, source (pseudo)
    
    #Créé les listes qui contiendront le texte de chaque canal
    liste_canaux = [""]*len(config.config(info=16)) #Va chercher la liste des canaux suivant la configuration)
    
    #Les listes d'utilisateurs pour chaque canal
    liste_utilisateurs = {}
    
    #Evenement sur IRC, on modifi la liste quand un utilisateur rejoins ou ferme le canal ou se deconnecte
    even_irc = ["",  "",  ""] #nom_evenement, canal, source (utilisateur)
    ####/IRC
    
    #Défini le type de MAJ (dans le dossier de djl ou dans ~/.djl/src)
    type_maj = 0
    
    #Passe à un quand il faut mettre à jour la police  d'écriture de djl
    ch_police = 0
    
    #Définition des serveurs utilisés (constantes)
    SERVEUR_SOAP = ''
    SERVEUR_LIBRAIRIES = ''
    SERVEUR_STABLE = ''
    SERVEUR_DEV = ''
