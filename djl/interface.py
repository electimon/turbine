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

'''Dessin de l'interface principale'''

from PyQt4 import QtGui, QtCore
import os #, sys
from variables import variables
from config import config
import i18n

#Quand on demande la version de djl:
def version():
    return "1.2.20"

dossier_racine = os.getcwd()

class v:
    testtemp = 0
def test():
    v.testtemp += 1
    print v.testtemp

class info_box(QtGui.QWidget):
    def __init__(self, texte="", titre="Attention"):
        '''Affiche une boite de dialogue avec le texte avec la police choisie dans la config et un simple bouton "Fermer'''
        QtGui.QMessageBox.__init__(self)
        
        texte=texte.replace("\n", "<br>")
        
        #texte = _(texte)
        titre = _(titre)
        taille_police = str(config(info=15)+2)
        
        #temp:
        texte = texte
        
        q_texte = QtCore.QString("<font style=\"font-size: "+ taille_police +"px;\">"+texte+"</font>")
        QtGui.QMessageBox.information(self, titre, q_texte, i18n.traduc("Fermer"))

class Onglets_djl(object):
    def setupUi(self, MainWindow):
        '''Dessin de l'interface de la fenêtre principale'''
        
        MainWindow.setObjectName("MainWindow")
        
        self.font = QtGui.QFont()
        #Défini la taille de police général de djl (la plus petite)
        self.font.setPointSize(config(info=15))
        self.setFont(self.font)

        self.font2 = QtGui.QFont()
        #Défini la taille de police (moyenne) pour certains éléments (comme la liste des jeux)
        self.font2.setPointSize(config(info=15)+2)
        
        self.font3 = QtGui.QFont()
        #Défini la taille (la plus grande) de police pour certains éléments (Comme le nom du jeu en dépôt)
        self.font3.setPointSize(config(info=15)+6)

        if config(info=10)=='1': #Future, enlever la condition pour djl 1.2.13
            x, y = 780, 680
            self.centralwidget = QtGui.QWidget(MainWindow)
            self.centralwidget.setObjectName("centralwidget")
            MainWindow.setCentralWidget(self.centralwidget)
    
            self.tabWidget = QtGui.QTabWidget(self.centralwidget)
            #self.tabWidget = QtGui.QTabWidget(self) #<<<
            
            #self.tabWidget.setGeometry(QtCore.QRect(0,0,x,y-23))
            self.tabWidget.setObjectName("tabWidget")
    
            self.tab = QtGui.QWidget() #Liste des jeux
            self.tab.setObjectName("tab")
    
            self.tab_2 = QtGui.QWidget() #Dépot
            self.tab_2.setObjectName("tab_2")
    
            self.tab_3 = QtGui.QWidget() #IRC
            self.tab_3.setObjectName("tab_3")
    
            self.tab_4 = QtGui.QWidget() #Actu
            self.tab_4.setObjectName("tab_4")
            
            self.tab_5 = QtGui.QWidget() #Gestionnaire de modules
            self.tab_5.setObjectName("tab_5")
            
            ###
            self.gridlayout = QtGui.QGridLayout(self.centralwidget)
            self.gridlayout.setObjectName("gridlayout")
            
            self.gridlayout.addWidget(self.tabWidget,0,0)
    
            self.gridlayout_1 = QtGui.QGridLayout(self.tab)
            self.gridlayout_1.setObjectName("gridlayout1")
            
            #Défini l'ordre des onglets:
            self.tabWidget.addTab(self.tab_4,"")
            self.tabWidget.addTab(self.tab,"")
            self.tabWidget.addTab(self.tab_2,"")
            self.tabWidget.addTab(self.tab_3,"")
            self.tabWidget.addTab(self.tab_5,"")
    
            ##################################
        else:
            x, y = 350, 640

        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,x,y).size()).expandedTo(MainWindow.minimumSizeHint()))
        icone = QtGui.QIcon((os.getcwd() + '/icone.png'))
        MainWindow.setWindowIcon(icone)


        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
        #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,x,26))
        self.menubar.setObjectName("menubar")
        self.menubar.setFont(self.font)

        MainWindow.setMenuBar(self.menubar)

        ##################################################
        #Liste des jeux:
        #print '>>>'+config(info=10)
        
        #Futur, enlever la clause pour djl 1.2.13
        if config(info=10)=='0': #Si c'est l'interface simple
            self.listWidget = QtGui.QListWidget(self)
            #self.recherche_jeu = QtGui.QLineEdit(self)
            self.setCentralWidget(self.listWidget)
            
        ##if config(info=10)=='1': #Si c'est l'interface complète
        else:
            #self.creer_liste(filtre='0')
            self.listWidget = QtGui.QListWidget(self.tab) # Liste des jeux de l'onglet "Jeux"
            self.recherche_jeu = QtGui.QLineEdit(self.tab) #Barre de recherche des jeux
        
            self.gridlayout_1.addWidget(self.recherche_jeu,0,0)
            self.gridlayout_1.addWidget(self.listWidget,1,0)

        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setFont(self.font2)
        #self.listWidget.setGeometry(QtCore.QRect(0,0,x-10,y-55))
        self.listWidget.setBaseSize(QtCore.QSize(0,0))
        #Défini le taille des icones:
        self.listWidget.setIconSize(QtCore.QSize(32,32))
        self.listWidget.setGridSize(QtCore.QSize(34,34))
        self.listWidget.setObjectName("listWidget")
        #self.listWidget.contextMenuPolicy = 1
        self.listWidget.contextMenuEvent = self.contextMenuEvent

        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        self.menuMenu.setFont(self.font)

        self.menuAide = QtGui.QMenu(self.menubar)
        self.menuAide.setObjectName("menuAide")
        self.menuAide.setFont(self.font)

        self.actionAjouter_jeu = QtGui.QAction(MainWindow)
        self.actionAjouter_jeu.setObjectName("actionAjouter_jeu")

        self.action_change_ui = QtGui.QAction(MainWindow)
        self.action_change_ui.setObjectName("action_change_ui")

        self.action_Import_desk = QtGui.QAction(MainWindow)
        self.action_Import_desk.setObjectName("action_Import_desk")

        #self.actionSupprimer_desk = QtGui.QAction(MainWindow)
        #self.actionSupprimer_desk.setObjectName("actionSupprimer_desk")
        #self.actionSupprimer_desk.setEnabled(False)

        self.actionConfig = QtGui.QAction(MainWindow)
        self.actionConfig.setObjectName("actionConfig")

        self.actionRedem = QtGui.QAction(MainWindow)
        self.actionRedem.setObjectName("actionRedem")

        self.action_maj = QtGui.QAction(MainWindow)
        self.action_maj.setObjectName("action_maj")

        self.actionQuitter = QtGui.QAction(MainWindow)
        self.actionQuitter.setObjectName("actionQuitter")

        self.action_Infos_sys = QtGui.QAction(MainWindow)
        self.action_Infos_sys.setObjectName("action_Infos_sys")

        self.action_historique = QtGui.QAction(MainWindow)
        self.action_historique.setObjectName("action_historique")

        self.action_journal = QtGui.QAction(MainWindow)
        self.action_journal.setObjectName("action_journal")
        
        self.action_sortie_jeu = QtGui.QAction(MainWindow)
        self.action_sortie_jeu.setObjectName("action_sortie_jeu")
        
        self.action_rapport = QtGui.QAction(MainWindow)
        self.action_rapport.setObjectName("action_rapport")

        self.action_Apropos = QtGui.QAction(MainWindow)
        self.action_Apropos.setObjectName("action_Apropos")
        
        self.actionInstallWine = QtGui.QAction(MainWindow)
        self.actionInstallWine.setObjectName("actionInstallWine")
        
        #self.action_args = QtGui.QAction(MainWindow)
        #self.action_args.setObjectName("action_args")
        #self.action_args.setEnabled(False)

        self.menuMenu.addAction(self.action_change_ui)
        self.menuMenu.addAction(self.actionAjouter_jeu)
        self.menuMenu.addAction(self.action_Import_desk)
        #self.menuMenu.addAction(self.actionSupprimer_desk)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionInstallWine)
        #self.menuMenu.addAction(self.action_args)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionConfig)
        #Ajout du menu pour le choix de la langue:
        #self.menuLang = self.menuMenu.addMenu(self.tr(i18n.traduc("Langue")))
        self.menuLang = QtGui.QMenu(self.menuMenu)
        self.menuLang.setFont(self.font)
        self.menuMenu.addMenu(self.menuLang)
        self.menuMenu.addAction(self.action_maj)
        self.menuMenu.addAction(self.actionRedem)
        self.menuMenu.addAction(self.actionQuitter)
        self.menubar.addAction(self.menuMenu.menuAction())
         
        ###Menu de la langue:
        self.action_FR = QtGui.QAction(MainWindow)
        self.action_FR.setObjectName("action_FR")
        
        self.action_EN = QtGui.QAction(MainWindow)
        self.action_EN.setObjectName("action_EN")

        self.action_HU = QtGui.QAction(MainWindow)
        self.action_HU.setObjectName("action_HU")
        
        self.action_GL = QtGui.QAction(MainWindow)
        self.action_GL.setObjectName("action_GL") 
        
        self.action_RU = QtGui.QAction(MainWindow)
        self.action_RU.setObjectName("action_RU")
        
        self.action_SV = QtGui.QAction(MainWindow)
        self.action_SV.setObjectName("action_SV")
        
        self.action_IT = QtGui.QAction(MainWindow)
        self.action_IT.setObjectName("action_IT")
        
        self.action_ES = QtGui.QAction(MainWindow)
        self.action_ES.setObjectName("action_ES")
        
        self.action_DE = QtGui.QAction(MainWindow)
        self.action_DE.setObjectName("action_DE")
        
        self.action_PL = QtGui.QAction(MainWindow)
        self.action_PL.setObjectName("action_PL")
        
        self.action_PT = QtGui.QAction(MainWindow)
        self.action_PT.setObjectName("action_PT")

        self.menuLang.addAction(self.action_DE)
        self.menuLang.addAction(self.action_EN)
        self.menuLang.addAction(self.action_ES)
        self.menuLang.addAction(self.action_FR)
        self.menuLang.addAction(self.action_GL)
        self.menuLang.addAction(self.action_HU)
        self.menuLang.addAction(self.action_IT)
        self.menuLang.addAction(self.action_RU)
        self.menuLang.addAction(self.action_PL)
        self.menuLang.addAction(self.action_PT)
        self.menuLang.addAction(self.action_SV)

        ###

        self.menuDepot = QtGui.QMenu(self.menubar)
        self.menuDepot.setObjectName("menuDepot")
        self.menuDepot.setFont(self.font)

        self.action_creer_def = QtGui.QAction(MainWindow)
        self.action_creer_def.setObjectName("action_creer_def")
        
        self.action_dependances = QtGui.QAction(MainWindow)
        self.action_dependances.setObjectName("action_dependances")
        
        self.menuDepot.addAction(self.action_dependances)
        self.menuDepot.addAction(self.action_creer_def)
        
        self.menubar.addAction(self.menuDepot.menuAction())
        #self.menubar.addAction(self.menuDepot.menuAction())

        #self.menuDepot.addSeparator()

        #self.actionFermer = QtGui.QAction(MainWindow)
        #self.actionFermer.setObjectName("actionFermer")
        #self.menuDepot.addAction(self.actionFermer)
        #self.menubar.addAction(self.menuDepot.menuAction())
        
        self.menuAide.addAction(self.action_Infos_sys)
        self.menuAide.addAction(self.action_historique)
        self.menuAide.addAction(self.action_journal)
        self.menuAide.addAction(self.action_sortie_jeu)
        self.menuAide.addAction(self.action_rapport)
        self.menuAide.addAction(self.action_Apropos)
        self.menubar.addAction(self.menuAide.menuAction())
        
        self.action_sortie_jeu.setEnabled(False)
        ##################################################

        ##################################################

        self.retranslateUi(MainWindow)
        self.connexions_o()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        '''Affiche le texte de l'interface principale'''        
        #MainWindow.setWindowTitle(i18n.traduc("Depot"))
        MainWindow.setWindowTitle(i18n.traduc("djl " + version()))
        self.actionQuitter.setText(i18n.traduc("Quitter") + "\tCtrl+Q")

        self.action_creer_def.setText(i18n.traduc("Creer une nouvelle entree"))
        self.action_dependances.setText(i18n.traduc("Gestionnaire des librairies"))
        
        #self.action_args.setText(i18n.traduc("Arguments de lancement"))
        self.menuDepot.setTitle(i18n.traduc("Depot"))
        self.menuLang.setTitle(i18n.traduc("Langue"))

        if config(info=10)=='1': #Future, à enlever pour djl 1.2.13
            #Onglets:
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), i18n.traduc("Jeux"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), i18n.traduc("Depot"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), i18n.traduc("IRC"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), i18n.traduc("Actualites"))
            #self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), i18n.traduc("Communaute"))

        self.listWidget.clear()
        self.menuMenu.setTitle(i18n.traduc("Menu"))
        self.actionAjouter_jeu.setText(i18n.traduc("Ajouter un raccourci vers un jeu installe sur le systeme"))
        if config(info=10) == '1':
            self.action_change_ui.setText(i18n.traduc("Passer a l'interface simple"))
        if config(info=10) == '0':
            self.action_change_ui.setText(i18n.traduc("Passer a l'interface etendue"))

        self.action_Import_desk.setText(i18n.traduc("Importer un raccourci"))
        #self.actionSupprimer_desk.setText(i18n.traduc("Supprimer le raccourci"))
        self.actionInstallWine.setText(i18n.traduc("Ajouter un jeu Windows avec Wine"))
        self.actionConfig.setText(i18n.traduc("Configuration"))
        
        self.action_FR.setText(i18n.traduc("Francais"))
        self.action_GL.setText(i18n.traduc("Galego"))
        self.action_EN.setText(i18n.traduc("English"))
        self.action_HU.setText(i18n.traduc("Hungarian"))
        self.action_RU.setText(i18n.traduc("Русский"))
        self.action_SV.setText(i18n.traduc("Svenska"))
        self.action_IT.setText(i18n.traduc("Italiano"))
        self.action_ES.setText(i18n.traduc("Español"))
        self.action_DE.setText(i18n.traduc("Deutsch"))
        self.action_PL.setText(i18n.traduc("Polski"))
        self.action_PT.setText(i18n.traduc("Português"))

        self.action_maj.setText(i18n.traduc("Mise a jour de djl"))
        self.actionRedem.setText(i18n.traduc("Redemarrer djl"))

        self.menuAide.setTitle(i18n.traduc("Informations"))
        self.action_Infos_sys.setText(i18n.traduc("Informations systeme"))
        self.action_historique.setText(i18n.traduc("Consulter le journal des modifications de djl"))
        self.action_journal.setText(i18n.traduc("Consulter l'historique"))
        self.action_sortie_jeu.setText(i18n.traduc("Consulter la sortie des jeux"))
        self.action_rapport.setText(i18n.traduc("Rapporter une anomalie ou une suggestion..."))
        self.action_Apropos.setText(i18n.traduc("A propos..."))
        
        #Si le répertoire contenant les icones des menus existe, on les affiches:
        if os.path.exists(dossier_racine + '/res') == True:
            icone = QtGui.QIcon(dossier_racine + '/res/quitter.png')
            self.actionQuitter.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/information.png')
            self.action_Infos_sys.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/importer.png')
            self.action_Import_desk.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/configuration.png')
            self.actionConfig.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/a_propos.png')
            self.action_Apropos.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/ajouter.png')
            self.actionAjouter_jeu.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/configure_oxygen.png')
            self.action_maj.setIcon(icone)
            
            icone = QtGui.QIcon(dossier_racine + '/res/winehq.png')
            self.actionInstallWine.setIcon(icone)
            #icone = QtGui.QIcon(dossier_racine + '/res/arg_oxygen.png')
            #self.action_args.setIcon(icone)
            
            icone = QtGui.QIcon(dossier_racine + '/res/echange_ui_oxygen.png')
            self.action_change_ui.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/redemarre_oxygen.png')
            self.actionRedem.setIcon(icone)
            #icone = QtGui.QIcon(dossier_racine + '/res/supprimer_oxygen.png')
            #self.actionSupprimer_desk.setIcon(icone)
    
            icone = QtGui.QIcon(dossier_racine + '/res/msg_oxygen.png')
            self.action_rapport.setIcon(icone)
            
            icone = QtGui.QIcon(dossier_racine + '/res/locale_oxygen.png')
            self.menuLang.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/france.png')
            self.action_FR.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/en.png')
            self.action_EN.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/hu.png')
            self.action_HU.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/galicia.png')
            self.action_GL.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/ru.png')
            self.action_RU.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/sweden.png')
            self.action_SV.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/italy.png')
            self.action_IT.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/espagne.png')
            self.action_ES.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/de.png')
            self.action_DE.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/poland.png')
            self.action_PL.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/drapeaux/portugal.png')
            self.action_PT.setIcon(icone)
            
            icone = QtGui.QIcon(dossier_racine + '/res/txt_oxygen.png')
            self.action_historique.setIcon(icone)
            self.action_journal.setIcon(icone)
            self.action_sortie_jeu.setIcon(icone)
            
            icone = QtGui.QIcon(dossier_racine + '/res/ajouter.png')
            self.action_creer_def.setIcon(icone)
            icone = QtGui.QIcon(dossier_racine + '/res/configuration.png')
            self.action_dependances.setIcon(icone)

            #Affiche les icones dans les onglets:
            if config(info=10) == '1':
                icone = QtGui.QIcon(dossier_racine + '/res/actus.png')
                self.tabWidget.setTabIcon(0, icone)
                icone = QtGui.QIcon(dossier_racine + '/res/jeux_oxygen.png')
                self.tabWidget.setTabIcon(1, icone)
                icone = QtGui.QIcon(dossier_racine + '/res/importer.png')
                self.tabWidget.setTabIcon(2, icone)
                icone = QtGui.QIcon(dossier_racine + '/res/irc_crystal.png')
                self.tabWidget.setTabIcon(3, icone)
                
    def connexions_o(self):
        '''Connexion des objets qt vers les fonctions de djl.'''
        self.action_change_ui.connect(self.action_change_ui, QtCore.SIGNAL("triggered()"), self.change_ui)
        self.action_maj.connect(self.action_maj, QtCore.SIGNAL("triggered()"), self.trouve_serveur_maj)
        self.actionAjouter_jeu.connect(self.actionAjouter_jeu, QtCore.SIGNAL("triggered()"), self.ajout_jeu_)
        self.action_Import_desk.connect(self.action_Import_desk, QtCore.SIGNAL("triggered()"), self.import_desk)
        #self.actionSupprimer_desk.connect(self.actionSupprimer_desk, QtCore.SIGNAL("triggered()"), self.suppr_desk)
        self.actionInstallWine.connect(self.actionInstallWine, QtCore.SIGNAL("triggered()"), self.fonc_wine)
        self.actionConfig.connect(self.actionConfig, QtCore.SIGNAL("triggered()"), self.configuration)
        self.actionRedem.connect(self.actionRedem, QtCore.SIGNAL("triggered()"), self.redemarre)
        self.actionQuitter.connect(self.actionQuitter, QtCore.SIGNAL("triggered()"), self.quitte)
        
        self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.lance)
        if self.int_etendue:
            self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.info)
            self.listWidget.connect(self.listWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.info)
        
        self.action_Infos_sys.connect(self.action_Infos_sys, QtCore.SIGNAL("triggered()"), self.infos_sys)
        self.action_historique.connect(self.action_historique, QtCore.SIGNAL("triggered()"), self.affiche_historique)
        self.action_journal.connect(self.action_journal, QtCore.SIGNAL("triggered()"), self.affiche_journal)
        self.action_sortie_jeu.connect(self.action_sortie_jeu, QtCore.SIGNAL("triggered()"), self.affiche_sortie_jeu)
        self.action_rapport.connect(self.action_rapport, QtCore.SIGNAL("triggered()"), self.rapport)
        self.action_Apropos.connect(self.action_Apropos, QtCore.SIGNAL("triggered()"), self.a_propos)
        
        self.action_FR.connect(self.action_FR, QtCore.SIGNAL("triggered()"), self.langue_fr)
        self.action_EN.connect(self.action_EN, QtCore.SIGNAL("triggered()"), self.langue_en)
        self.action_HU.connect(self.action_HU, QtCore.SIGNAL("triggered()"), self.langue_hu)
        self.action_GL.connect(self.action_GL, QtCore.SIGNAL("triggered()"), self.langue_gl)
        self.action_RU.connect(self.action_RU, QtCore.SIGNAL("triggered()"), self.langue_ru)
        self.action_SV.connect(self.action_SV, QtCore.SIGNAL("triggered()"), self.langue_sv)
        self.action_IT.connect(self.action_IT, QtCore.SIGNAL("triggered()"), self.langue_it)
        self.action_ES.connect(self.action_ES, QtCore.SIGNAL("triggered()"), self.langue_es)
        self.action_DE.connect(self.action_DE, QtCore.SIGNAL("triggered()"), self.langue_de)
        self.action_PL.connect(self.action_PL, QtCore.SIGNAL("triggered()"), self.langue_pl)
        self.action_PT.connect(self.action_PT, QtCore.SIGNAL("triggered()"), self.langue_pt)
        
        self.action_creer_def.connect(self.action_creer_def, QtCore.SIGNAL("triggered()"), self.crer_entree)
        self.action_dependances.connect(self.action_dependances, QtCore.SIGNAL("triggered()"), self.fenetre_dependances)

        #Raccourcis clavier:
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.quitte)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+I"), self, self.affiche_sortie_jeu)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_1), self, self.chg_rss)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_2), self, self.chg_jeux)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_3), self, self.chg_depot)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_4), self, self.chg_irc)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_5), self, self.chg_modules)
        
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_Left), self, self.chg_onglet_g)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_Right), self, self.chg_onglet_d)

        if config(info=10) == '1':
            #On change le raccourcis avec la touche entrée suivant que l'on soit sur la liste des jeux ou le canal IRC
            self.tabWidget.connect(self.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.ch_tab)

            #Appuyer sur la touche entrée dans la fenêtre principale reviendra soit à envoyer un message sur IRC, soit à lancer un jeu
            QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self, self.entree)
            QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter), self, self.entree)
            QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.echappement)
            
            #Barre de texte pour rechercher un jeu dans la liste (liste principale)
            self.recherche_jeu.connect(self.recherche_jeu, QtCore.SIGNAL("textEdited(const QString &)"), self.cherche_jeu)

    def chg_rss(self):
        '''Passe à l'onglet du flux RSS dans l'inteface'''
        self.tabWidget.setCurrentIndex(0)
        
    def chg_jeux(self):
        '''Passe à l'onglet de la liste des jeux dans l'inteface'''
        self.tabWidget.setCurrentIndex(1)
    
    def chg_depot(self):
        '''Passe à l'onglet du dépôt dans l'inteface'''
        self.tabWidget.setCurrentIndex(2)
    
    def chg_irc(self):
        '''Passe à l'onglet du client IRC dans l'inteface'''
        self.tabWidget.setCurrentIndex(3)
    
    def chg_modules(self):
        '''Passe à l'onglet des modules dans l'inteface'''
        self.tabWidget.setCurrentIndex(4)

    def chg_onglet_g(self):
        '''Passe à l'onglet de gauche'''
        if self.tabWidget.currentIndex() == 0:
            self.tabWidget.setCurrentIndex((self.tabWidget.count()-1))
        else:
            self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()-1)
    
    def chg_onglet_d(self):
        '''Passe à l'onglet de droite'''        
        if (self.tabWidget.currentIndex()+1) == self.tabWidget.count():
            self.tabWidget.setCurrentIndex(0)
        else:
            self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()+1)

    def ch_tab(self):
        '''Quand on change d'onglet...'''
        if self.tabWidget.currentIndex() == 2: #Dépôt...
            if self.connecte_ws == 0: #Si on est pas connecté au WS, on le fait maintenant
                #self.Thread_depot()
                self.listWidget.clear()
                if int(config(info=3)) == 1 and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
                    self.menu_lance.clear()
                #Créé un nouvelle liste des jeux installés
                self.liste_jeux_installe()
                #Pareil pour les raccourcis
                self.liste_raccourcis()
            try:
                self.maj_description()
            except AttributeError:
                pass
            self.widget_liste_jeux.setFocus() #Donne le focus à la liste des jeux
            
        elif self.tabWidget.currentIndex() == 3: #IRC.
            #Si on affiche le canal IRC, on remet le titre "normal" qui a put être modifié avec l'arrivée d'un nouveau message
            self.clignote_IRC = 0
            self.tabWidget.setTabIcon(3, QtGui.QIcon(dossier_racine + '/res/irc_crystal.png'))
            if int(config(info=3)) == 1 and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
                self.tray.setIcon(QtGui.QIcon(dossier_racine + '/icone.png'))
            self.tabWidget.setTabText(3, i18n.traduc("IRC"))

            #On donne le focus à la barre de texte pour envoyer le message:
            self.line_Edit_chat.setFocus()
            
        elif self.tabWidget.currentIndex() == 1: #Liste des jeux principale.
            #Donne le focus à la barre de recherche.
            self.recherche_jeu.setFocus()
        elif self.tabWidget.currentIndex() == 4: #Modules
            self.chTabMod()

    def entree(self):
        '''Appuyer sur la touche entrée dans la fenêtre principale reviendra soit à envoyer un message sur IRC, soit à lancer un jeu
        L'action change en fonction de l'onglet actuellement utilisé'''
        #print self.tabWidget.currentIndex()
        if self.tabWidget.currentIndex() == 1: #liste principale
            self.lance()
        elif self.tabWidget.currentIndex() == 2: #depot
            #self.maj_description()
            self.installer_jouer()
        elif self.tabWidget.currentIndex() == 3: #irc
            self.envoi_irc()
        elif self.tabWidget.currentIndex() == 0: #rss
            self.navigateur_RSS()
        elif self.tabWidget.currentIndex() == 4: #Modules
            self.EntreeMod()

    def echappement(self):
        '''Quand on appui sur la touche Echap dans l'interface principale...'''
        if self.tabWidget.currentIndex() == 1: #liste principale
            self.recherche_jeu.setText("") #Remet à zero la barre de recherche
            self.listWidget.setCurrentRow(0)
        elif self.tabWidget.currentIndex() == 4:
            self.EchapMod()

    def contextMenuEvent(self, event):
        '''Affiche le menu contextuel'''
        if not self.int_etendue: #Régression, temp
            event.ignore() #Régression, temp
            return #Régression, temp
        
        var_ok = 0
        #Si le jeu actuellement selectionné est un raccourci...
        if '.desktop' in self.nom_jeu_pr():
            raccourci = 1
        else:
            raccourci = 0

        #print '>>',  str(self.listWidget.currentRow())
        if self.int_etendue: #Si c'est l'interface étendue...
            if self.listWidget.currentRow() == -1: #Si aucun jeu n'est séléctionné, on ignore
                event.ignore()
                return
            if self.tabWidget.currentIndex() == 1:
                var_ok = 1
            else:
                event.ignore()
                return
        
        if not self.int_etendue or var_ok == 1: #Si c'est l'interface simple...
            if var_ok == 0:
                if self.listWidget.currentRow() == -1: #Si aucun jeu n'est séléctionné, on ignore
                    event.ignore()
                    return
                    
            menu = QtGui.QMenu(self)
            menu.setFont(self.font)
            
            self.act_lance = QtGui.QAction(_((i18n.traduc("Jouer"))), self)
            self.act_lance.connect(self.act_lance, QtCore.SIGNAL("triggered()"), self.lance)
            menu.addAction(self.act_lance)
            icone = QtGui.QIcon(dossier_racine + '/res/jeux_oxygen.png')
            self.act_lance.setIcon(icone)
            
            if self.connecte_ws == 1 or raccourci == 1:
                self.act_infos = QtGui.QAction(_((i18n.traduc("Informations"))), self)
                self.act_infos.connect(self.act_infos, QtCore.SIGNAL("triggered()"), self.boite_infos)
                icone = QtGui.QIcon(dossier_racine + '/res/information.png')
                self.act_infos.setIcon(icone)
                menu.addAction(self.act_infos)
            
            self.act_argument = QtGui.QAction(_((i18n.traduc("Arguments de lancement"))), self)
            self.act_argument.connect(self.act_argument, QtCore.SIGNAL("triggered()"), self.fen_arguments)
            icone = QtGui.QIcon(dossier_racine + '/res/arg_oxygen.png')
            self.act_argument.setIcon(icone)
            menu.addAction(self.act_argument)

            if raccourci == 0: #Si c'est un jeu installé en dur, on a le menu complet
                if os.uname()[4] != 'x86_64' or os.path.exists('/usr/bin/ldd32'): #Vérifi que l'on ne tourne pas sur x86_64
                    self.act_verif_depend = QtGui.QAction(_((i18n.traduc("Verifier les dependances"))), self)
                    self.act_verif_depend.connect(self.act_verif_depend, QtCore.SIGNAL("triggered()"), self.verif_dependances)
                    menu.addAction(self.act_verif_depend)
                    icone = QtGui.QIcon(dossier_racine + '/res/recherche_oxygen.png')
                    self.act_verif_depend.setIcon(icone)

                self.act_supr= QtGui.QAction((i18n.traduc("Supprimer")), self)                
                self.act_supr.connect(self.act_supr, QtCore.SIGNAL("triggered()"), self.confirmation_menu_c_suppr)

                menu.addAction(self.act_supr)
                icone = QtGui.QIcon(dossier_racine + '/res/supprimer_oxygen.png')
                self.act_supr.setIcon(icone)
                
                #Si on trouve le lien, on affiche la ligne pour le vister
                if variables.lien_site == 1:
                    self.act_site = QtGui.QAction(_((i18n.traduc("Visiter le site"))), self)
                    self.act_site.connect(self.act_site, QtCore.SIGNAL("triggered()"), self.navigateur_site)
                    menu.addAction(self.act_site)
                    icone = QtGui.QIcon(dossier_racine + '/res/actus.png')
                    self.act_site.setIcon(icone)
                
            else: #Si c'est un raccourci on affiche dans le menu que lancer le jeu et supprimer le raccourci
                self.act_modif= QtGui.QAction(i18n.traduc("Modifier le raccourci"), self)                
                self.act_modif.connect(self.act_modif, QtCore.SIGNAL("triggered()"), self.modif_jeu_)
                
                self.act_supr= QtGui.QAction(i18n.traduc("Supprimer le raccourci"), self)                
                self.act_supr.connect(self.act_supr, QtCore.SIGNAL("triggered()"), self.confirmation_suppr_desk)
                
                self.act_recherche= QtGui.QAction(i18n.traduc("Rechercher des informations sur internet"), self)                
                self.act_recherche.connect(self.act_recherche, QtCore.SIGNAL("triggered()"), self.recherche_internet_jeu)
                
                menu.addAction(self.act_modif)
                menu.addAction(self.act_supr)
                menu.addAction(self.act_recherche)
                
                icone = QtGui.QIcon(dossier_racine + '/res/ajouter.png')
                self.act_modif.setIcon(icone)
                
                icone = QtGui.QIcon(dossier_racine + '/res/supprimer_oxygen.png')
                self.act_supr.setIcon(icone)
                
                icone = QtGui.QIcon(dossier_racine + '/res/actus.png')
                self.act_recherche.setIcon(icone)
            
            self.var_liste_select = 0
            
            menu.exec_(event.globalPos())

