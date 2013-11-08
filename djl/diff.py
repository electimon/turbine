# -*- coding: utf-8 -*-

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

'''Fonctions diverses utilisés par l'interface principale'''

#import SOAPpy

from PyQt4 import QtCore, QtGui
import os, sys, urllib, codecs, time, threading, subprocess, socket,  shutil
import tarfile #uniquement pour décompresser la mise à jour.
import interface, navigateur,  import_raccourcis
#from installe import *
from installe import  modif_etat
from variables import variables,  dossier_racine,  home

from config import config
import ajout_jeu, gdep
import i18n

#home = os.path.expanduser('~')
#dossier_racine = os.getcwd()

#Fenetre de mise à jour:
class Main(object):
   #Liste globale pour définir la liste des jeux installés:
    global liste_jeux
    liste_jeux = []
    type_jeu = 'depot'

    def cherche_jeu(self):
        '''La fonction est appelé quand on tape du texte dans la barre de recherche de la liste de jeux principale
        On parcours la liste des jeux et on donne le focus si le texte correspond à un nom de jeu.'''
        #Parcours la liste des jeux (jeux du dépot + raccourcis) et cherche si ça correspond
        for id in range(len(self.liste_jeux_f)):
            ##if ".desktop" in self.liste_jeux_f[id]:
                ###Recherche en fonction de la variable "Name" du raccourci, plus lent.
                ##nom = str(self.lit_fichier_desktop(fichier=self.liste_jeux_f[id], type_info='Name')).lower()
            ##else:
                ##nom = self.liste_jeux_f[id].lower()
            
            nom = self.liste_jeux_f[id].lower()
            txt = unicode((self.recherche_jeu.text())).encode('utf-8').lower()
            if txt in nom:
                #print nom
                self.listWidget.setCurrentRow(id)
                return None
                
        #Si on a toujours rien trouvé, on remet à au début de la liste
        self.listWidget.setCurrentRow(0)

    def detail_jeux(self, no_jeu=0, type_info = 'nom'): 
        '''Récupère les informations d'un jeu donné sur le webservice (dans le dépot)'''
        sortie = 'nul'
        if type_info == 'version':
            sortie = self.parse_detailjeux(no_jeu, 0)
        elif type_info == 'site':
            try:
                sortie = self.parse_detailjeux(no_jeu, 12) #url_site_local
            except:
                sortie = self.parse_detailjeux(no_jeu, 1) #url
        elif type_info == 'telecharge':
            sortie = self.parse_detailjeux(no_jeu, 2)
        elif type_info == 'genre':
            try:
                sortie = self.parse_detailjeux(no_jeu, 3)
            except:   
                sortie = ""
        elif type_info == 'licence':
            sortie = self.parse_listelicence(int(self.parse_detailjeux(no_jeu, 4)))
        elif type_info == 'taille':
            sortie = self.parse_detailjeux(no_jeu, 5)
        elif type_info == 'plateforme':
            sortie = self.parse_detailjeux(no_jeu, 6)
        elif type_info == 'icone':
            sortie = self.parse_detailjeux(no_jeu, 7)
        elif type_info == 'image':
            sortie = self.parse_detailjeux(no_jeu, 8)
        elif type_info == 'commande':
            sortie = self.parse_detailjeux(no_jeu, 9)
        #elif type_info == 'dossier':
            #sortie = self.parse_detailjeux(no_jeu, 10)
        elif type_info == 'description':
            sortie = self.parse_detailjeux(no_jeu, 11)
        elif type_info == 'article': #Site officiel != article
            #sortie = self.parse_detailjeux(no_jeu, 12) #url_site_local
            try:
                sortie = self.parse_detailjeux(no_jeu, 13) #url_info
            except: pass
        return sortie

    #Ajoute un jeu windows à la liste avec Wine.
    def fonc_wine(self):
        #Vérifi si Wine est installé:
        if os.path.exists('/usr/bin/wine') or os.path.exists('/usr/local/bin/wine') or os.path.exists(home+'.local/bin/wine'):
            ui = Ui_Wine(self)
            ui.show()
        else:
            #texte = i18n.traduc("Le logiciel Wine n'a pas ete trouve
            interface.info_box(i18n.traduc("Le logiciel Wine n'a pas ete trouve, veuillez l'installer pour continuer."))
            
    def change_ui(self):
        #Change la configuration:
        fichier = open(home + '/.djl/config', 'r')
        fichier_cfg = fichier.readlines()
        fichier.close()
        
        #Remplace la ligne de configuration
        if config(info=10) == '1':
            fichier_cfg[10] = ('type_gui = 0\n')
            type_it = 1
        if config(info=10) == '0':
            fichier_cfg[10] = ('type_gui = 1\n')
            type_it = 0
        
        #Boucle pour ré-écrire le fichier de configuration:
        fichier = open(home + '/.djl/config', 'w')
        boucle = 0
        while boucle < len(fichier_cfg):
            fichier.write(fichier_cfg[boucle])
            boucle = boucle + 1
        fichier.close()

       ##Redémarre l'interface:
       #if type_it == 1:
           #print "Passage à interface simpe"
           #self.int_etendue = 0
           ##self.ech_fenetre() #Futur, djl 1.2.13
           
           ##self.setupUi(self)
           ##taillex, tailley = 250, 400
           ##self.resize(QtCore.QSize(QtCore.QRect(800,600,taillex,tailley).size()).expandedTo(self.minimumSizeHint()))
       #else:
           #print "Passage à interface étendue"
           #self.int_etendue = 1
           ##self.ech_fenetre() #Futur, djl 1.2.13

           ##self.setupUi(self)
           ##self.readSettings()
           ##self.setupUiIRC()
           ##self.Init_modules()
           ##self.SetupUi_RSS()
           ##self.maj_RSS()
           
       ##self.liste_jeux_installe()
       ##self.liste_raccourcis()
        
        self.redemarre() #temp, avant
    
    def lance_navigateur(self, lien, type=0):
        '''Lance la variable lien dans un navigateur internet, si type=0, on utilise le nav par défaut.
        Si il fait 1, on utilise le mode auto, djlfox ou le nav par defaut, en fonction de la version de Qt4'''
        if type == 1:
            try:
                from PyQt4 import QtWebKit
                ui = navigateur.Ui_navigateur(self, lien)
                ui.show()
            except ImportError:
                #Si l'utilisateur n'a pas QtWebKit, on utilisera un "vrai" navigateur
                type = 0
        
        if type == 0:
            _navigateur = config(info=6) 
            if _navigateur == '' or _navigateur == '':
                from webbrowser import open_new as _navigateur
                _navigateur(lien)
            else:
                lien = " " + lien #On ajoute un espace au début du lien, au cas où...
                subprocess.Popen(_navigateur + lien, executable=None, shell=True)

    def recherche_internet_jeu(self):
        '''Recherche sur internet d'un raccourcis depuis le menu contextuel dans la fenêtre principale'''
        jeu_actuel = self.liste_jeux_f[self.listWidget.currentRow()]
        jeu_actuel = jeu_actuel.replace(".desktop",  "").capitalize()
        
        if "-" in jeu_actuel:
            jeu_actuel = jeu_actuel.replace("-",  "+")
        
        if "_" in jeu_actuel:
            jeu_actuel = jeu_actuel.replace("_",  "+")
        
        if " " in jeu_actuel:
            jeu_actuel = jeu_actuel.replace(" ",  "+")
        lien = "http://www.exalead.com/search/results?q=" + jeu_actuel + "&sourceid=djl-linux&$rcexpanded=true"

        self.lance_navigateur(lien)

    def navigateur_article(self):
        '''Ouvre un navigateur avec l'article en ligne associé au jeu du dépot'''
        self.lance_navigateur(self.lien_article, type=1)
        
    def navigateur_site(self):
        '''Ouvre un navigateur avec le site internet associé au jeu du dépot'''
        self.lance_navigateur(self.lien_site)

    def affiche_icone(self,  no_description=-1):
        '''Récupère et affiche l'icône du jeu sélectionné dans le dépôt'''
        nom_jeu = self.nom_jeu_depot()
        if no_description == -1:
            no_description = self.trouve_index(nom_jeu)
            
        #Trouve l'emplacement de l'icone
        nom_icone = self.detail_jeux(no_description, type_info = 'icone')
        if nom_icone == "":
            adresse = dossier_racine
            nom_icone = "/icone.png"

        else:
            adresse = config(info=2) + '/' + config(info=14)+ '/icos/' # + jeu_courant
            if os.path.exists(adresse + nom_icone) == False or self.entete_fichier(adresse + nom_icone) == 1:
                urllib.urlretrieve('http://djl.jeuxlinux.fr/images/logo/' + nom_icone, adresse + nom_icone ,reporthook=None)
               #print "Icone téléchargé"
            else:
                #Si l'icone existe mais qu'elle fait moins que 1Ko, on force le téléchargement d'une nouvelle
                if os.path.getsize(adresse + nom_icone) <= 1024:
                    urllib.urlretrieve('http://djl.jeuxlinux.fr/images/logo/' + nom_icone, adresse + nom_icone ,reporthook=None)
                   #print "Icone téléchargé"
                
        #Affiche l'icone
        self.widget_icone.setPixmap(QtGui.QPixmap(adresse+nom_icone))

    def affiche_image(self,  no_description=-1):
        '''Récupère et affiche l'image du jeu séléctionné dans le dépôt
        Si force=1, on force le téléchargement (par exemple si l'image est corrompue)'''

        nom_jeu = self.nom_jeu_depot()
        if no_description == -1:
            no_description = self.trouve_index(nom_jeu)
            
        #Trouve l'emplacement de l'image
        nom_image = self.detail_jeux(no_description, type_info = 'image')
        if nom_image == "":
            return
        adresse = config(info=2) + '/' + config(info=14) + '/imgs/' # + jeu_courant

        if os.path.exists(adresse + nom_image) == False  or self.entete_fichier(adresse + nom_image) == 1:
            urllib.urlretrieve('http://djl.jeuxlinux.fr/images/' + nom_image, adresse + nom_image ,reporthook=None)
           #print "Image téléchargé"
        else:
            #Si l'image existe mais qu'elle fait moins que 10Ko, on force le téléchargement d'une nouvelle
            if os.path.getsize(adresse + nom_image) <= 10240:
                urllib.urlretrieve('http://djl.jeuxlinux.fr/images/' + nom_image, adresse + nom_image ,reporthook=None)
               #print "Image téléchargé"

        #Affiche l'image
        self.widget_capture.setPixmap(QtGui.QPixmap(adresse+nom_image))

    def fermer(self):
        '''Si l'on clique sur fermer la fenêtre'''
        #Créé le fichier temporaire pour demande le rafraichissement de l'interface principale:
        #creer_fichier_maj()
        
        #Ferme la fenêtre:
        self.close()

    def quitte(self):
        '''Si l'on choisi de quitter le programme'''
        #print i18n.traduc_ascii("Quitte")
        ecrit_historique(_('djl quitte.'))
        if config(info=10) == "1":
            self.writeSettings()
        #self.close()
        
        self.deco_irc()
        self.Quitte_()

    def Quitte_(self):
        '''Ferme un peu après l'appel pour éviter des problèmes avec les slots de Qt4'''
        #print("Fin") 
        time.sleep(0.3)
        self.app.exit(0)
        #sys.exit(self.app)

    def verif_maj_jeu(self, nom_jeu):
        '''Vérifi si le jeu courant est à jours'''
        no_description = self.widget_liste_jeux.currentRow()

        #Trouve la version du jeu en dépot
        version = self.detail_jeux(no_description, type_info = 'version')
        #Vire le numéro de version du dépot pour n'utiliser que le numéro de version du jeu:
        version_ = version.split('-')
        version = str(version_[0])

        #Trouve la version du jeu installé:
        try:
            fichier = config(info=2) + '/jeux/' + nom_jeu + '/version'
            fichier_v = open(fichier, 'r')
            version_installe = fichier_v.read()
            fichier_v.close()
            
            version_installe_ = version_installe.split('-')
            version_installe = str(version_installe_[0])
        except IOError, x:
            #Si il ne trouve pas la version parce que le fichier n'existe pas, on le créé depuis la version dans le fichier de définition
            print "self.verif_maj_jeu():", x
            version_installe = version

        #On vire les sauts de lignes superflus:
        version = version.replace('\n', '')
        version_installe = version_installe.replace('\n', '')
        
        #print "Versions:",version_installe, version

        #Si les version sont différentes, on permet la mise à jour:
        if version_installe != version and version_installe != 'nul':
            self.boutton_maj.setEnabled(True)
        #Sinon on désactive le bouton de la mise à jour:
        else:
            self.boutton_maj.setEnabled(False)

    def supprimer(self, menu_c=0):
        '''Fonction, supprime le jeu (Son répertoire et change l'état à 0)
        Si menu_c == 1, on a demandé la suppression depuis l'interface principale, sinon c'est depuis le dépôt.'''
        #self.info()
        if menu_c:
            nom_jeu = self.nom_jeu_pr()
        else:
            nom_jeu = self.nom_jeu_depot()

        if nom_jeu != '':
            try:
                shutil.rmtree(config(info=2) + '/jeux/' + nom_jeu)
            except:
                print i18n.traduc_ascii("Attention, le jeu n'a pas ete supprime correctement: " + nom_jeu)
        else:
            print "Chemin du jeu introuvable pour le supprimer"
            
        #Modifi l'état du jeu: 0 = non installé
        modif_etat(nom_jeu, val_etat = 0)
        self.etat(nom_jeu)

        #Demande le rafraichissement de l'interface principale:
        self.maj_liste()

    def fen_arguments(self):
        '''Affiche la fenêtre de configuration des arguments de lancement'''
        #Dialog = QtGui.QWidget(self)
        ui = interface.Ui_Arguments(self)
        ui.show()
    
    def trouve_args(self, nom_jeu):
        '''On cherche ici si des arguments sont spécifiés, pour lancer le jeu:'''
        fichier = config(info=2) + '/args'
        #Si le fichier n'existe pas, il est créé
        fichier = open(fichier, 'a+')
        
        txt_args = fichier.readlines()
        fichier.close()
        
        #boucle pour vérifier qu'il y ait bien des arguments pour le jeu en question:
        boucle = 0
        while boucle < len(txt_args):
            
        #for i in txt_args:
            #Si c'est le cas, on renvoi les arguments
            if nom_jeu in txt_args[boucle]:
                txt_args = txt_args[boucle].split(':')
                print '>Arguments:', str(txt_args[1])
                return txt_args[1]
            boucle = boucle + 1
            
        #Si il n'a rien trouvé, on retourne un blanc
        return ''

    def crer_entree(self):
        '''Affiche la fenêtre pour la création d'une nouvelle entrée (dans un navigateur)'''
        #lang = int(self.lang)-1
