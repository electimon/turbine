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

'''Interface du dépot'''

from PyQt4 import QtGui, QtCore

WebKit = True
try:
    from PyQt4 import QtWebKit
except ImportError:
    WebKit = False

import sys, os, threading, socket, urllib
from installe import Telechargement, supprime_archive, modif_etat
from variables import variables, home, dossier_racine
from config import config #Lis le fichier de configuration
#import diff

import i18n

sys.path.append("libs")
import SOAPpy

class Foncs_Depot(object):
    '''Fonctions dédiés au chargement du dépôt et au dialogue avec le serveur'''
    
    ### Fonctions de tri du dépôt ###
    
    def parse_listelicence(self, id):
        '''Parse la liste des licences du ws'''
        #Renvoi la chaine de caractère pour la licence numéro id
        return self.listelicense[id][0][1]['value']
        
    def parse_listegenre(self, id,  val=0):
        '''Parse la liste des type de jeu du ws'''
        #Si val vaut 0, on renvoi l'id du type de jeu, si il vaut 1, on renvoi la chaine de caractère.
        return self.liste_genre[id]['value'][0][val]['value']
        
    def parse_listejeux(self, id, val=0):
        '''Parse la liste des jeux, contient la liste de tous les jeux plus quelques informations pour chacun d'eux
            id est le numéro du jeu dans la liste, val le numéro de l'information demandée.'''
        return self.liste_jeux[0][id]['value'][0][val]['value']
        
    def parse_detailjeux(self, no_jeu, val=0):
        '''Parse le tableau venant du webservice donnant le detail d'un jeu.
        id est le numéro du jeu dans le dépôt, val est le numéro de l'information demandée.'''        
        if self.n_jeu_courant != no_jeu: #Si les infos ont déjà été demandés, on ne re-télécharge pas les informations.
            try:
                self.detailjeux = self.clientSOAP.detailJeux(self.parse_listejeux(no_jeu, 6), int(self.lang))
            except:
                #Si on ne trouve pas le jeu en dépot dans la langue séléctionnée, on prend l'Anglais:
                self.detailjeux = self.clientSOAP.detailJeux(self.parse_listejeux(no_jeu, 6), 3)            
        self.n_jeu_courant = no_jeu
        return self.detailjeux['item'][val]['value']
    
    ### Fonctions de tri du dépôt ###
        
    def maj_depot(self):
        '''Met à jour le dépot côté client (Normalement au démarrage ou manuellement (réservé à la version de développement))'''
        #Créé la liste des langues du depot:
        #self.liste_lang=self.clientSOAP.listeLang()
        
        #Récupère la liste des types de jeux:
        self.liste_genre = self.clientSOAP.listeType(self.lang)[0]
        
        #Recupère la liste des licenses:
        self.listelicense = self.clientSOAP.listeLicence(self.lang)
                
        #On récupère la liste des jeux (avec toutes les infos qui vont avec, commande de lancement, icone, etc...):
        self.liste_jeux = self.clientSOAP.listeJeux()
       #print self.liste_jeux 
        
        #Récupère le nombre de jeux:
        self.nb_jeux = len(self.liste_jeux[0])
       #print self.nb_jeux
        
        self.liste_nom_jeux = []
        for i in range(self.nb_jeux): #Récupère les noms de jeux 
            self.liste_nom_jeux.append(self.parse_listejeux(i, 0))
        
        if self.int_etendue == 1:
            self.filtre_liste()
            
            #Affiche dans la boite adéquat la liste des type de jeux:
            self.comboBox.clear()
            for i in range(len(self.liste_genre)):
                chaine = self.parse_listegenre(i, 1)
                if chaine == "Tous":
                    chaine = (i18n.traduc("Tous"))
                self.comboBox.addItem(chaine)
            self.comboBox.setCurrentIndex(0)
            
            #Affiche dans la combobox la liste des licenses:
            self.combo_license.clear()
            for i in range(len(self.listelicense)):
                chaine  = self.parse_listelicence(i)
                if chaine == "Toutes":
                    chaine = (i18n.traduc("Tous"))
                self.combo_license.addItem(chaine) 
            self.combo_license.setCurrentIndex(0)

    def Thread_depot(self):
        '''Télécharge le dépôt dans un Thread, pour ne pas bloquer l'interface pendant les quelques secondes de telechargement'''
        th = threading.Thread(name=None, target=self.connexion_SOAP)
        th.start()

    def connexion_SOAP(self):
        '''Création du client SOAP, connexion au serveur'''
        serveur_soap = variables.SERVEUR_SOAP
        
        print "Serveur:", serveur_soap
        
        if variables.version_dev == 1:
            serveur_soap = serveur_soap + "/djl_dev.php"
        else:
            serveur_soap = serveur_soap + "/djl.php"
            
        self.clientSOAP = SOAPpy.SOAPProxy(serveur_soap)
            
        self.clientSOAP.config.dict_encoding = "utf8"
        self.clientSOAP.config.debug = 0
        self.clientSOAP.config.dumpSOAPIn = 0
        self.clientSOAP.config.dumpSOAPOut = 0 

        try:
            self.maj_depot()
            #print "Ok on a le dépôt" #temp1
        except (SOAPpy.Errors.HTTPError, socket.error),  x:
            #Si ça merde, c'est qu'on a pas de dépôt accessible en ligne, on affiche donc rien dans le dépot
            print "Problème chargement du dépôt:",  x
            self.liste_genre = []
            self.liste_jeux = []
            self.nb_jeux = 0
            self.charge_depot() #Charge le dépôt en dur
            return
        
        #self.action_creer_def.setEnabled(True)
        
        #On pré-télécharge dans un Thread les images afin de rendre la navigation dans le dépot plus rapide.
        th_tele_imgs = pre_telecharge_images(liste=self.clientSOAP.listeImage())
        th_tele_imgs.start()
                
        #On enregistre en local le minimum afin d'avoir la liste de jeux même sans réseau
        th_enregistre_depot = sauvegarde_depot(self.liste_jeux,  self.methode_depot)
        th_enregistre_depot.start() #temp1
        
        self.connecte_ws = 1
        
        variables.maj_listejeux = True
        #print "Init du client SOAP terminé"
        
    def charge_depot(self):
        '''Charge le dépot, soit depuis l'internet, ou si le fichier existe, depuis le fichier en dur.'''
        self.connecte_ws = 0
        if self.methode_depot == 1:
            nom_fichier  = config(info=2) + '/' + config(info=14) + '/liste_jeux.cPickle'
        else:
            nom_fichier  = config(info=2) + '/' + config(info=14) + '/liste_jeux.txt'

        #Si le fichier existe, c'est qu'on a le dépot en dur, on le charge donc
        if os.path.exists(nom_fichier):
            self.connecte_ws = 0
            if self.methode_depot == 1: #Si la methode est à 1, on utilise cPickle pour charger le dépôt
                import cPickle #Pour dé-sérialiser le dépôt
                #self.setWindowTitle(i18n.traduc("djl " + interface.version()) + " " + i18n.traduc("(Non connecte)"))
    
                self.liste_genre = []
                self.liste_jeux = []
                
                #Récupére la liste des jeux depuis le dépot en cache
                fichier = open(nom_fichier,  'r')
                try:
                    self.liste_jeux = [cPickle.load(fichier)] #<<< Dans une liste, sinon ça déconne avec le nouveau ws
                except EOFError:
                    fichier.close()
                    os.remove(nom_fichier)
                    self.charge_depot()
                    return
                    
                self.nb_jeux = len(self.liste_jeux)
                fichier.close()
                
            else: #Si methode est à 2, on charge le dépôt avec la methode faite maison (plus rapide, mais peut être plus boguée)
                fichier = open(nom_fichier,  'r')
                txt_cache_depot = fichier.readlines()
                fichier.close()
    
                liste = []
                self.liste_genre = []
                self.liste_jeux = []
    
                for i in range(len(txt_cache_depot)):
                    txt_cache_depot[i] = txt_cache_depot[i].split(';')
                    sous_dico = {}
                    
                    #print txt_cache_depot[i]
                    
                    txt_cache_depot[i][7] = txt_cache_depot[i][7].replace("\n",  "")
                    sous_dico = [[ \
                                 {'value':txt_cache_depot[i][0], 'key':'nom'}, \
                                 {'value':txt_cache_depot[i][1], 'key':'version'},  \
                                 {'value':txt_cache_depot[i][2], 'key':'codename'}, \
                                 {'value':txt_cache_depot[i][3],  'key':'icone'},  \
                                 {'value':txt_cache_depot[i][4], 'key':'commande'}, \
                                 {'value':int(txt_cache_depot[i][5]),  'key':'type'},  \
                                 {'value':int(txt_cache_depot[i][6]), 'key':'id_jeu'},  \
                                 {'value':txt_cache_depot[i][7], 'key':'url_site'} \
                                 #]}
                                 ]]
                    
                    liste.append(sous_dico)

                self.liste_jeux =  liste                
                self.nb_jeux = len(liste)

        else:
            self.liste_genre = []
            self.liste_jeux = []
            self.nb_jeux = 0
            #self.action_creer_def.setEnabled(False)

