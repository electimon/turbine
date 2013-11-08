#!/usr/bin/python2
# -*- coding: utf-8 -*-

# djl (Dépot jeux Linux)
# Copyright (C) 2008-2009 - 2009 Florian Joncour - Diablo150 <diablo151@wanadoo.fr
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


'''Script principal de djl'''

try:  # Tente l'optimisation avec psyco
    import psyco
    # print "Psyco trouvé, optimisation..."
    psyco.full()
    # psyco.log()
    # psyco.profile()
except ImportError:
    pass

from PyQt4 import QtGui, QtCore
import sys
import urllib
sys.path.append("libs")
import irc
import SOAPpy

import threading
import os
import urllib
import atexit
import socket
import re

from installe import lance, msg_erreur, modif_etat, erreur_x11, installe
from variables import variables, home, dossier_racine

from config import config  # Lis le fichier de configuration
import diff  # Fonctions diverses utilisés par l'interface principale
import interface  # Dessin de l'interface principale
import i18n  # Récupère le texte sur le fichiers de traduction
import rss  # Agrégateur RSS
import depot  # Interface du dépot
import modules  # Gestionnaire de modules

# Envoi l'installation de l'internationalisation:
# i18n.i18n_init()

# Modifi le user-agent:
urllib.URLopener.version = "djl" + interface.version() + "/Linux"

# Change le nom du processus.
import ctypes
libc = ctypes.CDLL('libc.so.6')
libc.prctl(15, 'djl', 0, 0, 0)

# Définition des serveurs de mise à jours pour djl:
# Version de développement:
variables.SERVEUR_DEV = ["http://djl-linux.org/dev", "http://djl.jeuxlinux.fr/dev"]
# Version_stable
variables.SERVEUR_STABLE = [
    "http://djl-linux.org",
    "http://djl.jeuxlinux.fr",
    "http://djl.tuxfamily.org"]

# Serveur pour le téléchargement des librairies:
variables.SERVEUR_LIBRAIRIES = "http://djl-linux.org"

# Serveur pour le dépôt:
variables.SERVEUR_SOAP = "http://ws.djl-linux.org"

#global version_dev
variables.version_dev = 0
# Défini si l'on utilise ou non la version de développement (premier argument)
if len(sys.argv) > 1:
    # if sys.argv[1] == "-dev":
    if "-dev" in sys.argv:
        variables.version_dev = 1
        #import gc
        # gc.set_debug(gc.DEBUG_LEAK)


