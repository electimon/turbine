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

'''Gestionnaire des modules'''

from PyQt4 import QtGui, QtCore
import os, socket, threading, urllib, sys
import imp, zipimport, zipfile #Charge à chaud les modules sous forme de source Python brutes ou d'archives zip
from variables import home, dossier_racine
from config import config #Lis le fichier de configuration
import i18n

nombre_onglets = 1 #Constante, nombre d'onglets fixes (hors modules)

class ModulesEvents(object):
    '''Gère les évenements (claviers et souris) et les relaient aux modules'''
    def chTabMod(self):
        '''Quand on va sur l'onglet contenant les modules...'''
        if self.tabModules.currentIndex() >= nombre_onglets: #Si on est sur un module (plugin)
            #On lui donne le focus
            try:
                self.liste_modules[self.tabModules.currentIndex()-nombre_onglets][0].setFocus()
            except:
                self.liste_modules[self.tabModules.currentIndex()-nombre_onglets][0].Onglet.setFocus()
        
    def EntreeMod(self):
        '''Quand on appui sur entrée dans l'un des modules...'''
        #print "entree2"
        if self.tabModules.currentIndex() >= nombre_onglets:
            try:
                #On tente de lancer la fonction 'entree' du module, si elle existe pas, c'est sans effet
                self.liste_modules[self.tabModules.currentIndex()-nombre_onglets][0].entree()
            except AttributeError: pass

    def EchapMod(self):
        '''Quand on appui sur la touche d'échappement dans l'un des modules...'''
        #print "echap2"
        if self.tabModules.currentIndex() >= nombre_onglets:
            try:
                #On tente de lancer la fonction 'echap' du module, si elle existe pas, c'est sans effet
                self.liste_modules[self.tabModules.currentIndex()-nombre_onglets][0].echap()
            except AttributeError: pass