class Ui_Arguments(QtGui.QWidget):
    def __init__(self, parent=None):
        '''Fenetre dans laquelle on passe les arguments pour le lancement des jeux.'''
        QtGui.QDialog.__init__(self, parent)
        QtGui.QDialog.__init__(self)
        
        #Défini le nom du fichier:
        self.nom_fichier= config(info=2) + '/args'
        
        self.setupUi(self, parent)
        
        self.font = QtGui.QFont()
        self.font.setPointSize(config(info=15))
        self.setFont(self.font)
        
        #Si l'on clique sur annuler:
        self.buttonBox.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.ferme)
        #Si on clique sur ok:
        self.buttonBox.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.sauve_arguments)

        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self, self.sauve_arguments)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter), self, self.sauve_arguments)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self, self.ferme)
        
        self.fichier = open(self.nom_fichier, 'a+')
        
        self.texte = self.fichier.read()
        
        #Si il y a déjà des arguments, on les affichent:
        if variables.args_dir_jeu in self.texte:
            self.ajout=0
            #On coupe le fichier pour créer une liste contenant chaque lignes:
            self.texte=self.texte.split('\n')
            #On coupe chaque ligne en 2 (entre le nom du jeu et les arguments)
            for i in range(len(self.texte)):
                #print i, len(self.texte)
                self.texte[i]=self.texte[i].split(':')

            #Affiche les arguments qui vont bien dans la zone de texte:
            print self.trouve_args()
            self.lineEdit.setText(self.trouve_args())
        else:
            self.ajout=1
        self.fichier.close()
            
    def trouve_args(self, val=0):
        '''Fonction qui trouve les arguments dans le fichier'''
        boucle=0
        while boucle < len(self.texte):
            if variables.args_dir_jeu in self.texte[boucle][0]:
                if val == 0:
                    arg = self.texte[boucle][1]
                    #Renvoi la valeur de l'argument:
                    return arg
                elif val == 1:
                    #Renvoi le numéro de ligne:
                    return boucle
            boucle=boucle+1
            
    def sauve_arguments(self):
        '''Quand on clique sur sauver...'''
        #Si les arguments existent, on ne change que la ligne:
        if self.ajout == 0:
            
            fichier = open(self.nom_fichier, 'r')
            texte=fichier.readlines()
            fichier.close()

            fichier = open(self.nom_fichier, 'w')
            
            ligne = self.trouve_args(1)
            tmp = texte[ligne].split(':')
            #Change la ligne avant de la réécrire:
            texte[ligne] = tmp[0] + ':' + self.lineEdit.text() + '\n'
            
            #écrit le fichier avec les changements:
            boucle=0
            while boucle < len(texte):
                fichier.write(texte[boucle])
                boucle=boucle+1
            fichier.close()
        
        #Si les arguments n'existent pas, on les ajoutes
        elif self.ajout == 1:
            fichier = open(self.nom_fichier, 'a+')
            fichier.write(str(variables.args_dir_jeu)+ ':' + str(self.lineEdit.text()) +'\n')
            fichier.close()
        
        self.ferme()

    def ferme(self):
        '''Ferme la fenêtre'''
        #try:
            #self.fichier.close()
        #except:
            #pass
        self.close()

    def setupUi(self, Form, parent):
        '''Dessin de l'interface de la fenêtre des arguments de lancement'''
        Form.setObjectName("Form")
        x, y = 400, 90
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,x,y).size()).expandedTo(Form.minimumSizeHint()))
        Form.setMinimumSize(QtCore.QSize(x,y))
        Form.setMaximumSize(QtCore.QSize(x,y))
        
        #Place de fenêtre au centre de la fenêtre principale
        posx = parent.pos().x() + parent.width()/2
        posy = parent.pos().y() + parent.height()/2
        self.move(posx-(x/2), posy-(y/2))
        #/
        
        icone = QtGui.QIcon((os.getcwd() + '/icone.png'))
        self.setWindowIcon(icone)

        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(5,30,x-10,22))
        self.lineEdit.setObjectName("lineEdit")

        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(0,5,281,21))
        self.label.setObjectName("label")

        self.buttonBox = QtGui.QDialogButtonBox(Form)
        self.buttonBox.setGeometry(QtCore.QRect(230,60,160,26))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        '''Affiche le texte de l'interface de la fenêtre des arguments de lancement'''
        Form.setWindowTitle(i18n.traduc("Arguments"))
        self.label.setText(i18n.traduc("Options de lancements:"))