class Ui_Djl(QtGui.QMainWindow, interface.Onglets_djl, diff.Main, irc.interface_IRC, rss.UiRSS, depot.UiDepot, depot.Foncs_Depot, modules.Interface):

    def filtre_liste(self):
        '''Créé la liste des jeux affichés dans le dépôt en fonction des filtres seléctionnés'''
        filtre_genre = self.parse_listegenre(self.comboBox.currentIndex(), 0)

        filtre_licence = self.combo_license.currentIndex()

        self.liste_jeux_ok = []
        self.liste_index = []
        self.widget_liste_jeux.clear()

        for i in range(self.nb_jeux):
            type_jeu = self.parse_listejeux(i, 5)  # Recupère le type de jeu
            licence = self.parse_listejeux(i, 9)  # Recupère la licence du jeu

            # Filtre ici les jeux par genre
            if (int(type_jeu) == int(filtre_genre)) | (int(filtre_genre) == 0):
                # Filtre ici les jeux par licence
                if (int(licence) == int(filtre_licence)) | (int(filtre_licence) == 0):
                    nom_jeu = self.parse_listejeux(i, 0)

                    # Si on a la version de développement, on ajoute un * au nom du jeu si il
                    # n'est pas validé, afin de le reconnaitre:
                    if variables.version_dev == 1:
                        if self.parse_listejeux(i, 8) == "0":
                            nom_jeu = "* " + nom_jeu

                    self.widget_liste_jeux.addItem(nom_jeu)
                    nom_rep = self.parse_listejeux(i, 2)
                    self.liste_jeux_ok.append(nom_rep)
                    self.liste_index.append(self.parse_listejeux(i, 6))

        # print '>>>' + str(len(self.liste_jeux_ok))

        self.label.setText(i18n.traduc("Liste des jeux disponible: (")
                           + str(len(self.liste_jeux_ok)) + '/' + str(self.nb_jeux) + ')')

    def maj_description(self):
        '''Dès que l'on change de jeu dans la liste, affiche la description dans la zone correspondante: (Depot)'''
        # Si la liste des jeux n'est pas encore prete, on sort de la fonction
        if len(self.liste_jeux_ok) == 0:
            return

        nom_jeu = self.nom_jeu_depot()
        # print nom_jeu
        no_description = self.trouve_index(nom_jeu)

        # print variables.installe

        version = self.parse_listejeux(no_description, 1).split('-r')[0]

        nom = self.parse_listejeux(no_description, 0)

        # Affiche le nom du jeu dans la description:
        self.label_4_2.setText(nom)

        # Affiche la version du jeu dans la description:
        self.label_4_v.setText(i18n.traduc("Version:") + " " + version)

        # Trouve le type de jeu depuis le webservice:
        gr = self.detail_jeux(no_description, type_info='genre')  # id (entier) du genre
        for i in range(len(self.liste_genre)):
            if gr == self.parse_listegenre(i, 0):
                gr = i
                break

        # Si il trouve quelque chose:
        if gr != '':
            try:
                genre = self.parse_listegenre(int(gr), 1)
            except (TypeError, IndexError), x:
                print "Genre: ", str(x)
                genre = "?"

            # Affiche le type de jeu dans le 'label' prévu à cet effet:
            self.label_5.setText(i18n.traduc("Genre") + ": " + genre)
        else:
            self.label_5.setText(i18n.traduc("Genre: Non defini"))

        # Trouve la taille de l'archive depuis le webservice:
        tl = self.detail_jeux(no_description, type_info='taille')
        if tl == '':
            self.label_6.setText(i18n.traduc("Taille: Non definie"))
        else:
            self.label_6.setText(i18n.traduc("Taille: ~") + str(tl) + ' Mo')

        # Trouve la licence dans depuis le webservice:
        licence = self.detail_jeux(no_description, type_info='licence')
        if licence != '':
            licence = licence.capitalize()
            self.label_9.setText(i18n.traduc("Licence") + ": " + licence)
        else:
            self.label_9.setText(i18n.traduc("Licence: Non definie"))

        # Troule l'article associé au jeu (généralement sur jeuxlinux.fr) afin
        # d'avoir plus d'informations sur celui-ci:
        art = str(self.detail_jeux(no_description, type_info='article'))

        # Si il ne trouve pas d'article, on bloque le bouton
        if art == "" or art == "nul":
            self.b_article.setEnabled(False)
        else:
            # Sinon on le débloque et on créé la variable qui permettra de visiter le site
            self.b_article.setEnabled(True)
            self.lien_article = art

        site = str(self.detail_jeux(no_description, type_info='site'))
        if site == "" or site == "nul":
            self.b_site.setEnabled(False)
        else:
            self.b_site.setEnabled(True)
            self.lien_site = site
        # print 'article>' + str(art) +  '< - site>' + str(site) + '<'
        # Trouve la description
        txt_desc = self.detail_jeux(no_description, type_info='description')
        if txt_desc != 0 and txt_desc != "pas de description !":
            # self.texte_description.setText(txt_desc)
            txt_desc = txt_desc.replace("\n", "<br />")
            self.texte_description.setHtml(txt_desc)
        else:
            self.texte_description.setHtml(i18n.traduc("Pas de description disponible."))
        # On a vu pour le déscription, maintenant on va chercher l'icone:
        self.affiche_icone(no_description)
        # Lance l'affichage de l'image du jeu:
        self.affiche_image(no_description)

        # Si le jeu est en cours d'installation, on desactive les boutons
        # d'installation/suppression.
        if nom_jeu in variables.installe:
            if variables.installe[nom_jeu] == False:
                self.boutton_supprimer.setEnabled(False)
                self.boutton_installer.setEnabled(False)
                self.boutton_maj.setEnabled(False)
                return

        # Sinon, va chercher l'etat, afin de savoir si le jeu est installé ou non:
        self.etat(nom_jeu)

    def entete_fichier(self, fichier):
        '''Va chercher l'entête du fichier donné et s'assure que c'est bien une image ou un fichier texte et non pas une page html 404.'''
        try:
            fichier_o = open(fichier, 'r')
        except:
            return 1

        entete = fichier_o.readline(-1).replace("\n", "")
        if "html" in entete or "HTML" in entete:
            return 1
        else:
            return 0

    def liste_jeux_installe(self):
        '''On créé ici la liste des jeux installés et archivés pour les afficher dans la fenêtre principale'''
        self.liste_jeux_f = []
        # print ">>>Maj liste jeux installe"
        # Liste les dossier du répertoire 'jeux' pour lister les jeux installés depuis le dépot:
        liste_depot = os.listdir(config(info=2) + '/jeux')
        liste_depot.sort()

        id = 0  # id du jeu ajouté, sert pour le menu dans la boite à miniatures

        for i in range(len(liste_depot)):
            index = self.trouve_index(dossier=liste_depot[i])
            # print "Index:",  str(index)
            if index != 'nul':
                item = QtGui.QListWidgetItem(self.listWidget)

                nom_jeu = self.parse_listejeux(index, 0)
                icone = self.parse_listejeux(index, 3)
                adresse_icone = (config(info=2) + '/' + config(info=14) + '/icos/' + icone)

                if not os.path.exists(adresse_icone):
                    # print "L'icone n'existe pas:",  icone
                    urllib.urlretrieve(
                        'http://djl.jeuxlinux.fr/images/logo/' +
                        icone,
                        adresse_icone,
                        reporthook=False)

                item.setIcon(QtGui.QIcon(adresse_icone))
                item.setText(nom_jeu)

                # Si on a l'icone dans la boite à miniature, on y ajoute également la liste:
                if int(config(info=3)) == 1 and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
                    act = QtGui.QAction(self)
                    act.setIcon(QtGui.QIcon(adresse_icone))
                    act.setText((nom_jeu))
                    self.menu_lance.addAction(act)

                    self.connect(
                        act,
                        QtCore.SIGNAL("triggered()"),
                        self.Mapper,
                        QtCore.SLOT("map()"))
                    self.Mapper.setMapping(act, id)
                    id = id + 1

                self.liste_jeux_f.append(liste_depot[i])
            if int(config(info=3)) == 1 and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
                self.nb_menu_mini = id

    def trouve_commande(self, dossier=''):
        '''Trouve le nom de la commande associée au jeu dans la liste'''
        index = self.trouve_index(dossier)
        cmd = self.parse_listejeux(index, 4)
        # print '>',  cmd
        return cmd

    def cree_reps(self):
        '''Créé l'arborescence du dépot dans le répertoire de cache'''
        # Créé le répertoire racine:
        if not os.path.exists(config(info=2)):
            os.mkdir(config(info=2))

        # Créé le répertoire d'installation des jeux:
        if not os.path.exists(config(info=2) + '/jeux'):
            os.mkdir(config(info=2) + '/jeux')

        # Créé le répertoire qui contiendra les raccourcis
        if not os.path.exists(config(info=2) + '/raccourcis'):
            os.mkdir(config(info=2) + '/raccourcis')

        # Créé le répertoire d'etat des jeux
        if not os.path.exists(config(info=2) + '/etat_jeux'):
            os.mkdir(config(info=2) + '/etat_jeux')

        # Créé le répertoire du cache
        if not os.path.exists(config(info=2) + '/' + config(info=14)):
            # print '>',config(info=2) + '/' + config(info=14)
            # Créé les sous-répertoire des jeux
            os.mkdir(config(info=2) + '/' + config(info=14))

        if not os.path.exists(config(info=2) + '/' + config(info=14) + '/imgs'):
            os.mkdir(config(info=2) + '/' + config(info=14) + '/imgs')

        if not os.path.exists(config(info=2) + '/' + config(info=14) + '/icos'):
            os.mkdir(config(info=2) + '/' + config(info=14) + '/icos')

    def info(self):
        '''Récupère des informations dès que l'on selectionne un jeu dans la liste de jeux principale.'''
        jeu_actuel = self.liste_jeux_f[self.listWidget.currentRow()]
        variables.args_dir_jeu = jeu_actuel

        # self.action_args.setEnabled(True)

        index = self.trouve_index(jeu_actuel)

        if index == 'nul':
            nom_j = jeu_actuel
            if '.desktop' in nom_j:
                nom_j = nom_j.replace('.desktop', '')
                nom_j = nom_j.capitalize()
        else:
            nom_j = self.parse_listejeux(index, 0)

        #self.action_args.setText(i18n.traduc("Arguments de lancement pour") + " " + nom_j)

        # Si c'est un fichier .desktop...
        if 'desktop' in str(jeu_actuel):
            # self.actionSupprimer_desk.setEnabled(True)
            pass
        else:
            # Sinon, on le rend inactif:
            # self.actionSupprimer_desk.setEnabled(False)

            # On va chercher le lien vers le site officiel du jeu(uniquement si on est
            # déjà connecté au webservice
            if self.connecte_ws == 1:
                try:
                    self.lien_site = self.detail_jeux(
                        self.trouve_index(jeu_actuel),
                        type_info='site')
                    variables.lien_site = 1
                except socket.gaierror:
                    # Si il ne peut pas se connecter au serveur, tant pis pour le lien
                    self.lien_site = "nul"
                    variables.lien_site = 0
            else:
                variables.lien_site = 0

    def trouve_index(self, dossier='', id=0):
        '''Trouve l'index dans la listes d'informations d'un jeu donné pour pouvoir récupérer les infos que l'on veut'''
        for i in range(self.nb_jeux):
            val = self.parse_listejeux(i, 2)

            if str(dossier) == str(val):
                # print self.parse_listejeux(i, 6), i
                if id == 0:
                    return i
                elif id == 1:
                    return int(self.parse_listejeux(i, 6))
        return (
            # Si il a fini la boucle et qu'on a rien trouvé, le jeu sera ignoré faute
            # d'informations.
            'nul'
        )