#        try:
#            #Si une exception est levée, c'est que le dépot n'est pas prêt, car on utilise l'interface minimale.
#            #self.connexion_SOAP() est censé être appelé quand on va dans l'onglet dépôt
#            lang = self.liste_lang[0][lang]['value'][0][1]['value']
#        except AttributeError:
#            #self.Thread_depot()
#            self.connexion_SOAP()
#            self.crer_entree()
#            return
        lang = config(info=9).split('_')[0]
        lien ="http://djl.jeuxlinux.fr/djl_addgame_" + str(lang) + ".php"
        self.lance_navigateur(lien,type=1)

    def configuration(self):
        '''Envoi l'affichage de la fenêtre de configuration'''
        import configuration
        Dialog = QtGui.QWidget(self)
        ui = configuration.Ui_Configuration(Dialog)
        ui.show()
    
    def nom_jeu_depot(self):
        '''Renvoi le nom du jeu actuellement selectionné dans le dépôt'''
        no = self.widget_liste_jeux.currentRow()
        try:
            return self.liste_jeux_ok[no]
        except IndexError:
            return self.liste_jeux_ok[0]
    
    def nom_jeu_pr(self):
        '''Renvoi le nom du jeu actuellement selectionné dans la fenêtre principale'''
        no = self.listWidget.currentRow()
        return self.liste_jeux_f[no]
    
    def maj_jeu(self):
        '''Met à jour le jeu courant  (supprime l'ancienne et réinstalle la nouvelle version)'''
        #Supprime le jeu (ancienne version)
        self.supprimer()

        #Lance l'installation de la nouvelle version:
        self.boutton_installer.setEnabled(False)
        
        #Envoi la fenêtre de téléchargement:
        #self.telecharge_ui()
        self.installer_jouer()

    def closeEvent(self, event):
        '''A la fermeture de la fenetre...'''
        #variables.depot = 0
        #self.writeSettings()
        
        #Si il n'y a pas l'icone dans la barre des taches, on quitte
        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable() or config(info=3) == '0':
            self.quitte()
        #Si il y a une icone dans la barre de taches, on ne ferme pas l'application, on la cache:
        elif config(info=3) == '1':
            event.ignore()
            self.hide()

        #########################################
        
    #Liste des jeux >:
    def barre_icone(self):
        '''Permet l'affichage d'une icone dans la barre des titres (tray)'''
        interface = config(info=10)
        print ">>>", interface
        
        self.tray = None
        if QtGui.QSystemTrayIcon.isSystemTrayAvailable() == True:
            self.tray = QtGui.QSystemTrayIcon(self)

            icone = QtGui.QIcon((dossier_racine + '/icone.png'))
            self.tray.setIcon(icone)
            self.tray.setToolTip(i18n.traduc("Cliquez pour afficher le menu principal"))

            #Défini le menu:
            self.menu_b=QtGui.QMenu(self)

            self.action_Fenetre_principale = QtGui.QAction(self)
            self.action_Fenetre_principale.setObjectName("action_Fenetre_principale")
            
            icone = QtGui.QIcon(dossier_racine + '/res/maj.png')
            self.action_Fenetre_principale.setIcon(icone)
            
            ###
            if interface == "1":
                self.a_affiche_actus = QtGui.QAction(self)
                self.a_affiche_actus.setObjectName("a_affiche_actus")
                self.a_affiche_jeux = QtGui.QAction(self)
                self.a_affiche_jeux.setObjectName("a_affiche_jeux")
                self.a_affiche_depot = QtGui.QAction(self)
                self.a_affiche_depot.setObjectName("a_affiche_depot")
                self.a_affiche_irc = QtGui.QAction(self)
                self.a_affiche_irc.setObjectName("a_affiche_irc")
                
            #Sous menu pour lancer des jeux depuis la miniature
            self.menu_lance = QtGui.QMenu(self)
            
            self.menu_b.addMenu(self.menu_lance)
            self.menu_b.addSeparator()
            self.menu_b.addAction(self.action_Fenetre_principale)
            #self.menu_b.addAction(self.actionDepot)
            self.menu_b.addSeparator()
            if interface == "1":
                self.menu_b.addAction(self.a_affiche_actus)
                self.menu_b.addAction(self.a_affiche_jeux)
                self.menu_b.addAction(self.a_affiche_depot)
                self.menu_b.addAction(self.a_affiche_irc)
                self.menu_b.addSeparator()
                
            self.menu_b.addAction(self.actionConfig)
            self.menu_b.addAction(self.actionQuitter)
            
            if interface == "1":
                icone = QtGui.QIcon(dossier_racine + '/res/actus.png')
                self.a_affiche_actus.setIcon(icone)
                icone = QtGui.QIcon(dossier_racine + '/res/jeux_oxygen.png')
                self.a_affiche_jeux.setIcon(icone)
                icone = QtGui.QIcon(dossier_racine + '/res/importer.png')
                self.a_affiche_depot.setIcon(icone)
                icone = QtGui.QIcon(dossier_racine + '/res/irc_crystal.png')
                self.a_affiche_irc.setIcon(icone)
            
            icone = QtGui.QIcon(dossier_racine + '/res/jeux_oxygen.png')
            self.menu_lance.setIcon(icone)
            
            ###
            
            self.tray.setContextMenu(self.menu_b)
            self.tray.connect(self.tray, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.clique_icone_barre)
            
            self.action_Fenetre_principale.connect(self.action_Fenetre_principale, QtCore.SIGNAL("triggered()"), self.clique_icone_barre)            
            
            if interface == "1":
                self.a_affiche_actus.connect(self.a_affiche_actus, QtCore.SIGNAL("triggered()"), self.affiche_actus)
                self.a_affiche_jeux.connect(self.a_affiche_jeux, QtCore.SIGNAL("triggered()"), self.affiche_liste_jeux)
                self.a_affiche_depot.connect(self.a_affiche_depot, QtCore.SIGNAL("triggered()"), self.affiche_depot)
                self.a_affiche_irc.connect(self.a_affiche_irc, QtCore.SIGNAL("triggered()"), self.affiche_irc)
            
            self.menu_lance.setTitle(i18n.traduc("Jouer"))
            
            self.action_Fenetre_principale.setText(i18n.traduc("Afficher/Masquer fenetre principale"))
            if interface == "1":
                self.a_affiche_actus.setText(i18n.traduc("Actualites"))
                self.a_affiche_jeux.setText(i18n.traduc("Jeux"))
                self.a_affiche_depot.setText(i18n.traduc("Depot"))
                self.a_affiche_irc.setText(i18n.traduc("IRC"))
            self.tray.show()

    def lance_minitature(self, jeu=0):
        '''Quand on lance un jeu depuis la boite à miniatures'''
        self.listWidget.setCurrentRow(int(jeu))
        self.lance()

    def affiche_actus(self):
        '''Affiche la fenêtre principale sur l'onglet des actualités.'''
        self.show()
        self.tabWidget.setCurrentIndex(0)
        
    def affiche_liste_jeux(self):
        '''Affiche la fenêtre principale sur l'onglet de la liste des jeux.'''
        self.show()
        self.tabWidget.setCurrentIndex(1)
        
    def affiche_depot(self):
        '''Affiche la fenêtre principale sur l'onglet du dépôt.'''
        self.show()
        self.tabWidget.setCurrentIndex(2)
        
    def affiche_irc(self):
        '''Affiche la fenêtre principale sur l'onglet du canal IRC.'''
        self.show()
        self.tabWidget.setCurrentIndex(3)
        
    def boite_infos(self):
        '''Quand on clique sur "Informations" dans le menu contextuel de la fenêtre principale, 
        on affiche des informations sur le jeu ou le raccourcis courant.'''
        #print "Informations..."
        
        nom = self.liste_jeux_f[self.listWidget.currentRow()]
        if ".desktop" in nom:
            raccourci = 1
            jeu_win = 0
            cmd_sys = 0
            #fichier = config(info=2) + '/raccourcis/' + nom
            binaire = self.lit_fichier_desktop(nom, type_info = 'Exec')
            
            if "\n" in binaire:
                binaire=binaire.replace("\n","")
            if "'" in binaire:
                binaire=binaire.replace("'","")
            if '"' in binaire:
                binaire=binaire.replace('"','')
            
            #Si le chemin n'est pas absolu, c'est une commande système...
            if not "/" in binaire:
                cmd_sys = 1
                if " " in binaire:
                    binaire=binaire.split(" ")
                    binaire=binaire[0]
                    
                if os.path.exists("/usr/bin/" + binaire) == True:
                    binaire = "/usr/bin/" + binaire
                elif os.path.exists("/usr/local/bin/" + binaire) == True:
                    binaire = "/usr/local/bin/" + binaire
                elif os.path.exists(home + "/.local/bin/" + binaire) == True:
                    binaire = home + "/.local/bin/" + binaire
                
                #if os.path.exists("/usr/local/games/" + binaire) == True:

            #Si c'est un jeu Windows avec Wine...
            elif "wine " in binaire or ".wine/" in binaire:
                jeu_win = 1
            #Il faut filtrer à fond pour réussir à trouver le fichier .exe avec la syntaxe des raccourcis Wine
                if "C:" in binaire:
                    binaire = binaire.split("C:")
                    if "wine" in binaire[0]:
                        binaire = home+"/.wine/drive_c/"+ binaire[1]
                    else:
                        binaire=home+"/.wine/drive_c/"+ binaire[0]

                if "\\" in binaire:
                    binaire = binaire.replace("\\","/")
                if "//" in binaire:
                    binaire = binaire.replace("//","/")
                    
                if "wine /" in binaire:
                    binaire = binaire.replace("wine /","/")

                if "/ " in binaire:
                    binaire = binaire.replace("/ ","\ ")
                    
                if os.path.exists(home + "/.wine/drive_c/" + binaire) == True:
                    binaire = home + "/.wine/drive_c/" + binaire
                
                if ".exe" in binaire:
                    bin_ = binaire.split(".exe")
                    if " -" in bin_[1]:
                        #print bin_
                        #binaire=binaire.replace(str(bin_),"")
                        binaire = bin_[0]+".exe"
                
                #Si le dernier caractère est un espace, on le supprime
                if binaire[len(binaire)-1] == " ":
                    chaine = ""
                    for i in range(len(binaire)):
                        if i != len(binaire)-1:
                            chaine = chaine+binaire[i]
                    binaire=chaine
            
        #Sinon c'est un jeu installé depuis le dépôt
        else:
            raccourci = 0
            repertoire = config(info=2) + '/jeux/' + nom
            commande = self.detail_jeux(self.trouve_index(nom), type_info = 'commande')
            
            nb_fichier = os.listdir(repertoire)
            if 'src' in nb_fichier:
                nb_fichier.remove('src')
            if '.directory' in nb_fichier:
                nb_fichier.remove('.directory')
            if 'version' in nb_fichier:
                nb_fichier.remove('version')

            #Si n'y a qu'un fichier/dossier, c'est que nous ne sommes pas dans le répertoire racine du jeu, mais dans son répertoire parent
            if len(nb_fichier) == 1:
                #Donc on prend le bon dossier:
                repertoire = (repertoire + "/" + nb_fichier[0])
            binaire = repertoire + "/" + commande
            
            #Va chercher la version du jeu installé
            fichier_version = config(info=2) + '/jeux/' + nom + '/version'
            fichier_v = open(fichier_version, 'r')
            version_installe = fichier_v.read()
            
            if "-r" in version_installe:
                version_installe=version_installe.split("-r")
                version_installe=version_installe[0]
            
            fichier_v.close()
        
        #print ">"+binaire+"<"
        
        if raccourci == 1:
            texte = nom
            texte = texte + "\n" + i18n.traduc("Type") + ": "  + i18n.traduc("raccourci")
            #Dernier accès au fichier: (utiliser time.localtime pour utiliser la date sous forme de liste)
            if os.path.exists(binaire) == True:
                texte = texte + "\n" + i18n.traduc("Dernier lancement") + ": "  + time.ctime(os.stat(binaire)[7])
                texte = texte + "\n" + i18n.traduc("Date de creation") + ": "  + time.ctime(os.stat(binaire)[8])

            if jeu_win == 1:
                texte = texte + "\n" + i18n.traduc("Jeu Windows utilisant Wine")
            elif cmd_sys == 1:
                texte = texte + "\n" + i18n.traduc("Commande systeme") + ": " + binaire

            
        elif raccourci == 0:
            texte =  nom + " " + version_installe
            texte = texte + "\n" + i18n.traduc("Type") + ": "  + i18n.traduc("Jeu installe depuis le depot")
            texte = texte + "\n" + i18n.traduc("Repertoire d'installation") + ": "  + repertoire
            texte = texte + "\n" + i18n.traduc("Dernier lancement") + ": "  + time.ctime(os.stat(binaire)[7])
            #Dernier accès au fichier: (utiliser time.localtime pour utiliser la date sous forme de liste)
            texte = texte + "\n" + i18n.traduc("Date d'installation") + ": "  + time.ctime(os.stat(binaire)[8])
            
            texte = texte + "\n" + i18n.traduc("Espace utilise") + ": "  + self.espace_utilise(repertoire) + " "  + i18n.traduc("Mo.")

        interface.info_box(texte, i18n.traduc("Informations"))
    
    def espace_utilise(self, rep):
        '''Fonction pour calculer l'espace utilisé par un répertoire donné (rep) et la retourn en Mo'''
        taille = 0.
        fichier=[] 
        for root, dirs, files in os.walk(rep): 
            for i in files: 
                fichier.append(os.path.join(root, i)) 
                taille = taille+os.path.getsize(root+"/"+i)
                #print root,i
        #On converti des octets vers les Mo.
        taille=taille/1048576
        
        #Ne garde que deux chiffres après la virgule
        taille=round(taille,2)
        return str(taille)

    def clique_icone_barre(self,raison=QtGui.QSystemTrayIcon.Trigger):
        '''Si on fait un clique gauche sur l'icone dans la barre des taches'''
        if raison == 3 or raison == 2: #Si on clique ou double clique
            if self.isHidden() == True:
                if config(info=10) == "1":
                    if self.clignote_IRC == 1:
                        self.tabWidget.setCurrentIndex(3)
                        self.clignote_IRC = 0
                self.show()
            else:
                self.hide()

        #Si on fait un clique droit sur l'icone dans la barre des taches:
        if raison == 1:
            self.menu_b.show()
    
    def trouve_serveur_maj(self, notif=0, serveur=0):
        '''Test les différents serveurs de la liste afin de s'assurer qu'ils fonctionnent'''
        #print ">Cherche serveur", serveur
        socket.setdefaulttimeout(5) #Temps de réponse avant de passer au serveur suivant
        
        fichier = self.serveur_maj[serveur] + "/maj_djl/version_djl"
        fichier_t= home + '/.djl/maj_djl.tmp'
        try:
            urllib.urlretrieve(fichier, filename=fichier_t, reporthook=None)
            #print "Trouvé:", serveur
            self.verif_maj_djl(notif, self.serveur_maj[serveur])
            #return serveur
        except IOError:
            if serveur < len(self.serveur_maj)-1:
                no_serveur = serveur + 1
                self.trouve_serveur_maj(notif, no_serveur)
            else:
                print "Aucun serveur disponible, mise à jour impossible"
                #no_serveur = 0
        socket.setdefaulttimeout(None)

    def verifi_fichier(self, fichier):
        '''Vérifi que le fichier téléchargé ne soit pas une erreur 404 ou 403, si c'est le cas, la fonction renvoi 1, sinon 0'''
        f = open(fichier, 'r')
        txt = f.read()
        f.close()
        if "404 Not Found" in txt or "403 Forbidden" in txt:
            return 1
        else:
            return 0

    def verif_maj_djl(self, notif=0, serveur=""):
        '''Vérifi si djl est à jour:
        (si notif=1, on affiche un message que si une MAJ est disponible)'''
        print ">", serveur
        #socket.setdefaulttimeout(3) #Temps de réponse avant d'annuler la mise à jour
        if serveur == "":
            serveur=self.serveur_maj[0]
        
        #if self.maj_ok == 0:
            #titre = i18n.traduc("Mise a jour de djl")
            #texte = i18n.traduc("Vous n'avez pas les doits suffisants pour ecrire dans le repertoire de djl. \n Il ne sera donc pas mis a jour.")
            #QtGui.QMessageBox.information(self, titre, texte)
            #self.action_maj.setEnabled(False)

        lien_maj = serveur + "/maj_djl/version_djl"
        if config(info=9) == "fr_FR":
            lien_changements = serveur+"/maj_djl/djl/Journal.txt"
        else:
            lien_changements = serveur+"/maj_djl/djl/Journal_en.txt"  
        fichier_maj = home + '/.djl/maj_djl.tmp'
        fichier_changements = home + '/.djl/changements.tmp'
        
        #Télécharge le fichier texte contenant la dernière version:
        try:
            urllib.urlretrieve(lien_maj, filename=fichier_maj, reporthook=None)
            urllib.urlretrieve(lien_changements, filename=fichier_changements, reporthook=None)
        except IOError:
            print "Impossible d'accéder au serveur"
            #Si le premier serveur ne répond pas, on essai avec le second serveur
            #(A condition que l'on utilise pas la version de développement)
            #if serveur == self.serveur_maj[0] and not "/dev" in serveur:
                #self.verif_maj_djl(notif, self.serveur_maj[1])
                #return
        #try:
        
        #Si on tombe sur une erreur 404 ou 403 dans le fichier de version, on annule la mise à jour.
        if self.verifi_fichier(fichier_maj) == 1:
            return
        
        if os.path.exists(fichier_maj) == True and os.path.exists(fichier_changements) == True:
            fichier = open(fichier_maj, 'r')
            nouvelle_version = fichier.read()
            fichier.close()
        
            f_changements = codecs.open(fichier_changements, 'r', 'utf-8')
            self.changements = f_changements.read()
    
            f_changements.close()
        else:
        
        #except:
            #Si le fichier n'a put être téléchargé et/ou le fichier temporaire notifiant la mise à jour n'existe pas
            #On part du principe que djl est à jour.
            nouvelle_version=interface.version()
            self.changements=""
            serveur=""
        
        version = interface.version()
        
        #print 'Version actuelle:', version
        #print 'Dernière version:', nouvelle_version
        ecrit_historique(i18n.traduc("Mise a jour de djl: ") + version + '>' + nouvelle_version)
        self.compare_maj(version, nouvelle_version, notif, serveur)
        #socket.setdefaulttimeout(None)

    def compare_maj(self, version, nouvelle_version, notif, serveur):
        '''Compare la version de djl actuelle et la dernière sur internet et dit si il faut ou non mettre à jour'''
        
        #Créé une boucle pour faire de la liste des changements une lignes de caractères avec sauts de lignes:
        changements = ""
        self.changements = self.changements.split('->', -1)
        self.changements_copie = self.changements
        boucle_ = 0
        if self.changements != '' or self.changements != '0':
            #Récupère ici la liste des changements sur le fichier texte (variable changements).
            while boucle_ < len(self.changements):
                #Si l'on atteind le numéro de version, on termine la boucle
                if version in self.changements[boucle_]:
                    
                    try:
                        changements = changements.replace('\n\n', '')
                    except: pass
                    
                    mesg = 1
                    break
                    
                #Sinon, continue de chercher dans la boucle.
                else:
                    #changements.append('\n \n' + self.changements_copie[boucle_])
                    
                    #Condition pour éviter d'afficher une liste de changements trop longue
                    #Variable qui défini le nombre maximum de versions à afficher dans l'historique des changements dans la boite de dialogue:
                    var_ch = 5 #(La dernière ligne sera "...", on affichera donc en réalité var_ch-1)
                    if boucle_ != var_ch:
                        changements = changements + '\n \n' + self.changements_copie[boucle_]
                    elif boucle_ == var_ch:
                        changements = changements + '\n \n' + '...'
                    mesg = 0
                boucle_=boucle_+1
        
        #Si on a toujours rien, on met l'historique de la dernière version:
        if mesg == 0:
            changements = "\n"+self.changements[1]
            try:
                changements = changements.replace('\n\n', '')
            except: pass
        
        envoi_maj = 0
        
        #Affiche un message qui dit si djl est à jour ou non:
        titre = i18n.traduc("Mise a jour de djl")
        
        #if mesg == 0:
            #txt_cg = ""
            #changements = ''
        #else:
        txt_cg = "\n" + i18n.traduc("Liste des nouveautes: ")

        #Si la variable qui contient le numéro de version sur internet n'est pas la même que la version actuelle, on affiche la boite de dialogue.
        if nouvelle_version != '0':
            if nouvelle_version != version:
                texte = i18n.traduc("Une mise a jour est disponible: ")
                reponse = QtGui.QMessageBox.information(self, titre, texte + str(version) + ' -> ' + str(nouvelle_version) + txt_cg + changements, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                
                if reponse == QtGui.QMessageBox.Ok:
                    self.affiche_maj(serveur, str(nouvelle_version))
                else:
                    return
    
            elif notif == 0:
                texte = i18n.traduc("djl est a jour: ")
                QtGui.QMessageBox.information(self, titre, texte + str(version))
        else: #Si sur le serveur la version est "0", on ne met pas à jour (état transitoire vers une future mise à jour))
            if notif == 0:
                texte = i18n.traduc("djl est a jour: ")
                QtGui.QMessageBox.information(self, titre, texte + str(version))
    
    def affiche_maj(self, serveur, id_archive):
        '''Envoi le téléchargement de la mise à jour avec le serveur qui va bien'''
        
        self.writeSettings() #Ecrit dans un fichier la taille et la position de la fenêtre principale.

        self.deco_irc() #On se deconnecte d'IRC
        self.hide() #Cache la fenêtre prendant la MAJ
        
        #Envoi l'affichage de la fenêtre
        Dialog = QtGui.QWidget(self)
        ui = Ui_Maj(Dialog, serveur, id_archive)
        ui.show()
    
    def redemarre(self):
        '''Redemarre djl'''
        self.writeSettings() #Ecrit dans un fichier la taille et la position de la fenêtre principale.
        
        self.deco_irc()
        
        th_redemarre = redemarre_djl()
        th_redemarre.start()
        time.sleep(0.3)
        self.quitte()

    def liste_raccourcis(self):
        '''Créé la liste des raccourcis depuis le répertoire ~/.djl/raccourcis (par defaut)'''
        liste_raccourcis = os.listdir(config(info=2) + '/raccourcis')
        liste_raccourcis.sort() #Tri la liste des raccourcis
        
        if int(config(info=3)) == 1 and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            id = 0
            try:
                nb_menu=self.nb_menu_mini
            except:
                nb_menu=0
            
        for i in range(len(liste_raccourcis)):
            #Si le nom du fichier contient '~', c'est que c'est un doublon qui a été modifié par un éditeur de texte, on ne l'affiche pas.
            if not '~' in liste_raccourcis[i]:
                item = QtGui.QListWidgetItem(self.listWidget)
                icone = str(self.lit_fichier_desktop(fichier=liste_raccourcis[i], type_info='Icon'))
                nom = str(self.lit_fichier_desktop(fichier=liste_raccourcis[i], type_info='Name'))
                item.setIcon(QtGui.QIcon(icone))
                item.setText(nom)
    
                #Ajoute le jeu dans la liste:
                self.liste_jeux_f.append(liste_raccourcis[i])
    
                #Si on a l'icone dans la boite à miniature, on y ajoute également la liste:
                if int(config(info=3)) == 1 and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
                    act=QtGui.QAction(self)
                    act.setIcon(QtGui.QIcon(icone))
                    act.setText((nom))
                    self.menu_lance.addAction(act)
                    
                    self.connect(act, QtCore.SIGNAL("triggered()"),self.Mapper, QtCore.SLOT("map()"))
                    self.Mapper.setMapping(act, self.nb_menu_mini+id)
                    id=id+1
                
    def import_desk(self):
        '''Fenetre d'importation des raccourcis .desktop'''
        #Dialog = QtGui.QWidget(self)
        destination = config(info=2) + '/raccourcis/'
        ui = import_raccourcis.Ui_Import_Raccourcis(self,  destination)
        ui.show()

        #Rafraichi la liste des jeux de l'interface principale
        self.maj_liste()

    def confirmation_menu_c_suppr(self):
        '''Fenetre de confirmation quand on demande de supprimer un jeu depuis la liste de jeux principale'''
        jeu_actuel = self.liste_jeux_f[self.listWidget.currentRow()].capitalize()
        titre = i18n.traduc("Confirmation")
        texte = i18n.traduc("Voulez vous vraiment supprimer le jeu") + " " + jeu_actuel + " ?"
        reponse = QtGui.QMessageBox.information(self, titre, texte, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                
        if reponse == QtGui.QMessageBox.Ok:
            self.menu_c_suppr()
        else:
            return

    def confirmation_suppr_desk(self):
        '''Fenetre de confirmation quand on demande de supprimer un raccourcis depuis la liste de jeux principale'''
        jeu_actuel = self.liste_jeux_f[self.listWidget.currentRow()]
        jeu_actuel = jeu_actuel.replace(".desktop",  "").capitalize()
        
        jeu_actuel = jeu_actuel.replace("_", " ")
        jeu_actuel = jeu_actuel.replace("-", " ")
        
        titre = i18n.traduc("Confirmation")
        texte = i18n.traduc("Voulez vous vraiment supprimer le raccourci") + " " + jeu_actuel + " ?"
        reponse = QtGui.QMessageBox.information(self, titre, texte, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                
        if reponse == QtGui.QMessageBox.Ok:
            self.suppr_desk()
        else:
            return

    def suppr_desk(self):
        '''Supprime le raccourcis sélectionné dans la liste de jeux principale (fichier .desktop)'''
        jeu_actuel = self.liste_jeux_f[self.listWidget.currentRow()]
        print jeu_actuel, _(' supprime')
        ecrit_historique(jeu_actuel + _(' supprime'))
        #Supprime le raccourci:
        supprime_fichier(config(info=2) + '/raccourcis/' + jeu_actuel)

        #Rafraichi la liste des jeux:
        self.maj_liste()
        
    def menu_c_suppr(self):
        '''Supression le jeu sélectionné depuis l'interface principale'''
        self.info()
        self.supprimer(menu_c=1)

    def ajout_jeu_(self):
        '''Envoi l'affichage de la fenêtre pour ajouter des jeux déjà installés sur le système (création de raccourcis)'''
        #Dialog = QtGui.QWidget(self)
        ui = ajout_jeu.Ui_ajout_jeu(self)
        ui.show()
        
    def modif_jeu_(self):
        '''Envoi l'affichage de la fenêtre pour modifier un raccourcis vers un jeu déjà installés sur le systeme'''
        #Dialog = QtGui.QWidget(self)
        fichier = self.liste_jeux_f[self.listWidget.currentRow()]
        nom = self.lit_fichier_desktop(fichier, "Name")
        icone = self.lit_fichier_desktop(fichier, "Icon")
        commande = self.lit_fichier_desktop(fichier, "Exec")
        
        repertoire = self.lit_fichier_desktop(fichier, "Path")
        if repertoire == None:
            repertoire = home
        elif repertoire == "":
            repertoire = home
            
        ui = ajout_jeu.Ui_ajout_jeu(self, fichier, nom, icone, commande, repertoire)
        ui.show()

    #def modif_jeu_depot(self):
        #import modif_depot
        #Dialog = QtGui.QWidget(self)
        #ui = modif_depot.Ui_modif_depot(Dialog)
        #ui.show()

    def lit_fichier_desktop(self, fichier, type_info='Name'):
        '''Fonction qui permet de lire les fichiers .desktop
        Elle récupère les informations suivantes: Name, Icon et Exec, 
        pour respectivement le nom, l'emplacement de l'icone et la commande pour lancer le jeu.'''
        
        nom_fichier = fichier
        fichier = open(config(info=2) + '/raccourcis/' + fichier, 'r')
        txt_raccourcis = fichier.readlines()

        #Parcours de la liste du fichier:
        boucle = 0
        while boucle < len(txt_raccourcis):
            #Si il y a l'information que l'on cherche dans le ligne en cours de lecture...
            if (type_info) in txt_raccourcis[boucle]:
                #Pour la recherche du nom du jeu, Ne prend pas en compte les lignes qui contiennent 'Generic', ainsi que celles qui contiennent [
                #Ce sont des fichiers .desktop générés par KDE ou autre, qui contiennent trop d'informations pour djl.
                if 'Generic' in txt_raccourcis[boucle] or '[' in txt_raccourcis[boucle] and type_info == 'Name':
                    pass
                else:
                    #Si l'adresse de, l'icone ne contient pas '/' le chemin n'est pas absolu et djl ne devrait donc pas le trouver
                    #On va donc tenter de le trouver:
                    if  type_info == 'Icon':
                        if '/' in txt_raccourcis[boucle]:
                            pass
                        else:
                            retour = txt_raccourcis[boucle]
                            retour = retour.replace(type_info + '=', '')
                            retour = retour.replace('\n', '')
                            
                            if self.djl_lance == 0:
                                ecrit_historique(_('icone introuvable:') + nom_fichier + i18n.traduc(", djl va tenter de la trouver, sinon elle sera remplacee."))

                            if retour == "":
                                ecrit_historique(i18n.traduc("L'icone du raccourcis") + nom_fichier + i18n.traduc(" n'a pas ete trouve, elle a ete remplace par l'icone de djl."))
                                retour = dossier_racine + '/icone.png'
                                return retour

                            #Tente de trouver l'icone avec différentes adresse et différents types de fichiers:
                            retour = import_raccourcis.trouve_ico(retour)
                            #On défini l'icone:
                            txt_raccourcis[boucle] = retour

                    #Si il y a des [] dans la ligne contenant la commande (typique à KDE), on les vires.
                    if type_info == 'Exec' and ']' in txt_raccourcis[boucle]:
                        retour = txt_raccourcis[boucle].split('=')[-1]
                        return retour
                        #On a trouvé l'information, on sort de la boucle
                        break
                    
                    if type_info == 'Exec' and 'TryExec' in txt_raccourcis[boucle]:
                        txt_raccourcis[boucle] = txt_raccourcis[boucle].replace('TryExec', 'Exec')
                    
                    if type_info == 'Path':
                        if '$HOME' in txt_raccourcis[boucle]:
                            txt_raccourcis[boucle] = txt_raccourcis[boucle].replace('$HOME', os.path.expanduser('~'))

                    #Dans les autres cas, on envoi l'information 'brute'
                    retour = txt_raccourcis[boucle]
                    retour = retour.replace(type_info + '=', '')
                    retour = retour.replace('\n', '')
                    
                    if ']=' in retour: #Si il reste un nom de variable, on l'enlève
                        retour = retour.split(']=')
                        retour = retour[len(retour)-1]
                        
                    return retour
            boucle = boucle+1
            
        if type_info == "Icon": #Si on a toujours rien trouvé:
            return dossier_racine + '/icone.png'
            
        fichier.close()

    def maj_liste(self):
        '''Fonction qui met à jour la liste des jeux principale à la volée'''
        #Remet la liste des jeux à 0:
        self.listWidget.clear()
        
        if int(config(info=3)) == 1 and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            self.menu_lance.clear()

        #Met à jour la liste des jeux installés:
        self.liste_jeux_installe()
        
        #Met à jour la liste des raccourcis
        self.liste_raccourcis()
        
        #Met à jour l'affichage du dépot (uniquement si on utilise l'interface étendue)
        #if variables.nom_jeu != '' and config(info=10) == "1":
        if  config(info=10) == "1" and self.connecte_ws == 1:
            self.etat(self.nom_jeu_depot())

    def infos_sys(self):
        '''Affiche les informations sur le système'''
        #print i18n.traduc_ascii("Informations systeme...")
        ecrit_historique(i18n.traduc("Informations systeme consultes"))

        texte_1 = i18n.traduc("Systeme d'exploitation: ") + (self.retour_commande(commande="uname -o", filtre1='', filtre2=''))
        
        texte_2 = i18n.traduc("Nom de la machine: ") + (self.retour_commande(commande="uname -n", filtre1='', filtre2=''))

        texte_3 = i18n.traduc("Architecture: ") + (self.retour_commande(commande="uname -m", filtre1='', filtre2=''))

        texte_4 = i18n.traduc("Environnement:  ") + (self.retour_commande(commande="echo $DESKTOP_SESSION", filtre1='', filtre2=''))

        texte_5 = i18n.traduc("Processeur: ") + (self.retour_commande(commande="cat /proc/cpuinfo", filtre1='model name', filtre2=':'))

        texte_6 = i18n.traduc("Fabricant de la carte graphique: ") + (self.retour_commande(commande="glxinfo", filtre1='OpenGL vendor string:', filtre2=''))

        texte_7 = i18n.traduc("Nom de la carte graphique: ") + (self.retour_commande(commande="glxinfo", filtre1='OpenGL renderer string:', filtre2=''))

        texte_8 = i18n.traduc("Version du pilote graphique: ") + (self.retour_commande(commande="glxinfo", filtre1='OpenGL version string:', filtre2=''))

        texte_9 = i18n.traduc("Memoire vive: ") + str(int(self.retour_commande(commande="cat /proc/meminfo", filtre1='MemTotal:', filtre2='kB'))/1024) + " " + _('Mo')+"\n"

        texte_10 = i18n.traduc("Carte son : ") + (self.retour_commande(commande="cat /proc/asound/card0/id", filtre1='', filtre2=''))

        texte_11 = i18n.traduc("Controle: ") + (self.trouve_joysticks())
        
        texte = texte_1 + texte_2 + texte_3 + texte_4 + texte_5+ \
        texte_6 + texte_7 + texte_8 + texte_9 + texte_10 + "<br />" + texte_11

        interface.info_box(texte, i18n.traduc("Informations systeme"))

    def trouve_joysticks(self):
        '''Repère dans /dev/input les manettes et souris pour les afficher dans les options système'''
        addr = '/dev/input/by-id'
        retour = "\n"
        if os.path.exists(addr) == True:
            liste = os.listdir(addr)
            for i in range(len(liste)):
                if not 'event' in liste[i]:
                    liste[i] = liste[i].replace("usb-",  "")
                    liste[i] = liste[i].replace("_",  " ")
                    if "joystick" in liste[i]:
                        liste[i] = liste[i].replace("-joystick",  "")
                        retour = retour + liste[i] + "\n"
                    elif "mouse" in liste[i]:
                        liste[i] = liste[i].replace("-mouse",  "")
                        retour = retour + liste[i] + "\n"
        else:
            return "0"
        return retour

    def affiche_historique(self):
        '''Affiche l'historique des modifcations de djl'''
        if config(info=9) == "fr_FR":
            fichier = os.getcwd() + '/Journal.txt'
        else:
            fichier = os.getcwd() + '/Journal_en.txt'
        self.affiche_fichier(fichier)
    
    def affiche_journal(self):
        '''Fonction pour ouvrir une boite de dialogue avec les messages de sortie de djl:'''
        self.affiche_fichier(home + '/.djl/djl_log.txt')
            
    def affiche_license(self):
        '''Affiche la licence de djl dans une fenêtre'''
        self.affiche_fichier("../COPYING")
    
    def affiche_sortie_jeu(self):
        '''Fonction pour ouvrir une boite de dialogue avec les messages de sortie des jeux'''
        self.affiche_fichier(home + '/.djl/debog', 1)

    def affiche_fichier(self, fichier, type=0):
        '''Ouvre un fichier texte donné et l'affiche dans une boite de dialogue avec liste déroulante et bouton de fermeture
        Si type = 1, la fenêtre vérifira périodiquement si le fichier est modifié, pour mettre à jour l'affichage, utilisé pour
        Consulter la sortie des jeux'''
        #variables.fichier_texte = fichier
        if variables.journal == 0: #Ouvre la fenêtre uniquement si elle n'est pas déjà ouverte:
            Dialog = QtGui.QWidget(self)
            ui = Ui_Journal(fichier, type, Dialog)
            ui.show()
            variables.journal = 1
            
    def rapport(self):
        '''Envoi un rapport de bogue sur le forum de djl avec un navigateur'''
        #self.lance_navigateur("http://forum.jeuxlinux.fr/viewforum.php?id=26") #Forum jeuxlinux.fr
        if self.lang == 1: #Si on utilise la langue Française:
            self.lance_navigateur("http://www.forum.djl-linux.org/viewforum.php?f=12", 1)
        else:
            #Sinon:
            self.lance_navigateur("http://www.forum.djl-linux.org/viewforum.php?f=9", 1)

    def a_propos(self):
        '''"Boite de dialogue à propos de djl..."'''
        texte_1 = i18n.traduc("Depot jeux linux ") + interface.version() + i18n.traduc(" par Diablo150 sous licence GPL 3.")
        texte_2 = i18n.traduc("Merci aux principaux contributeurs:")
        texte_3 = i18n.traduc("Mes deux freres.")
        texte_4 = i18n.traduc("Lululaglue, Jerhum, Julroy67 et sebastienb de jeuxlinux.fr.")
        texte_5 = "<br />" + i18n.traduc("Ainsi qu'a:")
        
        texte_6 = "- Chain\n- Yoann512\n- Maximee\n"+\
        "<br />"+\
        i18n.traduc("Traducteurs:") + "<br />" + \
        "- Sirio81 " + i18n.traduc("(English)") + "<br />" + \
        "- Sindwiller " + i18n.traduc("(Deutsch)") + "<br />" + \
        "- Chain " + i18n.traduc("(Русский)") + "<br />" + \
        "- David Ballesteros Mayo " + i18n.traduc("(Español)") + "<br />" + \
        "- Vinnie, Stormcrow, Mte90 " + i18n.traduc("(Italiano)") + "<br />" + \
        "- Nevon " + i18n.traduc("(Svenska)") + "<br />" + \
        "- napcok " + i18n.traduc("(Polski)" + "<br />" \
        "- Carlos Pais " + i18n.traduc("(Portugues)") + "<br />" + \
        "- Charles Barcza (www.blackPanther.hu) " + i18n.traduc("(Hungarian)") + "<br />")
        
        texte = texte_1 + "<br />" + texte_2 + "<br />" + texte_3 + "<br />" + texte_4 + "<br />" + texte_5 + "<br />" + texte_6
        interface.info_box(texte, i18n.traduc("A propos de djl"))

    def retour_commande(self, commande='', filtre1='', filtre2=''):
        '''Lance une commande données et renvoi le résultat  en y appliquant des filtres (utilisé pour récupérer les informations système)'''
        #Lance le programme
        c = os.popen(commande)
        #Récupère la sortie du terminal:
        retour = c.readlines()
        c.close()
        
        chaine = ""
        boucle = 0
        #Boucle pour parcourir la liste qui contient la sortie du programme:
        while boucle < len(retour):
            #Fais le tri dans la liste afin de ne récupérer que ce qui contient filtre 1 et filtre 2
            if filtre1 in retour[boucle]:
                #Supprime les espaces inutiles (cat /proc/cuinfo en affiche trop):
                if '   ' in retour[boucle]:
                    retour[boucle] = retour[boucle].replace('    ', ' ')
                if filtre2 in retour[boucle]:
                    retour[boucle] = retour[boucle].replace(filtre1, '')
                    retour[boucle] = retour[boucle].replace(filtre2, '')
                    chaine = retour[boucle]
                    break
                else:
                    retour[boucle] = retour[boucle].replace(filtre1, '')
                    chaine = retour[boucle]
                    break
            boucle=boucle+1
            
        #Si on trouve rien, on l'indique en retournant un truc bidon
        if chaine == "" or chaine == "\n":
            chaine = i18n.traduc("Non trouve") + "\n"
        return chaine
            
    def langue_fr(self):
        '''Lorsque l'on choisi la langue Française dans le menu...'''
        self.modif_langue(langue='fr_FR')

    def langue_en(self):
        '''Lorsque l'on choisi la langue Anglaise dans le menu...'''
        self.modif_langue(langue='en_US')

    def langue_hu(self):
        '''Lorsque l'on choisi la langue Hungarian dans le menu...'''
        self.modif_langue(langue='hu_HU')
        
    def langue_gl(self):
        '''Lorsque l'on choisi le Galicien dans le menu...'''
        self.modif_langue(langue='gl_ES')
        
    def langue_ru(self):
        '''Lorsque l'on choisi la langue Russe dans le menu...'''
        self.modif_langue(langue='ru_RU')
        
    def langue_sv(self):
        '''Lorsque l'on choisi la langue Suédoise dans le menu...'''
        self.modif_langue(langue='sv_SE')
        
    def langue_it(self):
        '''Lorsque l'on choisi la langue Italienne dans le menu...'''
        self.modif_langue(langue='it_IT')
        
    def langue_es(self):
        '''Lorsque l'on choisi la langue Espagnole dans le menu...'''
        self.modif_langue(langue='es_ES')
        
    def langue_de(self):
        '''Lorsque l'on choisi la langue Allemande dans le menu...'''
        self.modif_langue(langue='de_DE')
        
    def langue_pl(self):
        '''Lorsque l'on choisi la langue Polonaise dans le menu...'''
        self.modif_langue(langue='pl_PL')
        
    def langue_pt(self):
        '''Lorsque l'on choisi la langue Polonaise dans le menu...'''
        self.modif_langue(langue='pt_PT')

    def modif_langue(self, langue):
        '''Modifi dans le fichier de configuration pour la lange donnée en paramètre.'''
        self.cree_reps()
        
        #Change la configuration:
        fichier = open(home + '/.djl/config', 'r')
        fichier_cfg = fichier.readlines()
        fichier.close()
        
        #Si la ligne dans la configuration existe déjà, on la remplace:
        try:
            fichier_cfg[9] = ('langue = ' + str(langue)+'\n')
        except:
        #Sinon on la créé
            fichier_cfg.append('\nlangue = ' + str(langue)+'\n')
        
        #Bouble pour écrire dans le fichier de configuration:
        fichier = open(home + '/.djl/config', 'w')
        boucle = 0
        while boucle < len(fichier_cfg):
            fichier.write(fichier_cfg[boucle])
            boucle = boucle + 1
        fichier.close()

        #Redémarre djl pour appliquer les changements:
        #self.redemarre()
        self.envoi_traduc()
        
    def envoi_traduc(self):
        '''Lance/renouvelle la traduction du logiciel'''
        self.lang = config(info=9, sec=1)
        import i18n
        i18n.i18n_init()
        self.retranslateUi(self) #Traduction de l'interface
        self.maj_liste() #Recharge la liste des jeux
        self.init_IRC() #Recharge le client IRC
        self.traducsDepot() #Recharge les traductions du dépôt.
        self.maj_depot() #Recharge le dépôt (y compri la liste des types de jeux)
        self.maj_RSS() #Recharche les flux RSS.

    def readSettings(self):
        '''Au démarrage, charge la position et la taille de la fenêtre, sauvegardé au dernier lancement de djl'''
        settings = QtCore.QSettings("Djl", "djl")
        pos = settings.value("pos", QtCore.QVariant(QtCore.QPoint(200, 200))).toPoint()
        size = settings.value("size", QtCore.QVariant(QtCore.QSize(279, 585))).toSize()
        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        '''Sauvegarde la taille et la position de la fenêtre.'''
        settings = QtCore.QSettings("Djl", "djl")
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        #if config(info=10) == '0':
            #settings.setValue("size", QtCore.QVariant(self.size()))
        settings.setValue("size", QtCore.QVariant(self.size()))
        
    def fenetre_dependances(self):
        '''Affiche la fenêtre de gestion des dépendances'''
        #Dialog = QtGui.QWidget(self)
        try:
            if variables.affiche_f_depends:
                return
        except AttributeError: 
            variables.affiche_f_depends = True
        variables.affiche_f_depends = True
        #titre = 'Installer une librairie manquante'
        titre = "Gestionnaire des librairies"
        ui = Ui_Telecharge_Lib(self, titre=titre)
        ui.show()
        
        #########################################
        
class Ui_Telecharge_Lib(QtGui.QWidget):
    '''Fenêtre pour permettre la gestion des dépendances (librairies partagés)'''
    def __init__(self, parent=None, serveur='', repertoire='', titre = ''):
        QtGui.QWidget.__init__(self, parent)
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        self.gestionnaire = gdep.GestionLibs()
        self.repertoire = self.gestionnaire.Repertoire()
        
        #Créé les variables:
        #self.repertoire = home + "/.djl/" + repertoire  #Répertoire d'installation des librairies
        #self.f_liste = self.repertoire + "/liste" #Fichier contenant la liste des librairies
        #self.serveur = serveur + "/maj_djl/" + repertoire #Serveur pour télécharger les librairies
        self.verif_en_dur = False #Vérifi ou non si les librairies n'existent pas dejà dans /usr/lib
        
        self.titre = titre #Titre de la fenêtre
            
        self.liste = [] #Liste des fichiers, sera rempli en fonction des éléments de la QlistWidget

        self.setupUi(self)
        
        self.vliste = False #Quand la variable passe à True, on affiche la liste des librairies.
        self.timer = QtCore.QBasicTimer()
        self.timer.start(100, self)
        
        socket.setdefaulttimeout(3)
        try:
            th = threading.Thread(target=self.creer_liste)
            th.start()
            #self.creer_liste()
        except IOError, x:
            print titre, serveur, str(x)
        socket.setdefaulttimeout(None)
        
    def timerEvent(self, event):
        if self.vliste:
            self.affiche_liste()
            self.timer.stop()
            
    def affiche_liste(self):
        '''Affiche la liste des librairies'''
        liste = self.liste_f
        liste.sort() #Tri la listes
            
        for i in range(len(liste)):
            #liste[i] = liste[i].replace('\n', '')
            #N'affiche que les librairies qui n'existent pas sur le système:
            if not os.path.exists("/usr/lib/" + liste[i]) or not self.verif_en_dur:
                #Si c'est la fenêtre des dependances, les fichiers et la description sont les mêmes
                fichier = texte = liste[i]
                    
                if os.path.exists(self.repertoire + "/" + fichier):
                    icone = QtGui.QIcon(dossier_racine + '/res/retirer.png')
                else:
                    icone = QtGui.QIcon(dossier_racine + '/res/ajouter.png')
                self.liste.append(fichier)
                item = QtGui.QListWidgetItem(self.listWidget)
                if fichier != 'titre': #Si le nom de fichier est 'titre', on ne met pas l'icone
                    item.setIcon(QtGui.QIcon(icone))
                item.setText(texte)
                self.listWidget.addItem(item)
        
        #print len(self.liste) #Nombre d'éléments sur le serveur

    def creer_liste(self):
        '''Créé la liste des librairies pouvant être téléchargés depuis les informations du serveur.'''
        self.liste_f = self.gestionnaire.Rliste()
        self.vliste = True #La liste sera affichée, dans le Thread principal.

    def recherche(self):
        '''Quand on tape du texte dans la barre de recherche, on cherche le texte (!) dans la liste'''
        txt = unicode((self.Wrecherche.text())).encode('utf-8').lower()
        for id in range(len(self.liste)):
            if txt in self.liste[id].lower():
                self.listWidget.setCurrentRow(id)
                #print self.liste[id].lower()
                return
        self.listWidget.setCurrentRow(0)
    
    def installe_supprime(self):
        '''Télécharge et copie la librairie si elle n'existe pas, sinon on la supprime'''
        fichier = self.liste[self.listWidget.currentRow()]
        if fichier != 'titre':
            #Si la librairie existe, on la supprime
            if os.path.exists(self.repertoire + "/" + fichier):
                #print "Supprime: ", fichier
                os.remove(self.repertoire + "/" + fichier)
                
                #Change l'icone dans la liste pour montrer qu'elle pourra maintenant être installé
                icone = QtGui.QIcon(dossier_racine + '/res/ajouter.png')
                self.pushButton.setText(i18n.traduc("Installer"))
    
            #Si elle n'existe pas, on la télécharge
            else:
                #print "Installe: ", fichier
                self.gestionnaire.Telecharge(fichier)
                #urllib.urlretrieve(self.gestionnaire.Lien(fichier), self.repertoire + "/" + fichier, reporthook=False)
                
                #Change l'icone dans la liste pour montrer qu'elle pourra maintenant être supprimée
                icone = QtGui.QIcon(dossier_racine + '/res/retirer.png')
                self.pushButton.setText(i18n.traduc("Supprimer"))
                
            #On change l'icone en fonction que le fichier ait été installé ou supprimé:
            id = self.liste.index(fichier)
            self.listWidget.item(id).setIcon(icone)
        
    def closeEvent(self, Event):
        '''A la fermeture de la fenêtre...'''
        variables.affiche_f_depends = False

    def maj_bouton(self):
        '''Met à jour le texte du bouton pour afficher "Installer" ou "Supprimer" suivant si la librairie séléctionné exste sur le disque ou pas'''
        if os.path.exists(self.repertoire + "/" + self.liste[self.listWidget.currentRow()]):
            self.pushButton.setText(i18n.traduc("Supprimer"))
        else:
            self.pushButton.setText(i18n.traduc("Installer"))
    
    def echappement(self):
        '''Ferme la fenêtre'''
        self.close()
        
    def setupUi(self, Form):
        '''Dessin de l'interface de gestion des dépendances'''
        Form.setObjectName("Form")
        x, y = 300, 500
        Form.resize(x, y)
        
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        
        #Place de fenêtre au centre de la fenêtre principale
        posx = self.parent.pos().x() + self.parent.width()/2
        posy = self.parent.pos().y() + self.parent.height()/2
        self.move(posx-(x/2), posy-(y/2))
        #/

        self.Wrecherche = QtGui.QLineEdit(self)
        self.verticalLayout.addWidget(self.Wrecherche)
        
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setObjectName("listWidget")

        self.verticalLayout.addWidget(self.listWidget)
        self.pushButton = QtGui.QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        icone = QtGui.QIcon(dossier_racine + '/res/configuration.png')
        Form.setWindowIcon(icone)

        self.retranslateUi(Form)
        self.connexions()
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        '''Affichage du texte'''
        Form.setWindowTitle(_(self.titre))
        self.pushButton.setText(i18n.traduc("Installer"))
        #self.label.setText(i18n.traduc("Attention)

    def connexions(self):
        '''Connexion des objets Qt aux fonctions et raccourcis'''
        self.pushButton.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.installe_supprime)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.maj_bouton)
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.installe_supprime)
        self.Wrecherche.connect(self.Wrecherche, QtCore.SIGNAL("textEdited(const QString &)"), self.recherche)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.echappement)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self, self.installe_supprime)