class GModules(object):
    '''Gère directement les modules, chargement, déchargement, affichage, etc...'''
    def initGMods(self):
        '''Appelé au démarrage'''
        #Défini le conteneur pour les modules (Utilisé pour les gérer , mais le vrai conteneur est défini dans chacun des modules):
        self.ConteneurMods = self.tabModules
        
        self.liste_modules = [] #Liste qui contiendra toutes les instances des modules.
        sys.path.append(self.repMod)
        #Importe (charge) les modules additionnels déjà installés
        self.import_modules()

    def MajMod(self):
        '''Met à jour le module sélectionné'''
        #print self.ListeModules.currentRow() #Module actuellement séléctionné dans la liste
        #print self.listeMod #Liste des modules disponibles sur le serveur
        #self.self.liste_modules[i][0] #Liste des modules lancés [no_modules][instance, Qicone, version]
        module = self.listeMod[self.ListeModules.currentRow()][0]

        self.SupprMod(module) #Supprime le module
        self.InstMod(module) #Réinstalle le module
        self.import_modules() #Recharge les modules
        
        #Remet l'icone précédente
        icone = QtGui.QIcon(dossier_racine + '/res/retirer.png')
        self.ListeModules.item(self.ListeModules.currentRow()).setIcon(icone)
        
        #Vire le module pouvant être mis à jour de la liste:
        self.VerifMajMod()
        self.AffMajMod()

    def AffMajMod(self):
        '''Vérifi si le module actuellement selectionné peut être mis à jour, si c'est le cas on active le bouton pour la mise à jour'''
        if self.ListeModules.currentRow() in self.ListeMajMod:
            self.BouttonMajMod.setEnabled(True)
        else:
            self.BouttonMajMod.setEnabled(False)

    def VerifMajMod(self):
        '''Vérifi si les modules sont à jours, si ça n'est pas le cas, on affiche l'icone pour le notifier
        Compare les versions sur la liste sur internet avec les versions de modules installés en dur pour vérifier si c'est à jour'''
        icone = QtGui.QIcon(dossier_racine + '/res/maj_oxygen.png')
        self.ListeMajMod = [] #Contiendra la liste des modules pouvant être mis à jour (par id)
        for i in range(len(self.listeMod)):
            nom_module = self.listeMod[i][0]
            if nom_module != 'titre':
                id_module = self.trouve_module(nom_module, instance = False)
                if id_module != None:
                    #print self.liste_modules[id_module]
                    #print self.listeMod[i]
                    #print '---------'
                    #Si les deux version diffèrent, le module n'est pas à jour
                    if self.liste_modules[id_module][2] != self.listeMod[i][1]:
                        #print "Pas à jour:",  nom_module, str(i)
                        self.ListeMajMod.append(i)
                        self.ListeModules.item(i).setIcon(icone)

    def trouve_module(self, nom_module, instance=1):
        '''Parcours la liste des modules pour en trouver un en particulier et retourner son instance ou son id'''
        for i in range(len(self.liste_modules)):
            if nom_module in str(self.liste_modules[i][3]):
                if instance: #Si on demande son instance:
                    return self.liste_modules[i][0]
                else: #Si on demande son id
                    return i
        return None #Il n'a rien trouvé :(

    def AffIconesMods(self):
        '''Affiche les icones des modules'''
        #print self.iconesMods
        for i in range(len(self.liste_modules)):
            self.ConteneurMods.setTabIcon(nombre_onglets+i, self.liste_modules[i][1])
            #print self.iconesMods[i]

    def import_modules(self):
        '''Importe dynamiquement tous les modules du répertoire "~/.djl/modules"
        Si des modules sont déjà importés, on les délies et on les ré-importes, ce qui permet de les recharger'''
        #Garde en mémoire l'onglet courant, pour remettre le focus dessus après le rechargement
        onglet_courant = self.ConteneurMods.currentIndex()
        #Parcours la liste des modules (la liste est vide au demarrage) et lance la fonction 'fin' dans ces derniers,
        #pour faire le nettoyage. On utilise ensuite del pour délier en mémoire, le module sera vidé de la mémoire.
        for i in range(len(self.liste_modules)):
            try:
                try:
                    self.liste_modules[0][0].fin() #Envoi la fonction de fin du module
                except AttributeError, x:
                    print "Plugin Error (del1)> " + str(x)
                try:
                    #Ce qui suit ne marche que si le module dérive de QtGui.QWidget
                    #Qt liberera la mémoire quand on appelera la fonction close()
                    self.liste_modules[0][0].setAttribute(QtCore.Qt.WA_DeleteOnClose) 
                    self.liste_modules[0][0].close()
                except (AttributeError, RuntimeError):
                    #Si il y a exception, on tente d'utiliser l'objet 'Onglet' dans le module.
                    self.liste_modules[0][0].Onglet.setAttribute(QtCore.Qt.WA_DeleteOnClose) 
                    self.liste_modules[0][0].Onglet.close()
                    
                ##print str(self.liste_modules[0]) + ": " + str(sys.getrefcount(self.liste_modules[0]))
                #del self.liste_modules[0][0] #Délie le module (son instance)
                #del self.liste_modules[0][1] #Délie l'icone du module
                #del self.liste_modules[0][2] #Délie le numéro de version du module
                del self.liste_modules[0]
                
            except (AttributeError, IndexError, KeyError), x:
                print "Plugin Error (del2)> " + str(x)
                print self.liste_modules[0][0]
        self.liste_modules = []

        if os.path.exists(self.repMod):
            liste = os.listdir(self.repMod) #Liste des modules
            liste.sort() #Tri par ordre alphabétique les modules, c'est important, ça défini l'ordre d'import.
            for i in range(len(liste)):
                icone = QtGui.QIcon(dossier_racine + '/res/modules_oxygen.png')
                ext = liste[i].split(".")
                #si c'est bien un fichier python, on l'importe:
                if ext[len(ext)-1] == "py" or "-mod" in liste[i] or ext[len(ext)-1] == "zip": #si il y a '-mod", c'est que le module est un répertoire
                    #print "Module:", self.repMod + "/" + liste[i]
                    if ".py" in liste[i]:
                        nom_module = liste[i].replace(".py", "")
                        type = 0
                    elif ".zip" in liste[i]:
                        nom_module = liste[i].replace(".zip", "")
                        type = 1
                    else:
                        nom_module = liste[i]
                        type = 2
                    
                    #Charge le code du module
                    try:
                        if type == 0 or type == 2: #Si c'est un module sous forme de fichier .py ou autre
                            try:
                                module = imp.load_source(nom_module, self.repMod + "/" + liste[i])
                            except ImportError, x: #Le problème d'importation vient du code du module, pas du chargement du module mêmeasurementSystem
                                print "Module import error (load)>", nom_module + ':', x
                                continue
                                
                        elif type == 1: #Si c'est une module sous forme de paquet zip:
                            ###
                            try:
                                archive = self.repMod + '/' + liste[i]
                                zimp = zipimport.zipimporter(archive)
                                fichier_zip = zipfile.ZipFile(archive, 'r') #Ouvre l'archive zip contenant les sources
                                liste_fichiers = fichier_zip.namelist() #Récupère la liste des fichiers de l'archive 

                                for id in range(len(liste_fichiers)):
                                    if liste_fichiers[id] == "icone.png": #Si le paquet contient une icone, on l'affiche
                                        #print "icone: ", liste_fichiers[id]
                                        #On extrait l'icone de l'archive...
                                        donn = fichier_zip.read(liste_fichiers[id])
                                        addr_ico = config(info=2) + '/' + config(info=14) + '/' + liste[i].split('.zip')[0] + '_' + liste_fichiers[id]
                                        #print len(donn)
                                        f = open(addr_ico, 'w')
                                        f.write(donn)
                                        f.close()
                                        #On charge l'icone:
                                        icone = QtGui.QIcon(addr_ico)
                                        #print str(icone), str(addr_ico)
                                        
                                    if not '__init__' in liste_fichiers[id]:
                                        #print liste_fichiers[id]
                                        if '.py' in liste_fichiers[id]:
                                            zimp.load_module(liste_fichiers[id].replace('.py', '')) #Précharge les sources (pas le script principal)
                                
                                fichier_zip.close()
                                module = zimp.load_module("__init__") #Charge le fichier '__init__.py' du paquet zip.
                            except (zipimport.ZipImportError), x: #Typiquement quand le fichier __init__ n'est pas trouvé
                                print "Zip module error:", nom_module, '-', x
                                continue #On passe à l'itération de boucle suivante, le module ne sera pas chargé.
                            ###
                    except (NameError, AttributeError), x:
                        print nom_module, "Module error:", x
                        continue #Passe au module suivant si il y a un problème de dépendance avec celui là
                    
                    #Essai de trouver le numero de version du module, si ça plante (pas de numéro), on défini la version à -1
                    try:
                        versionMod = module.version
                    except AttributeError:
                        versionMod = '-1'
                    
                    #Lance le module et ajoute son instance dans la liste (ça servira pour l'utiliser mais aussi pour le nettoyage).
                    try:
                        print module , versionMod #, icone
                        #Lance le module et envoi l'instance dans la liste des modules (ainsi que l'icone, la version et le nom du fichier source)
                        self.liste_modules.append([module.main(self), icone, versionMod, liste[i]])
                        #sys.modules[nom_module].No = i #Numéro du module
                    except AttributeError, x:
                        #print "Plugin Error (import)> " + sys.modules[nom_module].nom_module +  ": " + str(x)
                        print "Plugin Error (import)> " + nom_module +  ": " + str(x)
        self.ConteneurMods.setCurrentIndex(onglet_courant) #On se remet sur l'onglet précedent
        self.AffIconesMods() #Envoi l'affichage des icones des modules.
    