#    def trouve_nom_jeu(self, nom_jeu):
#        '''Trouve le 'vrai' nom du jeu en fonction du nom de son répertoire ou raccourcis'''
# if '.desktop' in nom_jeu: #Si c'est un raccourcis:
#            return self.lit_fichier_desktop(nom_jeu, type_info = 'Name')
# else: #Si c'est un jeu installé avec djl:
# nom = self.djl.detail_jeux(self.djl.trouve_index(nom_jeu), type_info = 'commande')
#            return self.parse_listejeux(i, [self.trouve_index(nom_jeu)], 0)

    def verif_dependances(self):
        '''Vérifi les dépendances pour le jeu actuellement seléctionné dans la liste de jeux principale
        (uniquement les jeux de djl, pas les raccourcis).'''
        jeu_actuel = self.nom_jeu_pr()
        commande = 'nul'
        cmd = self.trouve_commande(dossier=jeu_actuel)
        rep = config(info=2) + '/jeux/' + jeu_actuel

        if os.path.exists('/usr/bin/ldd32'):
            ldd = 'ldd32'
        else:
            ldd = 'ldd'

        liste = os.listdir(rep)
        if len(liste) <= 2:  # Si le répertoire ne contient que 2 éléments ou moins, c'est normal
            for i in range(len(liste)):
                if os.path.isdir(rep + '/' + liste[i]):
                    repertoire = rep + '/' + liste[i]
        else:  # Si il y a plusieurs répertoires dans le répertoire du jeu, on binaire doit être là
            repertoire = rep

        # Créé la variable d'environnement qui va bien avant de vérifier les librairies:
        if os.path.exists(repertoire + '/lib'):
            LIBRARY_PATH = repertoire + ':' + repertoire + \
                '/lib:' + config(info=2) + "/libs" + ':/usr/lib'
        elif os.path.exists(repertoire + '/libs'):
            LIBRARY_PATH = repertoire + ':' + repertoire + \
                '/libs:' + config(info=2) + "/libs" + ':/usr/lib'
        else:
            LIBRARY_PATH = repertoire + ':' + config(info=2) + "/libs" + ':/usr/lib'

        os.putenv("LD_LIBRARY_PATH", LIBRARY_PATH)

        commande = repertoire + '/' + cmd
        dep_ok = ''
        dep_manque = ''
        chaine = ''
        trouve = False
        retour = os.popen(ldd + ' ' + commande).readlines()  # str() temp
        #retour = retour.replace('  ', '')

        if len(retour) > 2:
            for i in range(len(retour)):
                # Si il semble manquer la librairie, on l'ajoute dans la chaine des
                # dependances manquantes
                if "not found" in retour[i]:
                    trouve = True
                    dep_manque = dep_manque + retour[i]  # + "<br>"
                # Si il a trouve la librairie, on l'ajoute à la chaine des dépendances satisfaites
                else:
                    dep_ok = dep_ok + retour[i]

            if trouve:  # Si il y a au moins une librairie manquante
                chaine = _('Dependances non satisfaites') + ':' + "\n\n" + dep_manque
            else:  # Si toutes les dépendances semblent ok
                chaine = _('Toutes les dependances semblent satisfaites') + ':' + "\n\n" + dep_ok
        # Si la sortie ne fais pas au moins 2 lignes, on affiche directement le
        # message, c'est surement une erreur (binaire on trouvé)
        else:
            chaine = i18n.traduc("Erreur") + ":\n"
            for i in range(len(retour)):
                chaine = chaine + retour[i]

        interface.info_box(chaine, _('Verifier les dependances'))
        # print commande
        # print os.path.exists(commande)
        # print retour

    def lance(self, Qitem='', Djeu='', Darguments=''):
        '''On lance un jeu ici (jeu séléctionné dans la liste de jeux principale ou défini par la variable Djeu), avec si besoin des arguments'''

       # if self.tabWidget.currentIndex() == 1: #liste principale
           # self.lance()
       # elif self.tabWidget.currentIndex() == 2: #depot
           # self.maj_description()
           # self.installer_jouer()

        if self.int_etendue:
            # Si on ne défini pas de jeu, on prend l'objet séléctionné dans la liste
            # de jeux principale
            if Djeu == '':
                if self.tabWidget.currentIndex() == 1:  # liste principale
                    jeu_actuel = self.nom_jeu_pr()
                elif self.tabWidget.currentIndex() == 2:  # depot
                    jeu_actuel = self.nom_jeu_depot()
                else:
                    jeu_actuel = self.nom_jeu_pr()
            else:
                for i in range(len(self.liste_jeux_f)):
                    if Djeu == self.liste_jeux_f[i]:
                        jeu_actuel = Djeu
                        break
        else:  # Si on utilise l'interface simple...
            jeu_actuel = self.nom_jeu_pr()

        # print '>', jeu_actuel, Darguments, Djeu

        diff.ecrit_historique(str(jeu_actuel) + i18n.traduc("lance"))

        # On lance la fonction qui va bien au module 'Dlog', si il existe
        try:
            self.trouve_module('Dlog', 1).lance(jeu_actuel)
        except:
            pass  # Mieux vaut ignorer les exception, sinon on ne peut plus lancer les jeux

        # Bloque l'interface graphique quelques secondes avant de lancer le jeu:
        # Si le jeu met un peu de temps à se lancer, l'utilisateur ne pourra pas
        # lancer (bêtement) plusieurs fois le jeu
        self.listWidget.setEnabled(False)
        self.bloque_ui = 1

        # Si c'est un fichier .desktop, on lance le jeu comme il faut:
        if '.desktop' in jeu_actuel:
            cmd = self.lit_fichier_desktop(fichier=jeu_actuel, type_info='Exec')
            # print '>Commande: ', str(cmd), '/', str(jeu_actuel), self.listWidget.currentRow()

            # Si le raccourcis utilise une variable path pour définir le réperoire du jeu
            dir_jeu = self.lit_fichier_desktop(fichier=jeu_actuel, type_info='Path')

            # Supprime les espaces dans la ligne de commande et les remplace par '\ '
            # if ' ' in cmd:
                # if '\ ' in cmd:
                    # pass
                # else:
                    #cmd=cmd.replace(' ', '\ ')

            # Ajoute les arguments de lancement défini par l'utilisateur (si il y en a)
            cmd = cmd + ' ' + Darguments + ' ' + str(self.trouve_args(jeu_actuel))

            th_lance = lance(jeu_actuel, cmd, dir_jeu, raccourci=1)
            th_lance.start()

        # Sinon, c'est un jeu installé depuis le dépot, on le lance donc différemment:
        else:
            # On récupère la commande du jeu:
            cmd = self.trouve_commande(dossier=jeu_actuel)

            # Ajoute les arguments (si il y en a)
            cmd = cmd + ' ' + str(self.trouve_args(jeu_actuel)) + ' ' + Darguments

            # On lance le jeu avec la class lance() dans installe.py:
            th_lance = lance(jeu_actuel, cmd)
            th_lance.start()

        print("- " + jeu_actuel + ">" + cmd)

        # Affiche la sortie dans une boite de dialogue (en fonction de la configuration):
        if int(config(info=7)) == 1:
            self.affiche_sortie_jeu()

        # Affiche la boite de dialogue "En cours de lancement" pendent 3 secondes:
        self.MessageLancement = diff.MessageLancement(3, self)
        self.MessageLancement.show()

    def archive_lien(self, lien):
        '''Essai de récupérer le nom d'une archive avec les méta informations. Si il ne trouve rien, renvoi "nul". '''
        try:
            l = urllib.urlopen(lien)
        except:
            return "nul"

        meta = l.info()  # Recupère les méta informations de l'archive

        # Si on recois une page html c'est que le lien de téléchargement est foireux.
        if meta.gettype() == "text/html":
            return "nul"
        else:
            try:
                info_m = meta["Content-Disposition"]
            except KeyError:
                return "nul"

            if "filename=" in info_m:
                info_m = info_m.split("filename=")
                archive = info_m[len(info_m) - 1]
            else:
                return "nul"

        archive = archive.replace('"', '')
        return archive

    def parse_lien(self, lien):
        '''Parse un lien de téléchargement pour récupérer le nom de l'archive que l'on essai de télécharger'''

        archive = ""

        # Essai de récupérer le nom de l'archive via lles meta informations:
        meta = self.archive_lien(lien)

        # Si on a le nom du paquet d'après les meta informations...
        if meta != "nul":
            return meta  # ...On renvoi le nom du paquet.

        else:  # Sinon on essai de trouver le nom du paquet "intelligement"
            # extensions acceptés, utilisé pour retrouver le nom du paquet dans sliste
            exts = ["tar", "zip", "tgz", "package", "run", "bin", "inj", "bz2"]

            # Essai de récupérer le nom de l'archive:
            archive = lien.split("/")
            archive = archive[len(archive) - 1]
            # Découpe en sous liste le nom du paquet pour virer les indésirables (?, #, etc...)
            sliste = re.split('[/=?#]', archive)

            #print ("sliste:", sliste)

            for i in range(len(sliste)):
                for n in range(len(exts)):
                    if ("." + exts[n]) in sliste[i]:
                        return sliste[i]
        return archive

    def installer_jouer(self):
        '''Quand on clique sur le bouton installer/jouer...'''
        # Trouve le nom du jeu actuellement sélectionné (depot)
        nom_jeu = self.nom_jeu_depot()

        no_description = self.trouve_index(nom_jeu)
        # print '>>>',  no_description

        # Trouve l'adresse de téléchargement
        adresse_telecharge = self.detail_jeux(no_description, type_info='telecharge')

        # Répère le nom de l'archive du jeu:
        #nom_archive = adresse_telecharge.split('/')[-1]
        nom_archive = self.parse_lien(adresse_telecharge)

        print "Nom_archive:", nom_archive

        # On fini le nettoyage pour récupérer le nom de l'archive (exemple:
        # file=wings2_v1.3.6_linux.tar.gz)
        if "=" in nom_archive:
            nom_archive = nom_archive.split("=")
            nom_archive = nom_archive[len(nom_archive) - 1]

        # Si le nom de l'archive est de type "fichier.tar.gz?cmd", on enleve une
        # partie pour s'arreter à l'extension du fichier
        if "?" in nom_archive:
            nom_archive = nom_archive.split("?")
            nom_archive = nom_archive[0]

        # Si l'archive existe déjà, on ne la re-télécharge pas
        #print (config(info=2) + '/jeux/') + variables.nom_archive
        if self.etat_actuel == 0 and os.path.exists((config(info=2) + '/jeux/') + nom_archive) == True:
            # Si l'archive est plus petite que 500 Ko, on re-télécharge:
            if int(os.stat((config(info=2) + '/jeux/') + nom_archive).st_size) / 1024 > 500:
                print "L'archive du jeu existe déjà, elle ne sera pas téléchargé"
                self.etat_actuel = 2

        # print self.etat_actuel
        commande = self.trouve_commande(dossier=nom_jeu)

        # Si le jeu n'est pas encore installé, on lance le téléchargement, il sera
        # installé ensuite:
        if self.etat_actuel == 0:
            if adresse_telecharge != 0:

                self.boutton_supprimer.setEnabled(False)
                self.boutton_installer.setEnabled(False)
                self.boutton_maj.setEnabled(False)

                # Répère la version afin de garder en mémoire la version du jeu installé,
                # afin de permettre plus tard la mise à jour:
                version = self.detail_jeux(no_description, type_info='version')

                # Récupère le nom de l'icone, il sera affiche dans l'onglet de téléchargement:
                icone = config(info=2) + '/' + config(info=14) + '/icos/' + \
                    self.detail_jeux(no_description, type_info='icone')

                # Récupère le titre du jeu qui sera affiché dans la QlistWidget
                titre = self.parse_listejeux(no_description, 0)

                # Envoi la fenêtre de téléchargement:
                #self.telecharge_ui(adresse_telecharge, nom_archive, nom_jeu, commande, version)
                self.NouvTelechargement(
                    adresse_telecharge,
                    nom_archive,
                    nom_jeu,
                    commande,
                    version,
                    icone,
                    titre)
            else:
                print i18n.traduc_ascii("Impossible de trouver l'adresse de telechargement")

        # Si le jeu est déjà installé, on le lance:
        if self.etat_actuel == 1:
            #th_lance = lance(nom_jeu, commande)
            # th_lance.start()
            #self.lance('', nom_jeu)
            self.lance()

            # Affiche la boite de dialogue "En cours de lancement" pendent 3 secondes:
            self.MessageLancement = diff.MessageLancement(3, self)
            self.MessageLancement.show()

        # Si le jeu est déjà téléchargé, on l'installe
        if self.etat_actuel == 2:
            # Répère la version afin de garder en mémoire la version du jeu installé,
            # afin de permettre plus tard la mise à jour:
            nom_version = self.detail_jeux(no_description, type_info='nom')
            version = nom_version.split(' ')
            version = version[len(version) - 1]

            # Lance l'installation:
            # nom_archive: le nom réel de l'archive, nom_jeu: répertoire où sera extrait le jeu.
            th_i = installe(nom_archive, nom_jeu, commande, version)
            th_i.start()

    # def keyPressEvent(self, event):
        #'''Quand une touche clavier est pressé...'''
        # print event.key()

    def timerEvent(self, event):
        '''Timer, boucle principale'''
        if self.t_maj:  # Si une mise à jour est disponible
            self.t_maj = 0
            self.trouve_serveur_maj(notif=1, serveur=0)

