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

'''Fenêtre de configuration de djl'''

import os, sys, threading
from PyQt4 import QtCore, QtGui
from locale import getdefaultlocale

#from installe import config
from variables import variables

home = os.path.expanduser('~')
dossier_racine = os.getcwd()
import i18n

#if not os.path.exists(home + '/.djl/config'):
   #import gettext
   #try:
       #lang = gettext.translation(domain="messages", localedir = os.getcwd() + '/i18n', languages=[str(getdefaultlocale()[0])])
       #lang.install()
   #except:
       #lang = gettext.translation(domain="messages", localedir = os.getcwd() + '/i18n', languages=['en_US'])
       #lang.install()
       
   #try: _
   #except NameError:
       #def _(s):
           #return s

class Ui_Configuration(QtGui.QWidget):
    def __init__(self, parent=None):
        '''Affiche la fenêtre de configuration de djl (On charge toute la config à l'init)'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)
        
        self.home = os.path.expanduser('~')
        self.adresse = ''

        self.setupUi(self)
        

        #Défini le texte de la boite pour créer le raccourcis de djl dans le menu KDE/Gnome, en fonction si le fichier existe ou pas
        if os.path.exists(home + '/.local/share/applications/djl.desktop') == True:
            self.b_raccourci.setText(i18n.traduc("Supprimer raccourci de djl du menu KDE/Gnome"))
        else:
            self.b_raccourci.setText(i18n.traduc("Ajouter un raccourci de djl dans le menu KDE/Gnome"))

        self.b_parcourir.connect(self.b_parcourir, QtCore.SIGNAL("clicked()"), self.parcours_rep)
        self.b_parcourir_nav.connect(self.b_parcourir_nav, QtCore.SIGNAL("clicked()"), self.parcours_nav)
        self.b_valider.connect(self.b_valider, QtCore.SIGNAL("clicked()"), self.valider)
        self.b_fermer.connect(self.b_fermer, QtCore.SIGNAL("clicked()"), self.ferme)
        self.b_raccourci.connect(self.b_raccourci, QtCore.SIGNAL("clicked()"), self.raccourci)
        
        self.taille_police.connect(self.taille_police, QtCore.SIGNAL("valueChanged(int)"), self.ch_police)

        #Si le fichier de configuration, existe, on affiche la configuration dans l'interface:
        fichier_cfg = self.home + '/.djl/config'
        if os.path.exists(fichier_cfg) == True:
            fichier = open(fichier_cfg, 'r')
            texte_fichier = fichier.readlines()

            #Affiche les 'checkboxs' validés ou non suivant la config:
            chk_valide = texte_fichier[0]
            chk_valide = chk_valide.replace('telecharger_lancer = ', '')
            chk_valide = chk_valide.replace('\n', '')
            if int(chk_valide) == 1:
                self.check_b_lancer_jeu.setChecked(True)
            else:
                self.check_b_lancer_jeu.setChecked(False)

            chk_suppr = texte_fichier[1]
            chk_suppr = chk_suppr.replace('telecharger_supprimer = ', '')
            chk_suppr = chk_suppr.replace('\n', '')
            if int(chk_suppr) == 1:
                self.check_b_suppr_archive.setChecked(True)
            else:
                self.check_b_suppr_archive.setChecked(False)
                
            #Affiche l'adresse d'installation des jeux dans le champ correspondant:
            addr = texte_fichier[2]
            addr = addr.replace('rep_jeux = ', '')
            addr = addr.replace('\n', '')
            self.ligne_adresse.setText(addr)

            chk_affiche_miniature = texte_fichier[3]
            chk_affiche_miniature = chk_affiche_miniature.replace('afficher_miniature = ', '')
            chk_affiche_miniature = chk_affiche_miniature.replace('\n', '')

            if int(chk_affiche_miniature) == 1:
                self.check_b_icone_barre.setChecked(True)
            else:
                self.check_b_icone_barre.setChecked(False)

            try:
                chk_maj_demarrage = texte_fichier[4]
                chk_maj_demarrage = chk_maj_demarrage.replace('maj_demarrage = ', '')
                chk_maj_demarrage = chk_maj_demarrage.replace('\n', '')

                if int(chk_maj_demarrage) == 1:
                    self.check_b_maj_demarrage.setChecked(True)
                else:
                    self.check_b_maj_demarrage.setChecked(False)
            except IndexError:
                #Si il y a exception (parce que la ligne dans le fichier de configuration est manquante) on remplace par le choix par defaut::
                self.check_b_maj_demarrage.setChecked(True)

            #Onglet à afficher au démarrage:
            try:
                onglet = texte_fichier[5]
                onglet = onglet.replace('onglet = ', '')
                onglet = onglet.replace('\n', '')
                
                self.comboBox.setCurrentIndex(int(onglet))

            except:
                self.comboBox.setCurrentIndex(0)
            
            try:
                nav = texte_fichier[6]
                nav = nav.replace('navigateur = ', '')
                nav = nav.replace('\n', '')
            except:
                nav = '/usr/bin/firefox'
            self.ligne_navigateur.setText(nav)
            
            #Configuration si l'on doit afficher la sortie des jeux à leur lancement
            try:
                chk_debug = texte_fichier[7]
                chk_debug = chk_debug.replace('debug = ', '')
                chk_debug = chk_debug.replace('\n', '')

                if int(chk_debug) == 1:
                    self.check_b_debug.setChecked(True)
                else:
                    self.check_b_debug.setChecked(False)
            except IndexError:
                #Si il y a exception (parce que la ligne dans le fichier de configuration est manquante) on remplace par le choix par defaut::
                self.check_b_debug.setChecked(False)
            
            #Vérifi si la gestion des dépendances est activé ou non:
            try:
                chk_dependances = texte_fichier[16]
                chk_dependances = chk_dependances.replace('dependances = ', '')
                chk_dependances = chk_dependances.replace('\n', '')

                if int(chk_dependances) == 1:
                    self.check_b_dependances.setChecked(True)
                else:
                    self.check_b_dependances.setChecked(False)
            except IndexError:
                #Si il y a exception (parce que la ligne dans le fichier de configuration est manquante) on remplace par le choix par defaut::
                self.check_b_dependances.setChecked(False)
            
            #Vérifi si les jeux doivent être lancé dans un second serveur graphique:
            try:
                chk_composition = texte_fichier[8]
                chk_composition = chk_composition.replace('composition = ', '')
                chk_composition = chk_composition.replace('\n', '')

                if int(chk_composition) == 1:
                    self.check_b_composition.setChecked(True)
                else:
                    self.check_b_composition.setChecked(False)
            except IndexError:
                #Si il y a exception (parce que la ligne dans le fichier de configuration est manquante) on remplace par le choix par defaut::
                self.check_b_composition.setChecked(False)
                
            #Réécrit si l'on utilise l'interface étendue ou simple:
            try:
                self.type_gui = texte_fichier[10]
                self.type_gui = self.type_gui.replace('type_gui = ', '')
                self.type_gui = self.type_gui.replace('\n', '')
            except IndexError:
                self.type_gui = "1"
                
            #Partie pseudo sur IRC:
            try:
                txt_pseudo = texte_fichier[11]
                txt_pseudo = txt_pseudo.replace('pseudo = ', '')
                txt_pseudo = txt_pseudo.replace('\n', '')
                #txt_pseudo = txt_pseudo.replace("-djl","")
    
                self.ligne_pseudo.setText(txt_pseudo)
            except IndexError:
                self.ligne_pseudo.setText(str(os.environ["USER"]).capitalize())
            
            #Démarrage (ou pas) du client IRC au démarrage
            try:
                conn_irc_demarrage = texte_fichier[12]
                conn_irc_demarrage = conn_irc_demarrage.replace('conn_irc_demarrage = ', '')
                conn_irc_demarrage = conn_irc_demarrage.replace('\n', '')
                
                if int(conn_irc_demarrage) == 1:
                    self.chk_conn_irc.setChecked(True)
                else:
                    self.chk_conn_irc.setChecked(False)
                
            except IndexError:
                self.chk_conn_irc.setChecked(True)
                
            #Couleur de fond du client IRC:
            try:
                fond_irc = texte_fichier[13]
                fond_irc = fond_irc.replace('fond_irc = ', '')
                fond_irc = fond_irc.replace('\n', '')
                
                self.couleur_irc.setCurrentIndex(int(fond_irc))

            except IndexError:
                self.couleur_irc.setCurrentIndex(0)
                
            #Taille des polices:
            try:
                taille_police = texte_fichier[14]
                taille_police = taille_police.replace('taille_police = ', '')
                taille_police = taille_police.replace('\n', '')
                
                self.taille_police.setValue(int(taille_police))

            except IndexError:
                self.taille_police.setValue(9)

            #Canaux IRC
            try:
                canaux = texte_fichier[15]
                canaux = canaux.replace('canaux_IRC = ', '')
                canaux = canaux.replace('\n', '')
                self.ligne_canaux.setText(canaux)

            except IndexError:
                try:
                    loc = getdefaultlocale()[0].split("_")[0]
                except:
                    loc = "en"
                self.ligne_canaux.setText("#djl" + " " + "#djl-"+str(loc))

        #Si le fichier de configuration n'existe pas, on affiche les choix par défaut
        else:
            self.ligne_adresse.setText(self.home + '/.djl')
            self.check_b_suppr_archive.setChecked(True)
            self.check_b_lancer_jeu.setChecked(False)
            self.check_b_icone_barre.setChecked(True)
            self.check_b_maj_demarrage.setChecked(True)
            self.check_b_debug.setChecked(False)
            self.check_b_composition.setChecked(False)
            self.check_b_dependances.setChecked(False)
            self.chk_conn_irc.setChecked(False)
            self.type_gui = "1"
            self.taille_police.setValue(9)
            
            try:
                loc = getdefaultlocale()[0].split("_")[0]
            except:
                loc = "en"
            self.ligne_canaux.setText("#djl" + " " + "#djl-"+str(loc))
            
        #Raccourcis claviers:
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.close)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self, self.valider)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter), self, self.valider)
    
    def ch_police(self):
        '''Rafraichi tout djl quand l'on choisi une nouvelle taille de police.'''
        self.font.setPointSize(self.taille_police.value())
        self.setFont(self.font)
        variables.ch_police=self.taille_police.value()
        #print "Taille police:", str(self.taille_police.value())

    def parcours_nav(self):
        '''Affiche une boite de dialogue pour parcourir le chemin vers le navigateur'''
        self.navigateur = QtGui.QFileDialog.getOpenFileName(self, '', self.home)
        self.ligne_navigateur.setText(self.navigateur)

    def raccourci(self):
        '''Supprime ou créé le raccourci du menu KDE/Gnome'''
        if os.path.exists(home + '/.local/share/applications/djl.desktop') == True:
            os.remove(home + '/.local/share/applications/djl.desktop')
            self.b_raccourci.setText(i18n.traduc("Ajouter un raccourci de djl dans le menu KDE/Gnome"))
            print _('Raccourcis supprime')
        else:
            #dossier_racine = os.getcwd()
            if not os.path.exists(home + '/.local/share/applications'):
                os.mkdir(home + '/.local/share/applications')
            n_fichier = home + '/.local/share/applications/djl.desktop'
            fichier = open(n_fichier, 'w')

            fichier.write('[Desktop Entry]')
            fichier.write('\n')
            fichier.write('Type=Application')
            fichier.write('\n')
            fichier.write('Name=djl')
            fichier.write('\n')
            fichier.write(_('GenericName[fr]=Depot jeux linux'))
            fichier.write('\n')
            fichier.write(_('GenericName=Depot jeux linux'))
            fichier.write('\n')
            fichier.write(_('Comment[fr]=Un gestionnaire de jeux videos pour Linux'))
            fichier.write('\n')
            fichier.write(_('Comment=Un gestionnaire de jeux videos pour Linux'))
            fichier.write('\n')
            fichier.write('Exec=' + dossier_racine + '/../djl.sh')
            #fichier.write('Exec=' + 'python2.5 ' + dossier_racine + '/djl.py')
            
            ##Debogage
            #fichier.write("\n")
            #fichier.write("Terminal=true")
            #fichier.write("\n")
            #fichier.write("TerminalOptions=\s--noclose")
            ##/Debogage
            
            fichier.write('\n')
            fichier.write('Path=' + dossier_racine)
            fichier.write('\n')
            fichier.write('Icon=' + dossier_racine + '/icone.png')
            fichier.write('\n')
            #fichier.write('Categories=Application;Game;')
            fichier.write('Categories=Game;')
            fichier.close()
            print _('Raccourci cree')
            self.b_raccourci.setText(i18n.traduc("Supprimer raccourci de djl du menu KDE/Gnome"))

    def parcours_rep(self):
        '''Affiche une boite de dialogue pour parcourir le répertoire d'installation des jeu'''
        self.adresse = QtGui.QFileDialog.getExistingDirectory(self, '', self.home)
        self.ligne_adresse.setText(self.adresse)

    def valider(self):
        '''Quand on clique sur le bouton valider...'''
        fichier_cfg = self.home + '/.djl/config'
        #Le si le fichier de configuration n'existe pas et que l'utilisateur clique sur valider, on sauvegarde la configuration et on lance la fenetre principale
        if not os.path.exists(fichier_cfg):
            self.sauve_config()

            #On lance la fenetre principale de djl dans un processus séparé, puis on ferme la fenetre de configuration
            #self.th_lance_fen = lance_fen_principale()
            #self.th_lance_fen.start()
            #sys.exit()
            self.lance_fen_principale()
            
        else:
            self.sauve_config()
            self.close()
            
    def lance_fen_principale(self):
        '''Si le fichier de configuration n'existait pas, on part du principe que c'est le premier lancement de djl, 
        djl n'est pas encore lancé, seul la fenêtre de configuration l'a été, on lance donc maintenant un nouveau djl.'''
        import subprocess
        p=subprocess.Popen('python djl_main.py', executable=None, shell=True, cwd=str(dossier_racine))
        self.close()
        sys.exit()

    def ferme(self):
        '''Ferme la fenêtre'''
        fichier_cfg = self.home + '/.djl/config'
        #Le si le fichier de configuration n'existe pas et que l'utilisateur clique sur fermer, on sauvegarde la configuration par défaut
        if not os.path.exists(fichier_cfg):
            self.sauve_config()

            ##On lance la fenetre principale de djl dans un processus séparé, puis on ferme la fenetre de configuration
            #self.th_lance_fen = lance_fen_principale()
            #self.th_lance_fen.start()
            #sys.exit()
            self.lance_fen_principale()
        else:
            self.close()

    def sauve_config(self):
        '''Sauve la configuration'''
        self.adresse = self.ligne_adresse.text()
        try:
            self.adresse = self.adresse.replace('\n', '')
        except: pass

        if '/jeux' in self.adresse:
            self.adresse.replace('/jeux', '')

        if self.adresse == '':
            #Aucun répertoire choisi, séléction de la configuration par défaut
            self.adresse = self.home + '/.djl'
            
        self.adresse=unicode(self.adresse).encode('utf-8')
        
        if not os.path.exists(self.adresse):
            try:
                os.mkdir(self.adresse)
            except OSError:
                print i18n.traduc_ascii("Attention, soit le repertoire du jeu est deja existant, soit vous n'avez pas les droits suffisants pour ecrire dessus")

        if not os.path.exists(self.adresse + '/jeux'):
            try:
                #Créé le répertoire où seront installés les jeux:
                os.mkdir(self.adresse + '/jeux')
            except:
                print i18n.traduc_ascii("Attention, le repertoire de jeux n'a put etre cree, vous n'avez peut etre pas les droits necessaires ou le fichier est existant")

        if not os.path.exists(self.adresse + '/etat_jeux'):
            try:
                #Créé le répertoir où seront créé les fichiers etat (pour savoir si les jeux sont installés ou non dans l'interface)
                os.mkdir(self.adresse + '/etat_jeux')
            except:
                print i18n.traduc_ascii("Attention, le repertoire d'etat n'a put etre cree, vous n'avez peut etre pas les droits necessaires ou le fichier est existant")

        #if not os.path.exists(self.adresse + config(info=14)):
            #try:
                #os.mkdir(self.adresse + config(info=14))
            #except:
                #print i18n.traduc_ascii("Erreur, le repertoire de definition n'a put etre cree, vous n'avez peut etre pas les droits necessaires ou le fichier est existant")

        if not os.path.exists(self.adresse + '/raccourcis'):
            try:
                #Créé le répertoir où seront créé les fichiers etat (pour savoir si les jeux sont installés ou non dans l'interface)
                os.mkdir(self.adresse + '/raccourcis')
            except:
                print i18n.traduc_ascii("Erreur, le repertoire des raccourcis n'a put etre cree, vous n'avez peut etre pas les droits necessaires ou le fichier est existant")

        self.navigateur = self.ligne_navigateur.text()
        #try:
        self.navigateur = self.navigateur.replace('\n', '')
        #except:
            #self.navigateur == '/usr/bin/firefox'

        #Si le bouton 'lancer le jeu après installation est coché:
        if self.check_b_lancer_jeu.checkState() == 2:
            self.lance_jeu = 1
        else:
            self.lance_jeu = 0

        if self.check_b_suppr_archive.checkState() == 2:
            self.suppr_arch = 1
        else:
            self.suppr_arch = 0

        if self.check_b_icone_barre.checkState() == 2:
            self.affiche_miniature = 1
        else:
            self.affiche_miniature = 0

        if self.check_b_maj_demarrage.checkState() == 2:
            self.maj_demarrage = 1
        else:
            self.maj_demarrage = 0
            
        if self.check_b_debug.checkState() == 2:
            self.debug = 1
        else:
            self.debug = 0
            
        if self.check_b_composition.checkState() == 2:
            self.composition = 1
        else:
            self.composition = 0
            
        if self.check_b_dependances.checkState() == 2:
            self.dependances = 1
        else:
            self.dependances = 0
            
        if self.chk_conn_irc.checkState() == 2:
            self.irc_demarrage = 1
        else:
            self.irc_demarrage = 0  

        #Ecrit le fichier de configuration si il n'existe pas:
        fichier_cfg = self.home + '/.djl/config'
        if not os.path.exists(fichier_cfg):
            print i18n.traduc_ascii("Le fichier de configuration n'existe pas, il sera cree")
        try:
            langue = getdefaultlocale()[0]
        except:
            langue = 'en_US'
            
        fichier = open(fichier_cfg, 'w')
        fichier.write('telecharger_lancer = ' + str(self.lance_jeu))
        fichier.write('\n')
        fichier.write('telecharger_supprimer = ' + str(self.suppr_arch))
        fichier.write ('\n')
        fichier.write('rep_jeux = ' + str(self.adresse)) # + '/jeux')
        fichier.write ('\n')
        fichier.write('afficher_miniature = ' + str(self.affiche_miniature))
        fichier.write ('\n')
        fichier.write('maj_demarrage = ' + str(self.maj_demarrage))
        fichier.write ('\n')
        fichier.write('onglet = ' + str(self.comboBox.currentIndex()))
        fichier.write ('\n')
        fichier.write('navigateur = ' + str(self.navigateur))
        fichier.write ('\n')
        fichier.write('debug = ' + str(self.debug))
        fichier.write ('\n')
        fichier.write('composition = ' + str(self.composition))
        fichier.write('\n')
        fichier.write('langue = ' + str(langue))
        fichier.write('\n')
        fichier.write('type_gui = ' + self.type_gui)
        fichier.write('\n')
        fichier.write('pseudo = ' + str(self.ligne_pseudo.text())) #+ '-djl')
        fichier.write('\n')
        fichier.write('conn_irc_demarrage = ' + str(self.irc_demarrage))
        fichier.write('\n')
        fichier.write('fond_irc = ' + str(self.couleur_irc.currentIndex()))
        fichier.write('\n')
        fichier.write('taille_police = ' + str(self.taille_police.value()))
        fichier.write('\n')
        fichier.write('canaux_IRC = ' + str(self.ligne_canaux.text()))
        fichier.write('\n')
        fichier.write('dependances = ' + str(self.dependances))
        fichier.close()

        print _('Fichier de configuration ecrit:'), str(self.adresse)

    def setupUi(self, Dialog):
        '''Envoi le dessin de l'interface'''
        Dialog.setObjectName("Dialog")
        x, y = 470, 505
        Dialog.resize(QtCore.QSize(QtCore.QRect(200,200,x,y).size()).expandedTo(Dialog.minimumSizeHint()))

        Dialog.setMinimumSize(QtCore.QSize(x,y))
        Dialog.setMaximumSize(QtCore.QSize(x,y))

        icone = QtGui.QIcon(os.getcwd() + '/icone.png')
        Dialog.setWindowIcon(icone)

        #Force la taille de la police à 10:
        self.font = QtGui.QFont()
        self.font.setPointSize(9)

        self.centralwidget = QtGui.QWidget(Dialog)
        self.centralwidget.setObjectName("centralwidget")
        
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0,0,x,y-30))
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        
        #Défini l'ordre des onglets:
        self.tabWidget.addTab(self.tab,"")
        self.tabWidget.addTab(self.tab_2,"")

        #Onglet par défaut:
        self.tabWidget.setCurrentIndex(0)

        icone = QtGui.QIcon(dossier_racine + '/icone.png')
        self.tabWidget.setTabIcon(0, icone)
        icone = QtGui.QIcon(dossier_racine + '/res/irc_crystal.png')
        self.tabWidget.setTabIcon(1, icone)
        
        self.label = QtGui.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(0,10,460,32))
        self.label.setObjectName("label")
        self.label.setFont(self.font)

        self.ligne_adresse = QtGui.QLineEdit(self.tab)
        self.ligne_adresse.setGeometry(QtCore.QRect(0,70,340,28))
        self.ligne_adresse.setObjectName("ligne_adresse")

        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(0,50,220,21))
        self.label_2.setObjectName("label_2")

        self.b_parcourir = QtGui.QPushButton(self.tab)
        self.b_parcourir.setGeometry(QtCore.QRect(340,70,111,27))
        self.b_parcourir.setObjectName("b_parcourir")

        self.label_3 = QtGui.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(0,103,110,21))
        self.label_3.setObjectName("label_3")

        self.ligne_navigateur = QtGui.QLineEdit(self.tab)
        self.ligne_navigateur.setGeometry(QtCore.QRect(110,100,230,28))
        self.ligne_navigateur.setObjectName("ligne_navigateur")

        self.b_parcourir_nav = QtGui.QPushButton(self.tab)
        self.b_parcourir_nav.setGeometry(QtCore.QRect(340,100,111,27))
        self.b_parcourir_nav.setObjectName("b_parcourir_nav")
        
        ###
        #Choix onglet par defaut
        self.label_onglet_def = QtGui.QLabel(self.tab)
        self.label_onglet_def.setGeometry(QtCore.QRect(0,130,120,28))
        self.label_onglet_def.setObjectName("label_onglet_def")
        
        self.comboBox = QtGui.QComboBox(self.tab)
        self.comboBox.setGeometry(QtCore.QRect(120,130,130,28))
        self.comboBox.setObjectName("comboBox")
        
        ###
        
        ###
        #Choix taille police
        self.label_taille_police = QtGui.QLabel(self.tab)
        self.label_taille_police.setGeometry(QtCore.QRect(0,160,120,28))
        self.label_taille_police.setObjectName("label_taille_police")
        
        self.taille_police = QtGui.QSpinBox(self.tab)
        self.taille_police.setGeometry(QtCore.QRect(120,160,120,28))
        self.taille_police.setObjectName("label_taille_police")
        
        self.taille_police.setMinimum(8)
        self.taille_police.setMaximum(12)
        ###
        l = 450
        self.check_b_suppr_archive = QtGui.QCheckBox(self.tab)
        self.check_b_suppr_archive.setGeometry(QtCore.QRect(0,190,l,23))
        self.check_b_suppr_archive.setObjectName("check_b_suppr_archive")

        self.check_b_lancer_jeu = QtGui.QCheckBox(self.tab)
        self.check_b_lancer_jeu.setGeometry(QtCore.QRect(0,220,l,23))
        self.check_b_lancer_jeu.setObjectName("check_b_lancer_jeu")

        self.check_b_icone_barre = QtGui.QCheckBox(self.tab)
        self.check_b_icone_barre.setGeometry(QtCore.QRect(0,250,l,23))
        self.check_b_icone_barre.setObjectName("check_b_lancer_jeu")

        self.check_b_maj_demarrage = QtGui.QCheckBox(self.tab)
        self.check_b_maj_demarrage.setGeometry(QtCore.QRect(0,280,l,23))
        self.check_b_maj_demarrage.setObjectName("check_b_maj_demarrage")
        
        self.check_b_debug = QtGui.QCheckBox(self.tab)
        self.check_b_debug.setGeometry(QtCore.QRect(0,310,l,23))
        self.check_b_debug.setObjectName("check_b_debug")
        
        self.check_b_composition = QtGui.QCheckBox(self.tab)
        self.check_b_composition.setGeometry(QtCore.QRect(0,340,l,35))
        self.check_b_composition.setObjectName("check_b_composition")
        
        self.check_b_dependances = QtGui.QCheckBox(self.tab)
        self.check_b_dependances.setGeometry(QtCore.QRect(0,370,l,35))
        self.check_b_dependances.setObjectName("check_b_dependances")

        self.b_raccourci = QtGui.QPushButton(self.tab)
        self.b_raccourci.setGeometry(QtCore.QRect(25,410,400,27))
        self.b_raccourci.setObjectName("b_raccourci")
        #self.b_raccourci.hide()

        self.b_valider = QtGui.QPushButton(self.centralwidget)
        self.b_valider.setGeometry(QtCore.QRect(110,475,106,27))
        self.b_valider.setObjectName("b_valider")

        self.b_fermer = QtGui.QPushButton(self.centralwidget)
        self.b_fermer.setGeometry(QtCore.QRect(250,475,106,27))
        self.b_fermer.setObjectName("b_fermer")
        
        #Partie configuration IRC/
        self.ligne_pseudo = QtGui.QLineEdit(self.tab_2)
        self.ligne_pseudo.setGeometry(QtCore.QRect(160,40,191,28))
        self.ligne_pseudo.setObjectName("ligne_pseudo")

        self.label_irc = QtGui.QLabel(self.tab_2)
        self.label_irc.setGeometry(QtCore.QRect(20,40,100,31))
        self.label_irc.setObjectName("label_irc")

        self.label_2_irc = QtGui.QLabel(self.tab_2)
        self.label_2_irc.setGeometry(QtCore.QRect(20,70,130,31))
        self.label_2_irc.setObjectName("label_2_irc")

        self.couleur_irc = QtGui.QComboBox(self.tab_2)
        self.couleur_irc.setGeometry(QtCore.QRect(160,70,191,28))
        self.couleur_irc.setObjectName("couleur_irc")

        self.chk_conn_irc = QtGui.QCheckBox(self.tab_2)
        self.chk_conn_irc.setGeometry(QtCore.QRect(20,10,330,23))
        #self.chk_conn_irc.setChecked(True)
        self.chk_conn_irc.setTristate(False)
        self.chk_conn_irc.setObjectName("chk_conn_irc")
        
        ##Partie canaux IRC
        self.label_canaux = QtGui.QLabel(self.tab_2)
        self.label_canaux.setGeometry(QtCore.QRect(20,100,430,31))
        self.label_canaux.setObjectName("label_canaux")
        
        self.ligne_canaux = QtGui.QLineEdit(self.tab_2)
        self.ligne_canaux.setGeometry(QtCore.QRect(20,125,430,28))
        self.ligne_canaux.setObjectName("ligne_canaux")
        ##

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        '''Ajoute le texte dans l'interface'''
        Dialog.setWindowTitle("Configuration")
        fichier_cfg = self.home + '/.djl/config'

        if not os.path.exists(fichier_cfg):
            self.label.setText(i18n.traduc("Ceci est le premier demarrage de djl, vous pouvez le configurer maintenant \n"
            " ou passer cette etape pour vous en tenir a la configuration par defaut."))
            self.ligne_pseudo.setText(str(os.environ["USER"]).capitalize())
        else:
            self.label.setText(i18n.traduc("Ceci est le menu de configuration de djl. \n"
        "Certaines actions necessiteront le redemarrage du logiciel."))

        self.label_onglet_def.setText(i18n.traduc("Onglet par defaut") + ":")

        self.label_2.setText(i18n.traduc("Repertoire d'installation des jeux:"))
        self.label_3.setText(i18n.traduc("Navigateur internet:"))
        self.b_parcourir.setText(i18n.traduc("Parcourir..."))
        self.b_parcourir_nav.setText(i18n.traduc("Parcourir..."))
        self.check_b_suppr_archive.setText(i18n.traduc("Supprimer les archives des jeux apres installation."))
        self.check_b_lancer_jeu.setText(i18n.traduc("Lancer les jeux apres installation."))
        self.check_b_icone_barre.setText(i18n.traduc("Iconifier djl dans la barre a miniature. (necessite redemarrage)"))
        self.check_b_maj_demarrage.setText(i18n.traduc("Verifier la mise a jour de djl au demarrage."))
        self.check_b_debug.setText(i18n.traduc("Afficher la sortie des jeux a leur lancement."))
        self.check_b_composition.setText(i18n.traduc("Lancer les jeux dans un serveur graphique separe\n(Permet d'eviter les problemes lies a l'utilisation de Compiz"))
        self.check_b_dependances.setText(i18n.traduc("Installer automatiquement les dependances manquantes."))
        self.b_valider.setText(i18n.traduc("Valider"))
        self.b_fermer.setText(i18n.traduc("Fermer"))
        
        self.label_taille_police.setText(i18n.traduc("Taille des polices:"))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), i18n.traduc("djl"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), i18n.traduc("IRC"))
    
        #Partie config IRC:
        self.label_irc.setText(i18n.traduc("Pseudo:"))
        self.label_2_irc.setText(i18n.traduc("Couleur de fond:"))
        self.label_canaux.setText(i18n.traduc("Canaux a utiliser (sur irc.freenode.net"))
        self.couleur_irc.addItem(i18n.traduc("Blanc"))
        self.couleur_irc.addItem(i18n.traduc("Noir"))
        self.chk_conn_irc.setText(i18n.traduc("Se connecter au demarrage"))

        liste_onglets = (i18n.traduc("Actualites"), i18n.traduc("Jeux"), i18n.traduc("Depot"), i18n.traduc("IRC"))
        for i in range(len(liste_onglets)):
            #print liste_onglets[i]
            self.comboBox.addItem(liste_onglets[i])
            