class Ui_Maj(QtGui.QWidget):
    def __init__(self, parent=None, serveur="", id_archive=""):
        '''Initialisation de la fenêtre de mise à jour de djl
        serveur = serveur utilisé pour la mise à jour'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.pushButton.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.b_ok)
        print serveur
        #print variables.version_dev
        self.maj(serveur, id_archive)

    def b_ok(self):
        '''Quand on clique sur 'ok'...'''
        #self.hide()
        self.close()

    def maj(self, serveur, id_archive):
        '''Envoi la mise à jour dans un thread séparé'''
        self.timer = QtCore.QBasicTimer()
        self.timer.start(10, self)

        self.th_maj = th_telechargement_maj(serveur, id_archive)
        self.th_maj.start()

    def timerEvent(self, event):
        '''Boucle pour rafraichir la fenêtre de mise à jour.'''
        
        #Rafraichi l'affichage de la barre de progression
        self.progressBar.setProperty("value",QtCore.QVariant(variables_maj.pourcentage))

        #Quand le téléchargement est terminé...
        if int(variables_maj.pourcentage) >= 100:
            #Stop le timer du rafraichissement:
            self.timer.stop()
            #Ferme la fenêtre:
            self.close()

            #On décompresse l'archive:
            archive = tarfile.open(home + '/.djl/archive_maj.tmp','r:gz')
            #print variables.type_maj
            if variables.type_maj == 0: #Si on a les droits dans le répertoire de djl, on y décompresse le programme
                archive.extractall(os.getcwd()+"/../../")
            else: #Sinon dans le répertoire personnel
                if os.path.exists(home+"/.djl/src/")==False:
                    os.mkdir(home+"/.djl/src/")
                archive.extractall(home+"/.djl/src/")
            archive.close()

            #La mise à jour est terminée, on redémarre djl:
            th_redemarre = redemarre_djl()
            th_redemarre.start()
            time.sleep(0.5)
            sys.exit()
            
    def setupUi(self, Form):
        '''Dessin de l'interface de la fenêtre de mise à jour'''
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,281,77).size()).expandedTo(Form.minimumSizeHint()))

        Form.setMinimumSize(QtCore.QSize(281,77))
        Form.setMaximumSize(QtCore.QSize(281,77))

        icone = QtGui.QIcon((os.getcwd() + '/icone.png'))
        Form.setWindowIcon(icone)

        self.pushButton = QtGui.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(95,50,91,27))
        self.pushButton.setObjectName("pushButton")

        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(0,0,181,21))
        self.label.setObjectName("label")

        self.progressBar = QtGui.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(0,20,281,23))
        self.progressBar.setProperty("value",QtCore.QVariant(0))
        self.progressBar.setObjectName("progressBar")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        '''Affiche le texte de l'interface de la fenêtre de mise à jour'''
        Form.setWindowTitle(i18n.traduc("Mise a jour de djl"))
        self.pushButton.setText(i18n.traduc("Ok"))
        self.label.setText(i18n.traduc("Mise a jour en cours..."))