# Quand les flux RSS sont prêts, on les affichent:
#        if self.int_etendue:
# Quand la liste des modules est récupérée sur le serveur...
#            if self.vliste:
# self.AffListeMod() #On affiche la liste
# self.VerifMajMod() #Vérifi si les modules sont à jours (maintenant qu'on a la liste)
#                self.vliste = False

        # Si la variables contenant la taille des polices change, on met à jour l'interface
        # Avec cette taille de police
        if variables.ch_police != 0:
            self.font.setPointSize(variables.ch_police)
            self.setFont(self.font)
            self.menubar.setFont(self.font)
            self.menuMenu.setFont(self.font)
            self.menuLang.setFont(self.font)
            self.menuAide.setFont(self.font)
            self.menuDepot.setFont(self.font)

            self.font2.setPointSize(variables.ch_police + 2)
            self.font3.setPointSize(variables.ch_police + 6)
            if self.int_etendue == 1:
                self.listWidgetTelechargement.setFont(self.font2)
                self.listWidget.setFont(self.font2)

            variables.ch_police = 0

        # Partie IRC
        if variables.connecte == 1:
            # Si on est connecte, on active le client
            self.active_client()

        # Vérifi la réception de messages sur irc:
        if variables.connecte == 2:
            if variables.recoi_irc[0] != '':
                # print variables.recoi_irc[0]
                # On viens de recevoir un message, on ajoute le texte dans la liste
                self.recoi_msg_irc()
                variables.recoi_irc[0] = ''

            if variables.even_irc[0] == "join":
                self.ajout_utilisateur_irc()
                variables.even_irc = ["", "", ""]
            elif variables.even_irc[0] == "part":
                self.supprime_utilisateur_irc()
                variables.even_irc = ["", "", ""]
            elif variables.even_irc[0] == "quit":
                self.supprime_utilisateur_irc()
                variables.even_irc = ["", "", ""]

            if self.clignote_IRC == 1:
                if self.clignote_IRC_var == 1:
                    icone = QtGui.QIcon(dossier_racine + '/res/irc_crystal.png')
                    self.tray.setIcon(QtGui.QIcon(dossier_racine + '/icone.png'))
                    self.clignote_IRC_var = 0
                else:
                    icone = QtGui.QIcon(dossier_racine + '/res/irc_crystal_mp.png')
                    self.tray.setIcon(icone)
                    self.clignote_IRC_var = 1
                self.tabWidget.setTabIcon(3, icone)

        else:
            if variables.even_irc[0] == "err_pseudo":
                # Le pseudo est déjà utilisé, on se reconnecte:
                print "Pseudo déjà utilisé, on se reconnecte."
                self.redemarre_IRC()
                variables.even_irc[0] = ["", "", ""]
            # Fin IRC

        if os.path.exists(home + '/.djl/debog') == True:
            self.action_sortie_jeu.setEnabled(True)
        else:
            self.action_sortie_jeu.setEnabled(False)

        ##fichier = home + '/.djl/maj_liste'
        # Vérifi le fichier existe:
        # if os.path.exists(fichier) == True:
            # Si c'est le cas, on met à jour l'interface:

        # Met à jour toute la liste des jeux si demandé:
        if variables.maj_listejeux:
            self.maj_liste()
            variables.maj_listejeux = False
            # Supprime le fichier:
            # diff.supprime_fichier(fichier)

        # Bloque l'interface graphique quelques secondes après avoir lancé le jeu:
        # Correspond à n*itérarion de la boucle en ms
        if self.boucle_bloque_ui >= 15:
            self.listWidget.setEnabled(True)
            self.bloque_ui = 0
            # self.MessageLancement.close() #Ferme la fenêtre 'en cours de lancement...'

        if self.bloque_ui == 1:
            # self.listWidget.setEnabled(False)
            self.boucle_bloque_ui = self.boucle_bloque_ui + 1

        # Si le fichier de débogage a changé, on affiche une boite avec le message
        # d'erreur (mais il peut être filtré) (voir classe
        # msg_erreur(QtGui.QWidget) dans installe.py)
        if variables.erreur == 1:
            # print '>Anomalie au lancement du jeu'
            msg_erreur()
            variables.erreur = 0

        if variables.erreur == 2:
            Dialog = QtGui.QWidget(self)
            #ui = erreur_x11(Dialog)
            # ui.show()
            erreur_x11()
            variables.erreur = 0

    def etat(self, nom_jeu):
        '''Permet de savoir si le jeu est installé ou non
          Si etat = 0: pas installé, 1 = installé, 2 = téléchargé mais pas installé'''
        repertoire = config(info=2) + '/etat_jeux/'
        fichier = repertoire + nom_jeu

        if os.path.isdir(fichier):
            return

        # Vérifi si le fichier etat existe et l'utilise
        if os.path.exists(fichier) == True:
            txt_etat = open(fichier, 'r')
            etat = int(txt_etat.read())
            txt_etat.close()
        # Si le fichier etat qui n'existe pas, on part du principe que le jeu n'est pas installé
        else:
            etat = 0

        # print nom_jeu, str(etat)

        if etat == 0:
            self.boutton_installer.setText(i18n.traduc("Installer"))
            self.boutton_installer.setEnabled(True)
            self.boutton_supprimer.setEnabled(False)
            self.boutton_maj.setEnabled(False)
            self.label_4.setText(i18n.traduc("Etat: Non installe"))
            # print 'Le jeu n\'est pas installé'

        if etat == 1:
            self.label_4.setText(i18n.traduc("Etat: Installe"))
            self.boutton_installer.setText(i18n.traduc("Jouer"))
            self.boutton_installer.setEnabled(True)
            self.boutton_supprimer.setEnabled(True)
            # Verifi si la mise à jour est possible:
            self.verif_maj_jeu(nom_jeu)
            # print 'Le jeu est installé'

        if etat == 2:
            self.label_4.setText(i18n.traduc("Etat: Telecharge"))
            self.boutton_installer.setText(i18n.traduc("Installer"))
            self.boutton_installer.setEnabled(True)
            self.boutton_maj.setEnabled(False)
            # self.boutton_supprimer.setEnabled(True)
            # print 'Le jeu est en cours d\'installation'

        # Si l'etat est à 4, c'est qu'on a annulé le téléchargement
        if etat == 4:
            self.label_4.setText(i18n.traduc("Etat: Non installe"))
            self.boutton_installer.setText(i18n.traduc("Installer"))
            self.boutton_installer.setEnabled(True)
            self.boutton_supprimer.setEnabled(False)
            self.boutton_maj.setEnabled(False)
            modif_etat(nom_jeu, val_etat=0)
            etat = 0

        self.etat_actuel = etat

    # def event(self, event):
        #'''capture les evenements Q provenant de djl'''
        # pass
        # print event
        # print event.type()

    def It_Liste(self, iterateur):
        '''Converti l'itérateur donné en argument en liste, les éléments sont des chaine'''
        liste = []
        for i in range(len(iterateur)):
            # print type(iterateur[i])
            liste.append(str(iterateur[i]))
        return liste

    def GestionThemes(self):
        '''Gère les thèmes Qt de l'interface de djl.'''

        # Défini les thèmes par defaut (par ordre de priorité):
        themes = ["oxygen", "plastique"]
        trouve = False

        # Liste les thèmes disponibles sur le système:
        listethemes = self.It_Liste(QtGui.QStyleFactory.keys())
        for i in range(len(themes)):
            if themes[i] in listethemes or themes[i].capitalize() in listethemes:
                theme = themes[i]
                trouve = True
                break

        # Change le thème si on en a trouvé un, sinon Qt définira un thème par defaut:
        if trouve:
            QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(theme))

        # print "Thème actuel:", self.style().objectName()

