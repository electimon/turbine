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

'''Interfacage avec le fichier de configuration'''

import os,  locale
home = os.path.expanduser('~')

def config(info = 0,  sec=0):
    '''Le le fichier de configuration et renvoi les informations demandés'''
    fichier_cfg = home + '/.djl/config'
    if os.path.exists(fichier_cfg) :
        #Ouvre le fichier en lecture seule:
        fichier = open(fichier_cfg, 'r')
        texte = fichier.readlines()

    #Si l'on veut savoir si il faut ou non lancer le jeu après installation
    if info == 0:
        r_info = texte[0]
        r_info = r_info.replace('telecharger_lancer = ', '')
        r_info = r_info.replace('\n', '')
        return r_info

    #Si l'on veut savoir si il faut ou non supprimer l'archive après installation
    elif info == 1:
        r_info = texte[1]
        r_info = r_info.replace('telecharger_supprimer = ', '')
        r_info = r_info.replace('\n', '')
        return r_info

    #Si l'on veut savoir où seront installés les jeux:
    elif info == 2:
        r_info = texte[2]
        r_info = r_info.replace('rep_jeux = ', '')
        r_info = r_info.replace('\n', '')
        return r_info

    #Si il faut afficher ou non l'icone dans la barre des taches:
    elif info == 3:
        r_info = texte[3]
        r_info = r_info.replace('afficher_miniature = ', '')
        r_info = r_info.replace('\n', '')
        return r_info

    #Si il faut vérifier au démarrage si djl est à jour:
    elif info == 4:
        #En cas d'exception (donnée manquante), la valeur est remplacée par une autre, par défaut
        try:
            r_info = texte[4]
            r_info = r_info.replace('maj_demarrage = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = '1'
        return r_info

    #Si on demande l'onglet par defaut:
    elif info == 5:
        try:
            r_info = texte[5]
            if 'onglet' in r_info:                
                r_info = r_info.replace('onglet = ', '')
                r_info = r_info.replace('\n', '')
            else:
                r_info = '0'
        except:
            r_info = '0'
        return r_info

    #Si l'on demande quel navigateur utiliser:
    elif info == 6:
        #En cas d'exception (donnée manquante), la valeur est remplacée par une autre, par défaut
        try:
            r_info = texte[6]
            r_info = r_info.replace('navigateur = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = 'firefox'
        return r_info
        
        
    #Si l'on demande d'afficher ou non les informations de débogage des jeux:
    elif info == 7:
        #En cas d'exception (donnée manquante), la valeur est remplacée par une autre, par défaut
        try:
            r_info = texte[7]
            r_info = r_info.replace('debug = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = '0'
        return r_info
        
    #Si l'on demande ou non de lancer les jeux dans un second serveur graphique:
    elif info == 8:
        #En cas d'exception (donnée manquante), la valeur est remplacée par une autre, par défaut
        try:
            r_info = texte[8]
            r_info = r_info.replace('composition = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = '0'
        return r_info
        
    #Si l'on demande quel langue utiliser
    elif info == 9:
        #En cas d'exception (donnée manquante), la valeur est remplacée par une autre, par défaut
        try:
            r_info = texte[9]
            r_info = r_info.replace('langue = ', '')
            r_info = r_info.replace('\n', '')
        except:
            #Sinon on renvoi la localisation du système:
            r_info = locale.getdefaultlocale()[0]
        
        if sec == 1:
            if r_info == 'fr_FR':
                return 1
            elif r_info == 'ru_RU':
                return 2
            elif r_info == 'en_US':
                return 3
            elif r_info == 'sv_SE':
                return 4
            elif r_info == 'pt_PT':
                return 5
            else:
                return 3
        else:
            return r_info

    #Si on demande le type d'interface à utiliser (0=interface mininale, 1=interface étendue avec les onglets):
    elif info == 10:
        #En cas d'exception (donnée manquante), la valeur est remplacée par une autre, par défaut
        try:
            r_info = texte[10]
            r_info = r_info.replace('type_gui = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = '1'
        return r_info
        
    #Si on demande le pseudo de l'utilisateur
    elif info == 11:
        try:
            r_info = texte[11]
            r_info = r_info.replace('pseudo = ', '')
            r_info = r_info.replace('\n', '')
            #r_info = r_info.replace("-djl","")
        except:
            r_info = str(os.environ["USER"]).capitalize() + '-djl'
        return r_info
        
    #Si on demande si il faut lancer ou non le client IRC au démarrage
    elif info == 12:
        try:
            r_info = texte[12]
            r_info = r_info.replace('conn_irc_demarrage = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = '1'
        return r_info
        
    #Si on demande la couleur de fond du client IRC:
    elif info == 13:
        try:
            r_info = texte[13]
            r_info = r_info.replace('fond_irc = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = '1'
        return r_info
        
    ##Si on demande le répertoire du dépot:
    elif info == 14:
        return '/cache'
        
    #Si on demande la taille des polices:
    elif info == 15:
        try:
            r_info = texte[14]
            r_info = r_info.replace('taille_police = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = "9"
        return int(r_info)
        
    #Si on demande la liste des canaux IRC:
    elif info == 16:
        try:
            r_info = texte[15]
            r_info = r_info.replace('canaux_IRC = ', '')
            r_info = r_info.replace('\n', '')
            r_info = r_info.replace("  ", " ")
            liste = r_info.split(" ")
        except:
            loc = locale.getdefaultlocale()[0].split("_")[0]
            liste = ["#djl", "#djl-"+str(loc)]
        return liste
    
    #Si on demande si il faut télécharger automatiquement les dépendances:
    elif info == 17:
        try:
            r_info = texte[16]
            r_info = r_info.replace('dependances = ', '')
            r_info = r_info.replace('\n', '')
        except:
            r_info = "0"
        return int(r_info)
    
    #Sinon...
    else:
        return 0

    fichier.close()