class Interface(GModules, ModulesEvents):
    '''Gère l'interface pour le gestionnaire des modules'''
    def Init_modules(self):
        '''Fonction principale du gestionnaire de modules'''
        repertoire = 'modules' #Nom du répertoire contenant les modules sur le serveur et dans la partie cliente
        self.repMod = home + "/.djl/" + repertoire #Répertoire d'installation des modules
        self.f_listeMod = self.repMod + "/liste" #Fichier texte contenant la liste des modules
        self.srvMod = self.serveur_maj[0] + "/maj_djl/" + repertoire  #Serveur pour télécharger les modules
        
        self.Ui_modules() #Envoi l'affichage de l'interface
        
        socket.setdefaulttimeout(4)
        
        self.vliste = False #Quand la variable passe à True, on affiche la liste des modules.
        self.listeMod = [] #Liste des fichiers, sera rempli en fonction des éléments de la QlistWidget
        
#        self.tab_5.timerEvent = self.FtimerMod
#        self.timerMod = QtCore.QBasicTimer()
#        self.timerMod.start(100, self.tab_5)

        self.timerMod = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timerMod, QtCore.SIGNAL("timeout()"), self.FtimerMod)
        self.timerMod.start(300)

        try:
            th = threading.Thread(target=self.listeModules)
            th.start()
        except IOError, x:
            #print titre, serveur, str(x)
            print x
            
        socket.setdefaulttimeout(None)
        
        self.initGMods() #Envoi l'initialisation des modules déjà installés

    def listeModules(self):
        '''Créé la liste des modules pouvant être téléchargés depuis les informations du serveur.'''
        #On s'assure que le dossier pour contenir les modules existe:
        if not os.path.exists(self.repMod):
            os.mkdir(self.repMod)
        
        #Télécharge la liste
        try:
            urllib.urlretrieve(self.srvMod + "/liste", self.f_listeMod, reporthook=False)
        except IOError: #Si on ne peut pas accéder à la liste, on quitte la fonction, la liste des modules sera vide.
            return
            
        #Après avoir téléchargé la liste, on la lit:
        self.f_listeMod = open(self.f_listeMod, 'r')
        self.liste_fMod = self.f_listeMod.readlines()
        #print self.liste_fMod
        self.f_listeMod.close()
        
        #Si il tombe sur une page d'erreur 404, on quitte la fonction, la liste ne sera pas affichée
        for i in range(len(self.liste_fMod)):
            if "404 Not Found" in self.liste_fMod[i] or "403 Forbidden" in self.liste_fMod[i]:
                return
            elif "<html>" in self.liste_fMod[i]:
                return
            
        self.vliste = True #La liste sera affichée, dans le Thread principal.
        
    def AffListeMod(self):
        '''Affiche la liste des modules'''
        liste = self.liste_fMod
        for i in range(len(liste)):
            liste[i] = liste[i].replace('\n', '')
            mini_liste = liste[i].split(";") #L'élément 0 sera le nom du fichier, l'autre sera la description
            texte = mini_liste[1]
            fichier = mini_liste[0]
            
            if len(mini_liste) >= 3:
                version = mini_liste[2]
            else:
                version = 'nul'
            
            if os.path.exists(self.repMod + "/" + fichier):
                icone = QtGui.QIcon(dossier_racine + '/res/retirer.png')
            else:
                icone = QtGui.QIcon(dossier_racine + '/res/ajouter.png')
            self.listeMod.append([fichier, version])
            item = QtGui.QListWidgetItem(self.ListeModules)
            if fichier != 'titre': #Si le nom de fichier est 'titre', on ne met pas l'icone
                item.setIcon(QtGui.QIcon(icone))
            item.setText(texte)
            self.ListeModules.addItem(item)
    
    def FtimerMod(self):
        if self.vliste: #Quand la liste des modules est récupéré sur le serveur...
            self.AffListeMod() #On affiche la liste
            self.VerifMajMod() #Vérifi si les modules sont à jours (maintenant qu'on a la liste)
            self.timerMod.stop()
    
    def InstSupprMod(self):
        '''Télécharge et copie le module si il n'existe pas, sinon on le supprime'''
        fichier = self.listeMod[self.ListeModules.currentRow()][0]
        if fichier != 'titre':
            #Si le module exist, on la supprime
            if os.path.exists(self.repMod + "/" + fichier):
                #print "Supprime: ", fichier
                self.SupprMod(fichier)
                
                #Change l'icone dans la liste pour montrer qu'elle pourra maintenant être installé
                icone = QtGui.QIcon(dossier_racine + '/res/ajouter.png')
                self.ChBoutonMod()
    
            #Si il n'existe pas, on le télécharge
            else:
                #print "Installe: ", fichier
                #urllib.urlretrieve(self.srvMod + "/" + fichier, self.repMod + "/" + fichier, reporthook=False)
                self.InstMod(fichier)
                
                #Change l'icone dans la liste pour montrer qu'elle pourra maintenant être supprimée
                icone = QtGui.QIcon(dossier_racine + '/res/retirer.png')
                self.ChBoutonMod()
                
            #On change l'icone en fonction que le fichier ait été installé ou supprimé:
            #id = self.listeMod.index(fichier)
            for i_ in range(len(self.listeMod)):
                if self.listeMod[i_][0] == fichier:
                    id = i_
                    continue
            self.ListeModules.item(id).setIcon(icone)
            self.import_modules() #Recharge les modules
            
            self.VerifMajMod() #Revérifi l'état de mise à jour des modules
            self.AffMajMod() #Rafraichi le bouton de mis à jour du module actuellement sélectionné
            
    def InstMod(self, module):
        '''Installe le module donné en argument'''
        urllib.urlretrieve(self.srvMod + "/" + module, self.repMod + "/" + module, reporthook=False)
        
    def SupprMod(self, module):
        '''Supprime le module donné en argument'''
        #On supprime également tous les fichiers qui commencent par le nom du module (le modules, fichiers .pyc, log, etc...
        liste = os.listdir(self.repMod)
        for i in range(len(liste)):
            l_fichier = liste[i].split('.')
            if l_fichier[0] == module.split('.')[0]: #Fatalement le nom du module ne doit comporter qu'un '.', genre 'fichier.py'
                os.remove(self.repMod + "/" + liste[i])
                
    def ChBoutonMod(self):
        '''Met à jour le texte du bouton pour afficher "Installer" ou "Supprimer" suivant si le module séléctionné existe sur le disque ou pas'''
        if self.listeMod[self.ListeModules.currentRow()][0] == 'titre':
            self.BouttonInstModules.setEnabled(False)
        else:
            self.BouttonInstModules.setEnabled(True)
            if os.path.exists(self.repMod + "/" + self.listeMod[self.ListeModules.currentRow()][0]):
                self.BouttonInstModules.setText(i18n.traduc("Supprimer"))
            else:
                self.BouttonInstModules.setText(i18n.traduc("Installer"))
        self.AffMajMod()
        
    def Ui_modules(self):
        '''Dessin de l'interface du gestionnaire de modules'''
        #####Layout principal de l'onglet:
        self.LayoutD = QtGui.QVBoxLayout(self.tab_5)
        self.LayoutD.setObjectName("LayoutD")
        
        self.tabModules = QtGui.QTabWidget(self.tab_5)
        self.tabModules.setObjectName("tabModules")
        self.LayoutD.addWidget(self.tabModules)
        ######
        
        ###Définition des sous onglets:
        self.tab_2_1 = QtGui.QWidget(self.tabModules) #Sous onglet principal
        self.tab_2_1.setObjectName("tab_2_1")
        self.tabModules.addTab(self.tab_2_1,"")
        ###
        
        ###Objets de l'interface:
        self.SDLayout = QtGui.QVBoxLayout(self.tab_2_1)
        self.SDLayout.setObjectName("SDLayout")
        
        self.ListeModules = QtGui.QListWidget(self.tab_2_1)
        self.ListeModules.setObjectName("ListeModules")
        self.SDLayout.addWidget(self.ListeModules)
        
        self.BouttonInstModules = QtGui.QPushButton(self.tab_2_1)
        self.BouttonInstModules.setObjectName("BouttonInstModules")
        self.SDLayout.addWidget(self.BouttonInstModules)
        self.BouttonInstModules.setEnabled(False)
        
        self.BouttonMajMod = QtGui.QPushButton(self.tab_2_1)
        self.BouttonMajMod.setObjectName("BouttonMajMod")
        self.BouttonMajMod.setEnabled(False)
        
        self.SDLayout.addWidget(self.BouttonMajMod)
        ###
        
        self.connexionsModules()
        self.traducsModules()
        
    def connexionsModules(self):
        '''Connexion des objets Qt aux fonctions et raccourcis'''
        self.BouttonInstModules.connect(self.BouttonInstModules, QtCore.SIGNAL("clicked()"), self.InstSupprMod)
        self.BouttonMajMod.connect(self.BouttonMajMod, QtCore.SIGNAL("clicked()"), self.MajMod)
        self.ListeModules.connect(self.ListeModules, QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.ChBoutonMod)
        self.ListeModules.connect(self.ListeModules, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.InstSupprMod)
        
        self.tabModules.connect(self.tabModules, QtCore.SIGNAL("currentChanged(int)"), self.chTabMod)
        #QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self.tabModules, self.EntreeMod)
        #QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter), self.tabModules, self.EntreeMod)
        #QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self.tab_2_1, self.EchapMod)
        
    def traducsModules(self):
        #self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), i18n.traduc("Gestionnaire des modules"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), i18n.traduc("Modules"))
        self.tabWidget.setTabIcon(self.tabWidget.indexOf(self.tab_5), QtGui.QIcon(dossier_racine + '/res/ajouter.png'))
        self.tabModules.setTabText(0, i18n.traduc("Depot"))
        self.tabModules.setTabIcon(0, QtGui.QIcon(dossier_racine + '/res/txt_oxygen.png'))

        self.BouttonInstModules.setText(i18n.traduc("Installer"))
        self.BouttonMajMod.setText(i18n.traduc("Mettre a jour"))