# Futur, à faire pour djl 1.2.13
   # def ech_fenetre(self):
       #'''Passe de l'interface simple à l'étendue et vice/versa'''
       # Redémarre l'icone dans la barre des taches (si il n'existe pas, une exception sera levée et rien ne se passera):
       # Attention, ça merde, il faudrait relancer l'icone dans la barre des taches pour bien faire
       # try:
           # self.removeWidget(self.tray)
           # self.barre_icone()
       # except AttributeError, x: print "Merde:", x

       # print self.centralWidget()

       # if self.int_etendue == 0:
           # print "Passage à interface simpe"
           #self.action_change_ui.setText(i18n.traduc("Passer a l'interface etendue"))

           # self.tabWidget.hide()

           # self.listWidget.setParent(self)
           # self.setCentralWidget(self.listWidget)

           #taillex, tailley = 250, 400
           # self.resize(QtCore.QSize(QtCore.QRect(800,600,taillex,tailley).size()).expandedTo(self.minimumSizeHint()))
       # else:
           # print "Passage à interface étendue"
           #self.action_change_ui.setText(i18n.traduc("Passer a l'interface simple"))

           # self.listWidget.setParent(self.tab) #C'est ici que ça merde
           # self.setCentralWidget(self.centralwidget)

           # self.tabWidget.show()

    def __init__(self, app):
        '''Initialisation de djl.'''
        QtGui.QMainWindow.__init__(self)
        self.app = app

        # print "Id X de djl:", self.winId()
        try:
            print("Composition de l'affichage: " +
                  str(QtGui.QX11Info.isCompositingManagerRunning()))
        except AttributeError, x:
            print x

        if config(info=10) == '1':
            self.int_etendue = 1
        else:
            self.int_etendue = 0
        # self.ech_fenetre() #Futur 1.2.13

        # Configure l'interface utilisateur.
        self.setupUi(self)
        # self.GestionThemes()

        try:
            QtCore.QCoreApplication.setApplicationName("djl")
            QtCore.QCoreApplication.setApplicationVersion(str(interface.version()))
        except:
            pass

        # Affiche ou non l'icone dans la boite à miniatures suivant la configuration:
        if int(config(info=3)) == 1 and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            self.barre_icone()
            # Nombre d'ajouts dans le menu, sera incrémenté au fur et à mesure que
            # l'on en ajoute dans le menu
            self.nb_menu_mini = 0
            self.Mapper = QtCore.QSignalMapper(self)  # Pour le sous-menu de lancement des jeux
            self.Mapper.connect(self.Mapper, QtCore.SIGNAL("mapped(int)"), self.lance_minitature)

        # On s'assure que le répertoire pour héberger le dépot existe:
        self.cree_reps()

        # Récupère la langue qui sera utilisé pour le WS ou le mini navigateur
        # (pour envoyer des entrée)
        self.lang = config(info=9, sec=1)

        # Serveurs pour les mises à jours (en fonction du fait que l'on utilise ou
        # non la version de développement
        if variables.version_dev == 1:
            self.serveur_maj = variables.SERVEUR_DEV[:]
        else:
            self.serveur_maj = variables.SERVEUR_STABLE[:]

        # On créé le dépot, soit depuis l'internet, soit depuis le fichier en dur
        if self.int_etendue == 1:
            self.n_jeu_courant = -1  # Jeu courant selectionné dans le dépôt
            self.SetupUi_Depot()

        # Methode pour sauver et charger le depot (methode perso: 2, pickle: 1) #temp
        self.methode_depot = 1
        # Utilise le mode automatique, si le dépot existe en dur, il est utilisé
        # au lancement (plus rapide)
        self.charge_depot()
        # self.connexion_SOAP() #Charge directement le dépot en ligne au démarrage (très lent)
        # Charge le dépot en ligne au démarrage (Dans un thread séparé, pour pas
        # ralentir le lancement) #temp
        self.Thread_depot()

        # Variable qui défini si l'on utilise l'interface étendu ou pas:
        if self.int_etendue == 1:
            # Va cherche les propriétés de la fenêtre principale (taille, position)
            self.readSettings()
        else:  # Si c'est l'interface minimale, on force l'utilisation d'une petite fenêtre
            taillex, tailley = 250, 400
            self.resize(QtCore.QSize(QtCore.QRect(800, 600, taillex, tailley).size())
                        .expandedTo(self.minimumSizeHint()))
            # x, y = 1280, 1024-40 #Taille de l'écran
            #ecran = QtGui.QX11Info.appScreen()
            ##x, y = QtGui.QX11Info.appDpiX(ecran), QtGui.QX11Info.appDpiY(ecran)
            # print x, y
            # print QtGui.QX11Info.display()
            # print QtGui.QDesktopWidget.numScreens()
            #self.move((QtCore.QVariant(QtCore.QPoint(x-taillex-5, y-tailley-5))).toPoint())

        #
        # Liste des jeux:
        # Dès le démarrage, on vérifi si on peut écrire dans le répertoire de djl:
        variables.type_maj = 0
        try:
            open(os.getcwd() + '/test.tmp', 'w')
            open(os.getcwd() + '/../test.tmp', 'w')
        except IOError:
            variables.type_maj = 1

        try:
            os.remove(os.getcwd() + '/test.tmp')
            os.remove(os.getcwd() + '/../test.tmp')
        except OSError:
            variables.type_maj = 1

        if variables.type_maj == 1:
            self.action_maj.setEnabled(False)

            print i18n.traduc_ascii("Impossible d'ecrire dans le repertoire de djl, il ne sera donc pas mis a jour.")
            diff.ecrit_historique(
                i18n.traduc("Impossible d'ecrire dans le repertoire de djl, il ne sera donc pas mis a jour."))
            # print i18n.traduc_ascii("Impossible d'ecrire dans le repertoire de djl, la mise a jour sera installee dans ~/.djl/src")
            #diff.ecrit_historique(i18n.traduc("Impossible d'ecrire dans le repertoire de djl, la mise a jour sera installee dans ~/.djl/src"))

        # Défini si djl est lancé (afin de n'activer certaine fonctions qu'une
        # seule fois après son lancement)
        self.djl_lance = 0

        # Variables pour bloquer l'interface principale après que l'on ai lancé un
        # jeu, afin d'éviter que l'utilisateur lance (bétement) plusieurs fois le
        # jeu si il met du temps à démarrer
        self.bloque_ui = 0
        self.boucle_bloque_ui = 0

        # Créé la liste des jeux installés
        #(sauf si l'onglet par défaut est le dépôt, car il rafraichira lui même la liste après avoir téléchargé les informations du dépôt).
        if config(info=5) != '2' or self.int_etendue == 0:
            self.liste_jeux_installe()

            # Le second les raccourcis .desktop standards
            self.liste_raccourcis()

        self.djl_lance = 1

        # Si c'est l'interface étendue Future, djl 1.2.13, enlever la condition
        if self.int_etendue == 1:
            # Si passe à un, on fait clignoter l'icone du client IRC pour dire qu'il y
            # a un message privé
            self.clignote_IRC = 0
            self.clignote_IRC_var = 0
            # Envoi l'affichage du client IRC
            self.setupUiIRC()
            # On init le client IRC
            self.init_IRC()

            # Envoi l'affichage du depot:
            # self.SetupUi_Depot()
            # Selectionne le premier jeu de la liste dans le dépot, sinon c'est le
            # dernier ajouté par defaut.
            self.widget_liste_jeux.setCurrentRow(0)

            # Envoi l'affichage du gestionnnaire des modules:
            self.Init_modules()

            # Envoi l'affichage des flux RSS:
            self.SetupUi_RSS()
            # Demande le rafraichissement des flux RSS
            self.maj_RSS()

            # On se place dans l'onglet défini par l'utilisateur:
            self.tabWidget.setCurrentIndex(int(config(info=5)))
            # Endif//

        # Au démarrage, vire les éventuels fichiers indésirables, sinon djl peut bloquer:
        diff.supprime_fichier(config(info=2) + str(config(info=14)) + '.directory')

        # Vérifi au démarrage si une mise à jour est disponible suivant la configuration:
        # A condition que l'utilisateur ait les droits nécessaires:
        # if int(config(info=4)) == 1 and self.connecte_ws == 1 and variables.type_maj == 0:
        if int(config(info=4)) == 1 and variables.type_maj == 0:
            # La mise à jour se fera depuis la prochaine itération de la boucle self.timer
            self.t_maj = 1
        else:
            self.t_maj = 0

        # Ajoute l'intance de la classe principale de djl dans les variables.
        variables.instance = self

        # Lance la boucle principale de djl.
        self.timer = QtCore.QBasicTimer()
        self.timer.start(200, self)

# Nettoyage des fichiers quand on quitte.
atexit.register(diff.nettoyage, n=1)

if __name__ == "__main__":
    version = interface.version()
    app = QtGui.QApplication(sys.argv)
    window = Ui_Djl(app)
    window.show()
    sys.exit(app.exec_())