class th_telechargement_maj(threading.Thread):
    '''Téléchargement des fichiers lors de la mise à jour dans un thread séparé de l'interface Ui_Maj'''
    def __init__(self,serveur, id_archive):
        threading.Thread.__init__(self)
        self.serveur=serveur
        self.id_archive=id_archive

    def run(self):
        '''Appelé lors de l'__init__() du Thread'''
        socket.setdefaulttimeout(None)
        print i18n.traduc_ascii("Mise a jours en cours...")
        archive = self.serveur + "/maj_djl/archives/djl-" + self.id_archive + ".tar.gz"
        print archive
        
        urllib.urlretrieve(archive, filename=home + '/.djl/archive_maj.tmp', reporthook=self.reporthook)
        
    def reporthook(self, nb_blocs, taille_bloc, taille_fichier):
        '''Calcul de l'avancement du téléchargement: (en %)
        La fonction est appelé par urllib.urlretrieve à chaque fois qu'un bloc est téléchargé'''
        variables_maj.pourcentage = int((((nb_blocs+0.)*(taille_bloc+0.))/taille_fichier+0.)*100+0.)

#Variables publiques pour le téléchargement des mises à jours:
class variables_maj:
    pourcentage = 0

class Ui_Journal(QtGui.QWidget):
    def __init__(self, fichier, type_, parent=None,):
        '''Fenêtre pour afficher le fichier donné en argument'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)
        self.type_ = type_
    
        self.fichier = fichier
        self.setupUi(self)
        
        self.font = QtGui.QFont()
        self.font.setPointSize(config(info=15))
        self.setFont(self.font)
        
        self.affiche_texte()
        
        self.pushButton.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.close)
        #self.textEdit.connect(self.textEdit, QtCore.SIGNAL("textChanged()"), self.rafraichi)

        print '>>>', str(type_), self.fichier
        if type_ == 1: #Si le texte doit être rafraichi périodiquement...
            self.taille_ancienne = 0
            self.timer = QtCore.QBasicTimer()
            self.timer.start(1000, self) #Temps de rafraichissement

        #Raccourcis clavier
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.close)

    def rafraichi(self):
        '''Défile le texte vers le bas'''
        val = int(self.textEdit.verticalScrollBar().maximum())
        self.textEdit.verticalScrollBar().setValue(val)

    def timerEvent(self, event):
        '''Timer pour rafraichir la fenêtre si la taille du fichier a changée (uniquement si il s'agit du fichier dédié au déboguage)'''
        taille = os.stat(self.fichier)[6]
        if taille != self.taille_ancienne:
            self.affiche_texte()
            self.taille_ancienne = taille
            self.rafraichi()

    def affiche_texte(self):
        '''Envoi l'affichaque du texte dans la boite self.textEdit'''
        if os.path.exists(self.fichier) == True:
            fichier = codecs.open(self.fichier, 'r', 'utf-8')
            try:
                txt_fichier = fichier.read()
            except UnicodeDecodeError:
                txt_fichier = ""
                #for l in fichier:
                    #print l
                    #txt_fichier = txt_fichier + l

            self.textEdit.setText(txt_fichier)
            fichier.close()
        
        else:
            print i18n.traduc_ascii("Le fichier n'existe pas")
    
    def closeEvent(self, event):
        '''Lorsque l'on demande de fermer la fenêtre'''
        if self.type_ == 1:
            self.timer.stop()
        variables.journal = 0

    def setupUi(self, Form):
        '''Envoi le dessin de l'interface'''
        self.setObjectName("Form")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,800,600).size()).expandedTo(Form.minimumSizeHint()))
        
        icone = QtGui.QIcon((dossier_racine + '/icone.png'))
        self.setWindowIcon(icone)

        self.textEdit = QtGui.QTextEdit(Form)
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setAcceptRichText(False)

        self.pushButton = QtGui.QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        
        ###
        self.gridlayout = QtGui.QGridLayout(self)
        self.gridlayout.setObjectName("gridlayout")
        
        self.gridlayout_2 = QtGui.QVBoxLayout()
        self.gridlayout_2.setObjectName("gridlayout_2")
        self.gridlayout.addLayout(self.gridlayout_2, 0, 0)
        
        self.gridlayout_2.addWidget(self.textEdit, 0)
        self.gridlayout_2.addWidget(self.pushButton, 1)
        ###

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        #Form.setCentralWidget(self.textEdit)

    def retranslateUi(self, Form):
        '''Affiche le texte de l'interface'''
        Form.setWindowTitle(i18n.traduc("Fichier: ") + self.fichier)
        self.pushButton.setText(i18n.traduc("Fermer"))