class UiDepot(object):
    def Cltimer(self):
        if self.clignote_depot:
            if self.val_clignote_depot == 0:
                self.tabDepot.setTabIcon(1, self.IconOngletTelechargement1)

                self.val_clignote_depot = 1
            else:
                self.tabDepot.setTabIcon(1, self.IconOngletTelechargement2)
                self.val_clignote_depot = 0
            
            self.t = threading.Timer(0.5, self.Cltimer)
            self.t.start()
        
    def timerEventDepot(self):
        '''Cette fonction est appellée toutes les secondes, ça permet de mettre à jour l'affichage et le calcul du débit par seconde du téléchargement.'''
        #print "-------"
        #print self.listeTelechargement
        #print variables.installe
        
        #Fais clignoter la barre de titre du dépôt si demandé:
        #if self.clignote_depot:
            #if self.val_clignote_depot == 0:
                #self.tabDepot.setTabIcon(1, self.IconOngletTelechargement1)

                #self.val_clignote_depot = 1
            #else:
                #self.tabDepot.setTabIcon(1, self.IconOngletTelechargement2)
                #self.val_clignote_depot = 0
            
        #Parcours la liste des téléchargements pour mettre à jour l'affichage
        for id in range(len(self.listeTelechargement)):
            obj = self.listeTelechargement[id]
            #Récupère les informations de téléchargement sur le Thread:
            nb_blocs, taille_bloc, taille_fichier = obj[0].renvoi_infos() 

            #Tant que le téléchargement n'est pas lancé, on n'affiche rien
            if taille_fichier != 1:
                if (nb_blocs*taille_bloc) <= taille_fichier:
                    #Calcul la taille de ce qui a déjà été téléchargé (en octets)
                    telecharge = nb_blocs * taille_bloc
                    
                    #Calcul la taille de ce qu'il reste à télécharger (en octets):
                    reste = taille_fichier - telecharge
        
                    #Calcul le total de données téléchargés et divise par le nombre de secondes afin d'avoir le débit kb/S
                    debit = (telecharge/self.iterationBoucleTele)/1024
                    
                    if debit > 0:
                        #Calcul le pourcentage d'avancement du téléchargement:
                        pourcentage = int(((telecharge+0.)/taille_fichier+0.)*100)
        
                        #Calcule le temps restant à télécharger en fonction du débit et du reste...
                        temps_restant = (reste/1024) / debit
                        temps_restant_minutes = temps_restant / 60 #Récupère le nombre de minutes en divisant simplement par 60
                        
                        temps_restant_secondes =  temps_restant - (temps_restant_minutes*60) #Recupère le nombre de secondes restantes
                        
                        if temps_restant_secondes < 10:
                            temps_restant_secondes =  "0" + str(temps_restant_secondes)
                        
                        nom_jeu = obj[3]
                        #On demande d'éditer la ligne, on récupère l'index, puis l'objet depuis l'index et enfin on édite l'objet
                        item = self.listWidgetTelechargement.item(id)
                        item.setText(nom_jeu + ' - ' + str(pourcentage) + ' % - ' + str(taille_fichier/1048576) +  " " + _('Mo') + ' - ' + str(debit)+' ' + _('Ko/s') + ' - ' + i18n.traduc("Temps restant:") + " " + str(temps_restant_minutes) + ":" + str(temps_restant_secondes))
                else:
                    #item = self.listWidgetTelechargement.item(self.listWidgetTelechargement.currentRow())
                    item = self.listWidgetTelechargement.item(id)
                    try:
                        item.setText(i18n.traduc("Decompression de l'archive en cours..."))
                    except AttributeError, x:
                        print x
                        continue
                        
            #Vérifi si l'installation est terminée:
            if variables.installe[obj[2]]:
                print "Terminé:" + str(obj[2])
                
                self.listWidgetTelechargement.takeItem(id) #Supprime la ligne de la liste (Widget)
                
                modif_etat(obj[2], val_etat = 1) #Met l'etat du jeu a 'installé'
                self.maj_liste() #Met à jour la liste de jeux principale
                del variables.installe[obj[2]]
                del self.listeTelechargement[id]

                return #On passe l'itération du timer pour éviter les problèmes suite à la suppression des éléments dans les listes
        self.iterationBoucleTele = self.iterationBoucleTele + 1

    def contextMenuEventDepot(self, event):
        '''Definition du menu contextuel'''
        if len(self.listeTelechargement) > 0:
            self.menuCDepot.exec_(event.globalPos())
    
    def StopTelechargement(self):
        '''Stop le téléchargement du jeu en cours (Annule)'''
        #print self.listeTelechargement
        id = self.listWidgetTelechargement.currentRow()
        
        #Stop le thread dédié au téléchargement:  (une exception est levée si le téléchargement n'a pas encore commencé, dans ce cas, on passe)
        try:
            self.listeTelechargement[id][0].annule()
            self.listeTelechargement[id][0]._Thread__stop()
        except TypeError, x:
            print x
            
        #Supprime l'archive: (une exception est levée si le téléchargement n'a pas encore commencé, puisqu'il n'y a pas d'archive)
        try:
            supprime_archive(self.listeTelechargement[id][1])
        except OSError, x:
            print x
            
        del variables.installe[self.listeTelechargement[id][2]] #Vire la variable d'installation du jeu (nom_jeu)
            
        #Modif l'etat pour que le dépot comprenne que l'installation a été annulée
        modif_etat(self.listeTelechargement[id][2], val_etat=4)
        
        self.maj_liste() #Met à jour la liste de jeux principale
            
        self.listWidgetTelechargement.takeItem(id) #Supprime la ligne de la liste (Widget)
        del self.listeTelechargement[id] #Supprime l'instance de la liste (Tableau)
        #print self.listeTelechargement
            
    def NouvTelechargement(self, adresse_telecharge, nom_archive, nom_jeu, commande, version, icone, titre):
        '''L'utilisateur a lancé un nouveau téléchargement, on l'ajoute à la liste'''
        item = QtGui.QListWidgetItem()

        item.setIcon(QtGui.QIcon(icone))
        item.setText(titre)
        
        self.listWidgetTelechargement.addItem(item)
        
        variables.installe[nom_jeu] = False #Ajoute au dictionnaire qui référence les téléchargements
        
        self.clignote_depot = True #Fais clignoter la barre du depot, que l'utilisateur voit que le téléchargement est lancé
        self.Cltimer()
        
        #Envoi le téléchargement:
        th_t = Telechargement(adresse_telecharge, nom_archive, nom_jeu, commande, version)
        th_t.start()
        self.listeTelechargement.append((th_t, nom_archive, nom_jeu, titre)) #Ajoute l'instance du téléchargement dans la liste ainsi que le nom de l'archive
  
    def ch_tabDepot(self):
        '''La fonction est appelée quand on change d'onglet dans le dépôt'''
        if self.tabDepot.currentIndex() == 1:  #Onglet téléchargement
            self.clignote_depot = False #Arrete le clignotement du dépot, si besoin
            self.tabDepot.setTabIcon(1, self.IconOngletTelechargement1)
        #else: #Onglet depot
            #self.clignote_depot = True #temp
        
    def SetupUi_Depot(self):
        '''Envoi l'affichage du dépôt et de ses objets, le tout est composé en deux partie, sur deux onglets
        Le premier, le dépôt à proprement parler, l'autre l'onglet des téléchargements, liste les téléchargements en cours'''

        self.listeTelechargement = [] #Contiendra la liste des instances de téléchargement
        self.iterationBoucleTele = 0 #Compte les itérations de boucles pour le téléchargement, utilisé pour calculer le temps restant
        self.clignote_depot = False #Le titre de l'onglet téléchargement dans le dépot clignotera quand ça passer à True
        self.val_clignote_depot = 0

        #self.tab_2 est défini dans le fichier source 'interface'
        #####Layout principal du dépot:
        self.gridlayoutD = QtGui.QGridLayout(self.tab_2)
        self.gridlayoutD.setObjectName("gridlayoutD")
        
        #Sous barre d'onglet de l'onglet dépôt
        self.tabDepot = QtGui.QTabWidget(self.tab_2)
        self.tabDepot.setTabPosition(QtGui.QTabWidget.West) #Rend la barre verticale
        
        try:
            self.tabDepot.setDocumentMode(True) #Vire l'encadrement de l'onglet (uniquement dispo depuis Qt 4.5).
        except AttributeError:
            pass
            
        self.tabDepot.setObjectName("tabDepot")
        self.gridlayoutD.addWidget(self.tabDepot,0,0)
        ######
        
        self.tab_2_1 = QtGui.QWidget(self.tabDepot) #Dépot
        self.tab_2_1.setObjectName("tab_2_1")
        
        self.tab_2_2 = QtGui.QWidget(self.tabDepot) #Téléchargements
        self.tab_2_2.setObjectName("tab_2_2")
        
        self.tabDepot.addTab(self.tab_2_1,"")
        self.tabDepot.addTab(self.tab_2_2,"")
        
        self.tabDepot.setTabIcon(0, QtGui.QIcon(dossier_racine + "/res/txt_oxygen.png"))
        self.IconOngletTelechargement1 = QtGui.QIcon(dossier_racine + "/res/telech1.png")
        self.IconOngletTelechargement2 = QtGui.QIcon(dossier_racine + "/res/transp.png")
        self.tabDepot.setTabIcon(1, self.IconOngletTelechargement1)

        ##Layouts du dépot:
        self.gridlayout_2 = QtGui.QGridLayout(self.tab_2_1) #Principal
        self.gridlayout_2.setObjectName("gridlayout_2")
        
        self.gridlayout_2_1 = QtGui.QGridLayout() # Conteneur à droite
        self.gridlayout_2_1.setObjectName("gridlayout_2_1")
        
        self.gridlayout_2_1h = QtGui.QHBoxLayout() #En haut dans le conteneur de droite
        self.gridlayout_2_1h.setObjectName("gridlayout_2_1h")
        
        self.gridlayout_2_2 = QtGui.QVBoxLayout() #Au millieu dans le conteneur de droite
        self.gridlayout_2_2.setObjectName("gridlayout_2_2")
        
        self.gridlayout_2_3 = QtGui.QVBoxLayout() #Conteneur en bas dans le conteneur de droite
        self.gridlayout_2_3.setObjectName("gridlayout_2_3")
        
        self.gridlayout_2_h_m = QtGui.QHBoxLayout() #Entre la description et la capture d'écran
        self.gridlayout_2_h_m.setObjectName("gridlayout_2_h_m")
        
        self.gridlayout_2_v_m = QtGui.QHBoxLayout() #Capture d'écran
        self.gridlayout_2_v_m.setObjectName("gridlayout_2_v_m")
        
        self.gridlayout_2_v = QtGui.QVBoxLayout() #Vertical à gauche dans le principal
        self.gridlayout_2_v.setObjectName("gridlayout_2_v")

        self.gridlayout_2.addLayout(self.gridlayout_2_v,0,0)
        self.gridlayout_2.addLayout(self.gridlayout_2_1,0,1)
        self.gridlayout_2_1.addLayout(self.gridlayout_2_1h,0,0)
        self.gridlayout_2_1.addLayout(self.gridlayout_2_2,1,0)
        self.gridlayout_2_1.addLayout(self.gridlayout_2_3,2,0)
        
        self.gridlayout_2_3.addLayout(self.gridlayout_2_h_m)
        self.gridlayout_2_3.addLayout(self.gridlayout_2_v_m)
        
        ### Nouveau
        self.gridlayout_2_1_0v = QtGui.QVBoxLayout() #Dans le conteneur en haut à droite (Nom du jeu)
        self.gridlayout_2_1_0v.setObjectName("gridlayout_2_1_0v")

        self.gridlayout_2_1_2g = QtGui.QGridLayout() #Dans le conteneur en haut à droite (Genre, taille, licence)
        self.gridlayout_2_1_2g.setObjectName("gridlayout_2_1_2g")
        ### /Nouveau
        
        #Fin des layouts du dépot
        ###
        
        self.label_8 = QtGui.QLabel(self.tab_2_1)
        self.label_8.setObjectName("label_8")
        self.gridlayout_2_v.addWidget(self.label_8)

        self.comboBox = QtGui.QComboBox(self.tab_2_1)
        self.comboBox.setObjectName("comboBox")
        
        self.gridlayout_2_v.addWidget(self.comboBox)

        self.combo_license = QtGui.QComboBox(self.tab_2_1)
        self.combo_license.setObjectName("combo_license")
        self.gridlayout_2_v.addWidget(self.combo_license)

        self.label = QtGui.QLabel(self.tab_2_1)
        self.label.setObjectName("label")
        self.gridlayout_2_v.addWidget(self.label)

        self.widget_liste_jeux = QtGui.QListWidget(self.tab_2_1)
        self.widget_liste_jeux.setObjectName("widget_liste_jeux")
        
        self.widget_liste_jeux.setMinimumSize(QtCore.QSize(200,200)) ##rep
        self.widget_liste_jeux.setMaximumSize(QtCore.QSize(250,1280))
        
        self.gridlayout_2_v.addWidget(self.widget_liste_jeux)

        self.boutton_installer = QtGui.QPushButton(self.tab_2_1)
        self.boutton_installer.setObjectName("boutton_installer")
        self.boutton_installer.setEnabled(False)
        self.gridlayout_2_v.addWidget(self.boutton_installer)

        self.boutton_supprimer = QtGui.QPushButton(self.tab_2_1)
        self.boutton_supprimer.setObjectName("boutton_supprimer")
        self.boutton_supprimer.setEnabled(False)
        self.gridlayout_2_v.addWidget(self.boutton_supprimer)

        self.boutton_maj = QtGui.QPushButton(self.tab_2_1)
        self.boutton_maj.setObjectName("boutton_maj")
        self.boutton_maj.setEnabled(False)
        self.gridlayout_2_v.addWidget(self.boutton_maj)

        self.label_2 = QtGui.QLabel(self.tab_2_1)
        self.label_2.setObjectName("label_2")
        self.gridlayout_2_2.addWidget(self.label_2)

        if WebKit: #Si QtWebkit est disponible...
            self.texte_description = QtWebKit.QWebView(self.tab_2_1)
            self.config_description = self.texte_description.settings()
            print QtWebKit.QWebSettings.FixedFont
            try:
                self.config_description.setFontFamily(QtWebKit.QWebSettings.FixedFont, "")
            except TypeError, x:
                print "self.config_description.setFontFamily():", str(x)
            self.texte_description.setTextSizeMultiplier(0.9)
        else:
            self.texte_description = QtGui.QTextEdit(self.tab_2_1)
            self.texte_description.setReadOnly(True)
            self.texte_description.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
  
        self.texte_description.setObjectName("texte_description")
        self.texte_description.setEnabled(True)
        self.texte_description.setMinimumSize(20, 20)

        self.gridlayout_2_2.addWidget(self.texte_description)

        self.widget_capture = QtGui.QLabel(self.tab_2_1)
        self.widget_capture.setObjectName("widget_capture")
        self.widget_capture.setMinimumSize(QtCore.QSize(320,240))
        self.widget_capture.setMaximumSize(QtCore.QSize(320,240))
        self.gridlayout_2_v_m.addWidget(self.widget_capture)
        
        ###Objets Icone, noms de jeux, etat...
        self.widget_icone = QtGui.QLabel(self.tab_2_1)
        self.widget_icone.setObjectName("widget_icone")
        self.widget_icone.setMinimumSize(QtCore.QSize(64,64))
        self.widget_icone.setMaximumSize(QtCore.QSize(64,64))
        self.gridlayout_2_1h.addWidget(self.widget_icone)

        self.label_4_2 = QtGui.QLabel(self.tab_2_1) #Nom du jeu, à côté de l'état
        self.label_4_2.setFont(self.font3)
        self.gridlayout_2_1_0v.addWidget(self.label_4_2)
        
        self.gridlayout_2_1h.addLayout(self.gridlayout_2_1_0v, 0)
        self.gridlayout_2_1_0v.addLayout(self.gridlayout_2_1_2g, 0)
        
        self.label_4_v = QtGui.QLabel(self.tab_2_1) #Version du jeu
        self.label_4_v.setFont(self.font)
        self.gridlayout_2_1_2g.addWidget(self.label_4_v, 0, 0)
        
        self.label_4 = QtGui.QLabel(self.tab_2_1) #Etat du jeu
        self.gridlayout_2_1_2g.addWidget(self.label_4, 0, 1)
        
        ###</>
        
        #self.label_4_2.setFont(self.font)
        self.label_4_2.setObjectName("label_4_2")

        #self.label_4.setFont(self.font)
        self.label_4.setObjectName("label_4")
        ############
        
        #Contenu additionnel:
        self.label_5 = QtGui.QLabel(self.tab_2_1) #Genre
        self.label_5.setObjectName("label_5")
        self.gridlayout_2_1_2g.addWidget(self.label_5, 1, 0)

        self.label_6 = QtGui.QLabel(self.tab_2_1) #Taille
        self.label_6.setObjectName("label_6")
        self.gridlayout_2_1_2g.addWidget(self.label_6, 1, 1)

        self.label_7 = QtGui.QLabel(self.tab_2_1) #Plate-forme
        self.label_7.setObjectName("label_7")
        self.gridlayout_2_1_2g.addWidget(self.label_7, 2, 0)
        
        self.label_9 = QtGui.QLabel(self.tab_2_1) #Licence
        self.label_9.setObjectName("label_9")
        self.gridlayout_2_1_2g.addWidget(self.label_9, 2, 1)

        self.b_site = QtGui.QPushButton(self.tab_2_1)
        self.b_site.setMinimumSize(QtCore.QSize(150,28))
        self.b_site.setMaximumSize(QtCore.QSize(150,28))
        self.b_site.setObjectName("b_site")
        self.b_site.setEnabled(False)
        self.gridlayout_2_h_m.addWidget(self.b_site)

        self.b_article = QtGui.QPushButton(self.tab_2_1)
        self.b_article.setMinimumSize(QtCore.QSize(150,28))
        self.b_article.setMaximumSize(QtCore.QSize(150,28))
        self.b_article.setObjectName("b_article")
        self.b_article.setEnabled(False)
        self.gridlayout_2_h_m.addWidget(self.b_article)
        
        ###Deuxième onglet, la fenêtre des téléchargements:
        self.gridlayout_2T = QtGui.QGridLayout(self.tab_2_2) #Principal
        self.gridlayout_2T.setObjectName("gridlayout_2T")
        self.listWidgetTelechargement = QtGui.QListWidget(self.tab_2_2)
        self.listWidgetTelechargement.setFont(self.font2)
        
        self.listWidgetTelechargement.setIconSize(QtCore.QSize(32,32))
        self.listWidgetTelechargement.setGridSize(QtCore.QSize(34,34))
        
        self.gridlayout_2T.addWidget(self.listWidgetTelechargement)
        self.listWidgetTelechargement.contextMenuEvent = self.contextMenuEventDepot
        
        self.timerTelechargement = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timerTelechargement, QtCore.SIGNAL("timeout()"), self.timerEventDepot)
        self.timerTelechargement.start(1000)
        ###/
        
        ###Definition du menu contextuel:
        self.menuCDepot = QtGui.QMenu(self)
        self.menuCDepot.setFont(self.font)
        
        self.act_AnnuleTelechargement = QtGui.QAction(_((i18n.traduc("Annuler"))), self)
        self.act_AnnuleTelechargement.connect(self.act_AnnuleTelechargement, QtCore.SIGNAL("triggered()"), self.StopTelechargement)
        self.menuCDepot.addAction(self.act_AnnuleTelechargement)
        icone = QtGui.QIcon(dossier_racine + '/res/redemarre_oxygen.png')
        self.act_AnnuleTelechargement.setIcon(icone)
        ###/
        
        self.connexionsDepot()
        self.traducsDepot()
    
    def connexionsDepot(self):
        #Lève un évènement quand on change d'onglet dans le dépôt
        self.tabDepot.connect(self.tabDepot, QtCore.SIGNAL("currentChanged(int)"), self.ch_tabDepot)
        
        #Attention, self.filtre_liste est ici executé au démarrage, quand la combobox s'initialise:
        self.comboBox.connect(self.comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.filtre_liste)
        self.combo_license.connect(self.combo_license, QtCore.SIGNAL("currentIndexChanged(int)"), self.filtre_liste)
        self.widget_liste_jeux.connect(self.widget_liste_jeux, QtCore.SIGNAL("itemSelectionChanged()"), self.maj_description)
        #Double cliquer sur un jeu de la liste revient à cliquer sur le bouton installer/lancer
        self.widget_liste_jeux.connect(self.widget_liste_jeux, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.installer_jouer)
        
        self.boutton_installer.connect(self.boutton_installer, QtCore.SIGNAL("clicked()"), self.installer_jouer)
        self.boutton_supprimer.connect(self.boutton_supprimer, QtCore.SIGNAL("clicked()"), self.supprimer)
        self.boutton_maj.connect(self.boutton_maj, QtCore.SIGNAL("clicked()"), self.maj_jeu)
        self.b_article.connect(self.b_article, QtCore.SIGNAL("clicked()"), self.navigateur_article)
        self.b_site.connect(self.b_site, QtCore.SIGNAL("clicked()"), self.navigateur_site)
    
    def traducsDepot(self):
        self.widget_liste_jeux.clear()
        self.boutton_installer.setText(i18n.traduc("Jouer"))
        self.boutton_supprimer.setText(i18n.traduc("Supprimer"))
        self.boutton_maj.setText(i18n.traduc("Mettre a jour"))
        self.texte_description.setHtml(i18n.traduc("Choisissez un jeu pour avoir une description."))
        self.label.setText(i18n.traduc("Liste des jeux disponible:"))
        self.label_2.setText(i18n.traduc("Description:"))

        #self.label_5.setText(i18n.traduc("Genre"))
        #self.label_6.setText(i18n.traduc("Taille"))
        self.label_7.setText(i18n.traduc("Plate-forme: x86"))
        self.label_8.setText(i18n.traduc("Trier les jeux:"))
        #self.label_9.setText(i18n.traduc("Licence"))
        self.b_article.setText(i18n.traduc("Plus d'informations..."))
        self.b_site.setText(i18n.traduc("Site internet") + "...")
        
        self.tabDepot.setTabText(0, i18n.traduc("Depot"))
        self.tabDepot.setTabText(1, i18n.traduc("Telechargement"))
        ############