class redemarre_djl(threading.Thread):
    def __init__(self):
        '''initalisation, démarre un nouveau processus djl, le Thread principale quittera djl quelques instants après'''
        threading.Thread.__init__(self)

    def run(self):
        '''Lance djl.py avec argument -r pour "dire" qu'on redemarre'''
        #Ecrit dans le journal de djl que nous avons redémarré le logiciel:
        print _('djl redemarre')
        ecrit_historique(_('djl redemarre'))
        
        fichier = 'djl.py'

        if variables.version_dev == 1:
            fichier=fichier + " -dev"

        if os.path.exists("/usr/bin/python2.6") == True:
            commande_python = "python2.6"
        elif os.path.exists("/usr/bin/python2.5") == True:
            commande_python = "python2.5"
        else:
            commande_python = "python"

        #Si le code source est dans le répetoire personnel, on le lance dedans:
        if os.path.exists(home + '/.djl/src/djl/' + fichier.replace(" -dev", "")) == True:
            os.popen(commande_python + ' ' + home + '/.djl/src/djl/' + fichier  + " -r")
        #Sinon on prend le répertoire d'installation de djl:
        else:
            os.popen(commande_python + ' ' + fichier + " -r")
    
def ecrit_historique(texte):
    '''Fonction pour écrire dans le fichier d'historique'''
    #Chaine contenant l'heure et la date:
    t_ = time.localtime()
    secondes = t_[5]
    if secondes < 10:
        secondes = '0' + str(t_[5])
    
    t = str(t_[3]) + ':' + str(t_[4]) + ':' + str(secondes) + ' le ' + str(t_[2]) + '/' + str(t_[1]) + '/' + str(t_[0]) 

    fichier_log = open(home + '/.djl/djl_log.txt', 'a+')
    fichier_log.write('>>> ' + t + ': ' + texte +  '\n')
    fichier_log.close()

def supprime_fichier(fichier):
    '''Supprime le fichier donné (normalement temporaire) en ignorant les exceptions'''
    try:
        os.remove(fichier)
    except: 
        pass

def nettoyage(n=0):
    '''Supprime les fichiers temporaires à la fin du programme'''
    if n == 1:
        supprime_fichier(home + '/.djl/maj_djl.tmp')
        supprime_fichier(home + '/.djl/changements.tmp')
        supprime_fichier(home + '/.djl/archive_maj.tmp')
        supprime_fichier(home + '/.djl/liste_jeux.tmp')
        supprime_fichier(home + '/.djl/fichiers_djl.tmp')

        #supprime_fichier(home + '/.djl/debog')
        
        #os.system("echo ''")
        sys.exit()

class MessageLancement(QtGui.QWidget):
    def __init__(self, chrono, parent=None):
        '''Fenetre appelée pour signaler le lancement d'un jeu, elle se ferme automatiquement au bout de quelques secondes'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)
        self.chrono = chrono*1000
        self.parent = parent
        self.setupUi(self)
        
    def timerEvent(self, event):
        self.timer.stop()
        self.close()
    
    def setupUi(self, fen):
        x, y = 400, 41
        self.setObjectName("MessageLancement")
        
        self.resize(QtCore.QSize(QtCore.QRect(0, 0,x,y).size()).expandedTo(self.minimumSizeHint()))
        
        #Place de fenêtre au centre de la fenêtre principale
        posx = self.parent.pos().x() + self.parent.width()/2
        posy = self.parent.pos().y() + self.parent.height()/2
        self.move(posx-(x/2), posy-(y/2))
        #/

        self.setMinimumSize(QtCore.QSize(x,y))
        self.setMaximumSize(QtCore.QSize(x,y))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        icone = QtGui.QIcon(dossier_racine + '/res/jeux_oxygen.png')
        self.setWindowIcon(icone)

        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(5,5,x-10,y-10))
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setObjectName("label")
        
        self.timer = QtCore.QBasicTimer()
        self.timer.start(self.chrono, self)
        
        self.label.setText(i18n.traduc("Le jeu est en cours de lancement")+'...')
        self.setWindowTitle("djl")

class Ui_Wine(QtGui.QWidget):
    def __init__(self, parent=None):
        '''Fenetre appelée pour créer des raccourcis vers des jeux Windows lancés avec Wine'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)
        self.setupUi(self, parent)
        
        self.font = QtGui.QFont()
        self.font.setPointSize(config(info=15))
        self.setFont(self.font)
        
        self.wine_buttonBox.connect(self.wine_buttonBox, QtCore.SIGNAL("accepted()"), self.bouton_ok)
        self.wine_buttonBox.connect(self.wine_buttonBox, QtCore.SIGNAL("rejected()"), self.bouton_annul)
        
        self.wine_parcouir_icone.connect(self.wine_parcouir_icone, QtCore.SIGNAL("clicked()"), self.parcours_icone)
        self.wine_parcouir_exe.connect(self.wine_parcouir_exe, QtCore.SIGNAL("clicked()"), self.parcours_exe)

        #Raccourcis clavier
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.close)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self, self.bouton_ok)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter), self, self.bouton_ok)

    def parcours_icone(self):
        '''Affiche la fenêtre de parcours de l'icone'''
        commande = QtGui.QFileDialog.getOpenFileName(self, "", home + '/.wine/icons')
        self.wine_chemin_icone.setText(commande)
        
    def parcours_exe(self):
        '''Affiche la fenêtre de parcours de l'executable'''
        #commande = QtGui.QFileDialog.getOpenFileName(self)
        commande = QtGui.QFileDialog.getOpenFileName(self, "", home + '/.wine/drive_c' '', i18n.traduc("Win32 exe (*.exe)"))
        
        #Si l'utilisateur n'a pas défini de nom, en le trouve en fonction du nom du .exe
        if self.wine_nom_jeu.text() == '':
            nom = commande.split('/')
            nom = nom[len(nom)-1]
            nom = nom.split('.')
            nom = nom[0]
            self.wine_nom_jeu.setText(nom)
            
        self.wine_chemin_exe.setText(commande)

    def bouton_ok(self):
        '''On sauvegarde...'''
        if self.wine_nom_jeu.text() == '' or self.wine_chemin_exe.text() == '':
            interface.info_box(i18n.traduc("Vous devez definir le chemin vers un fichier .exe ainsi que le nom du jeu."))
        else:
            #Enregistre les données dans un fichier .desktop standard:
            fichier = open(config(info=2) + '/raccourcis/' + str(self.wine_nom_jeu.text()).lower() + '.desktop', 'w')
            
            #Récupère le chemin vers l'executable:
            executable = self.wine_chemin_exe.text()
            #Récupère le répertoire dans lequel le .exe est placé:
            rep_temp = executable.split('/')
            repertoire = self.wine_chemin_exe.text()
            repertoire = repertoire.replace(rep_temp[len(rep_temp)-1], '')
            
            #Formatage de chaine pour utilise Wineprefix (si le .exe est placé dans ~/.wine ou un sous rpéertoire:
            if '.wine' in executable:
                chemin_win = executable.replace(str(home + '/.wine/drive_c/'), "C:\\\\")
                chemin_win = chemin_win.replace("/", "\\\\")
                executable = 'env WINEPREFIX="' + home + '/.wine"' + ' wine "' + chemin_win + '"'
            
            fichier.write('[Desktop Entry]' + '\n')
            fichier.write('Name=' + str(self.wine_nom_jeu.text()).capitalize() + '\n')
            fichier.write('Icon=' + self.wine_chemin_icone.text() + '\n')
            fichier.write('Exec=' + executable + '\n')
            fichier.write('Path=' + repertoire + '\n')
            fichier.write('Type=Application')
            fichier.close()
            #Demande le rafraichissement de l'interface principale:
            variables.maj_listejeux = True
            #Ferme la fenêtre:
            self.close()

    def bouton_annul(self):
        '''Si on annule, on ferme la fenetre'''
        self.close()
        
    def setupUi(self, Wine, parent):
        '''Envoi le dessin de l'interface'''
        x, y = 470, 175
        Wine.setObjectName("Wine")
        Wine.resize(QtCore.QSize(QtCore.QRect(0,0,x,y).size()).expandedTo(Wine.minimumSizeHint()))
        
        #Place de fenêtre au centre de la fenêtre principale
        posx = parent.pos().x() + parent.width()/2
        posy = parent.pos().y() + parent.height()/2
        self.move(posx-(x/2), posy-(y/2))
        #/
        
        Wine.setMinimumSize(QtCore.QSize(x,y))
        Wine.setMaximumSize(QtCore.QSize(x,y))

        icone = QtGui.QIcon(dossier_racine + '/res/winehq.png')
        Wine.setWindowIcon(icone)

        self.wine_label = QtGui.QLabel(Wine)
        self.wine_label.setGeometry(QtCore.QRect(10,10,460,31))
        self.wine_label.setTextFormat(QtCore.Qt.PlainText)
        self.wine_label.setObjectName("wine_label")

        self.wine_label_2 = QtGui.QLabel(Wine)
        self.wine_label_2.setGeometry(QtCore.QRect(10,45,71,31))
        self.wine_label_2.setObjectName("wine_label_2")

        self.wine_nom_jeu = QtGui.QLineEdit(Wine)
        self.wine_nom_jeu.setGeometry(QtCore.QRect(160,50,191,22))
        self.wine_nom_jeu.setObjectName("wine_nom_jeu")

        self.wine_label_3 = QtGui.QLabel(Wine)
        self.wine_label_3.setGeometry(QtCore.QRect(10,110,151,21))
        self.wine_label_3.setObjectName("wine_label_3")

        self.wine_chemin_exe = QtGui.QLineEdit(Wine)
        self.wine_chemin_exe.setGeometry(QtCore.QRect(160,110,191,22))
        self.wine_chemin_exe.setObjectName("wine_chemin_exe")

        self.wine_buttonBox = QtGui.QDialogButtonBox(Wine)
        self.wine_buttonBox.setGeometry(QtCore.QRect(150,140,161,31))
        self.wine_buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.wine_buttonBox.setObjectName("wine_buttonBox")

        self.wine_parcouir_exe = QtGui.QPushButton(Wine)
        self.wine_parcouir_exe.setGeometry(QtCore.QRect(360,110,101,21))
        self.wine_parcouir_exe.setObjectName("wine_parcouir_exe")

        self.wine_label_4 = QtGui.QLabel(Wine)
        self.wine_label_4.setGeometry(QtCore.QRect(10,80,91,21))
        self.wine_label_4.setObjectName("wine_label_4")

        self.wine_chemin_icone = QtGui.QLineEdit(Wine)
        self.wine_chemin_icone.setGeometry(QtCore.QRect(160,80,191,22))
        self.wine_chemin_icone.setObjectName("wine_chemin_icone")

        self.wine_parcouir_icone = QtGui.QPushButton(Wine)
        self.wine_parcouir_icone.setGeometry(QtCore.QRect(360,80,101,21))
        self.wine_parcouir_icone.setObjectName("wine_parcouir_icone")

        self.retranslateUi(Wine)
        QtCore.QMetaObject.connectSlotsByName(Wine)

    def retranslateUi(self, Wine):
        '''Envoi l'affichage du texte de l'inteface'''
        Wine.setWindowTitle("Wine")
        self.wine_label.setText(i18n.traduc("Attention: La stabilitee et les performances du jeu ne sont pas\nassures"))
        self.wine_label_2.setText(i18n.traduc("Nom du jeu:"))
        self.wine_label_3.setText(i18n.traduc("Chemin vers l'executable:"))
        self.wine_parcouir_exe.setText(i18n.traduc("Parcourir..."))
        self.wine_label_4.setText(i18n.traduc("Icone:"))
        self.wine_parcouir_icone.setText(i18n.traduc("Parcourir..."))