class pre_telecharge_images(threading.Thread):
    def __init__(self,  liste):
        '''Thread pour pré-télécharger dans le cache les images du dépot afin de rendre la navigation plus rapide'''
        threading.Thread.__init__(self)
        self.liste = liste
        
    def run(self):
        '''Télécharge les images...'''
        rep = config(info=2) + '/' + config(info=14) + '/imgs/'
        lien = "http://djl.jeuxlinux.fr/images/"

        nb = len(self.liste[0])
        for i in range(nb):
            try:
                #Vérifi le type d'info (renvoi 1 pour une icone, 2 pour une image).
                type_= self.liste[0][i]['value'][0][0]['value']
            except IndexError:
                continue
            if int(type_) == 2: #Si c'est une image...
                nom = self.liste[0][i]['value'][0][1]['value']
                if not os.path.exists(rep+nom):
                    try:
                        urllib.urlretrieve(lien+nom, rep+nom,  reporthook=None)
                    except IOError, x:
                        print x
                    #print "Téléchargé:",  nom,  str(i) + "/" + str(nb)
        #print "Fin"

class sauvegarde_depot(threading.Thread):
    def __init__(self,  liste,  methode=1):
        '''Thread pour sauvegarder certaines infos du dépot afin de pouvoir les utiliser si on est déconnecté du serveur'''
        threading.Thread.__init__(self)
        self.liste = liste[0]
        #Si la methode est 1, on utilise cPickle pour enregistrer le dépôt (plus lent mais probablement moins bogué)
        #Si c'est à 2, on enregistre dans un format fait maison, rapide mais peut être plus bogué que Pickle
        self.methode = methode

    def run(self):
        '''Ecrit les fichiers...'''
        if self.methode == 1:
            import cPickle
            rep = config(info=2) + '/' + config(info=14) + '/'
            fichier_liste_jeux = rep + 'liste_jeux.cPickle'

            fichier_liste_jeux = open(fichier_liste_jeux, 'wb')
            cPickle.dump(self.liste,  fichier_liste_jeux,  protocol=2)
            fichier_liste_jeux.close()
        else:
            rep = config(info=2) + '/' + config(info=14) + '/'
            fichier_liste_jeux = rep + 'liste_jeux.txt'
            
            #Ouvre le fichier de cache (écriture)
            fichier_liste_jeux = open(fichier_liste_jeux, 'w')
            
            #Parcours toutes les entrées du dépôt...
            for i in range(len(self.liste)):
                ligne = ""
                #Parcours tous les éléments de chaque entrée...
                for x in range(len(self.liste[i]['value'][0])):
                    info = self.liste[i]['value'][0][x]['value']
                    if x == 0:
                       ligne = info
                    else:
                        ligne = ligne + ";" + info
                    
                #print ligne
                if i > 0:
                    fichier_liste_jeux.write("\n")
                fichier_liste_jeux.write(ligne)
            fichier_liste_jeux.close()
