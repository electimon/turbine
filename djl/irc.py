# -*- coding: utf-8 -*-*

# DJL (Dépot jeux Linux)
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

'''Partie cliente sur IRC'''

# Problème quand on utilise /quit, l'utilisateur la chaine "utilisateur
# déco..." ne s'affiche pas (mais est ajouté à la liste)

import sys
sys.path.append("libs")
import irclib

from PyQt4 import QtGui, QtCore
import threading
from variables import variables, dossier_racine
import os
import time
import i18n

from config import config

# canaux = config(info=16) #Va chercher la liste des canaux suivant la configuration
serveur_IRC = "irc.freenode.com"


# Debogage d'IRClib
irclib.DEBUG = 0


class interface_IRC(object):

    def setupUiIRC(self):
        '''Tout ce qui concerne le dessin de l'onglet IRC'''
        self.gridlayout_3 = QtGui.QGridLayout(self.tab_3)
        self.gridlayout_3.setObjectName("gridlayout_3")

        self.gridlayout_3_1 = QtGui.QGridLayout()
        self.gridlayout_3_1.setObjectName("gridlayout_3_1")

        self.gridlayout_3_2 = QtGui.QGridLayout()
        self.gridlayout_3_2.setObjectName("gridlayout_3_2")

        self.gridlayout_3.addLayout(self.gridlayout_3_1, 0, 0)
        self.gridlayout_3.addLayout(self.gridlayout_3_2, 1, 0)

        self.listeW_canaux = QtGui.QListWidget(self.tab_3)
        self.listeW_canaux.setMinimumSize(QtCore.QSize(160, 200))
        self.listeW_canaux.setMaximumSize(QtCore.QSize(160, 1280))
        self.listeW_canaux.setObjectName("listeW_canaux")
        self.listeW_canaux.setEnabled(False)

        self.gridlayout_3_1.addWidget(self.listeW_canaux, 1, 0)

        self.textEdit_chat = QtGui.QTextEdit(self.tab_3)
        self.textEdit_chat.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.textEdit_chat.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit_chat.setReadOnly(True)
        self.textEdit_chat.setEnabled(False)
        self.textEdit_chat.setObjectName("textEdit_chat")
        self.textEdit_chat.setAcceptRichText(False)

        self.gridlayout_3_1.addWidget(self.textEdit_chat, 1, 1)

        # Change la couleur de fond de l'onglet IRC (si l'utilisateur a choisi en noir):
        if int(config(info=13)) == 1:
            from palette_irc import Palette_IRC
            self.textEdit_chat.setPalette(Palette_IRC.palette)

        self.line_Edit_chat = QtGui.QLineEdit(self.tab_3)

        self.line_Edit_chat.setObjectName("line_Edit_chat")
        self.line_Edit_chat.setEnabled(False)
        self.gridlayout_3_2.addWidget(self.line_Edit_chat, 0, 0)
        # self.gridlayout_3.addWidget(self.line_Edit_chat,3,1)

        self.pushButton_chat = QtGui.QPushButton(self.tab_3)
        self.pushButton_chat.setObjectName("pushButton_chat")
        self.pushButton_chat.setEnabled(False)
        self.gridlayout_3_2.addWidget(self.pushButton_chat, 0, 1)
        # self.gridlayout_3.addWidget(self.pushButton_chat,3,2)

        self.Button_connect_chat = QtGui.QPushButton(self.tab_3)
        self.Button_connect_chat.setObjectName("pushButton_chat")
        self.Button_connect_chat.setEnabled(True)
        self.Button_connect_chat.setMinimumSize(QtCore.QSize(160, 25))
        self.Button_connect_chat.setMaximumSize(QtCore.QSize(160, 25))
        self.gridlayout_3_1.addWidget(self.Button_connect_chat, 0, 0)

        self.listWidget_chat = QtGui.QListWidget(self.tab_3)
        self.listWidget_chat.setMinimumSize(QtCore.QSize(160, 200))
        self.listWidget_chat.setMaximumSize(QtCore.QSize(160, 1280))
        self.listWidget_chat.setObjectName("listWidget_chat")
        self.listWidget_chat.setEnabled(False)
        self.gridlayout_3_1.addWidget(self.listWidget_chat, 1, 2)

        self.pushButton_chat.setText(i18n.traduc("Envoyer"))
        self.listeW_canaux.connect(
            self.listeW_canaux,
            QtCore.SIGNAL("itemSelectionChanged()"),
            self.change_canal)
        self.pushButton_chat.connect(
            self.pushButton_chat,
            QtCore.SIGNAL("clicked()"),
            self.envoi_irc)
        self.Button_connect_chat.connect(
            self.Button_connect_chat,
            QtCore.SIGNAL("clicked()"),
            self.connexion_irc)

        # Pareil sur la liste des utilisateurs sur le canal IRC:
        self.listWidget_chat.connect(
            self.listWidget_chat,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.message_pv_irc)

    def init_IRC(self):
        '''Se connecte automatiquement sur IRC ou pas, suivant la configuration'''
        # Envoi la connexion au canal IRC suivant la configuration
        self.etat_irc = 1
        if int(config(info=12)) == 1:
            self.connexion_irc()
        else:
            self.Button_connect_chat.setText(i18n.traduc("Connection"))
            #self.etat_irc = 0

    def Prepare_IRC(self):
        '''Initialisation du client IRC'''

        # Défini le pseudo sur IRC:
        pseudo = config(info=11)
        if "-djl" in pseudo:
            self.pseudo = pseudo
        else:
            self.pseudo = pseudo + "-djl"

        # Trouve la liste des canaux dans la configuration
        self.canaux_IRC = config(info=16)

        # Met à zero toutes les variables contenant la liste des utilisateurs, le texte, etc...
        variables.liste_canaux = [""] * len(self.canaux_IRC)
        variables.liste_utilisateurs = {}
        variables.recoi_irc = ["", "", ""]
        variables. even_irc = ["", "", ""]

        self.listeW_canaux.clear()
        # Ajoute la liste des canaux dans la liste (IRC).
        for i in range(len(self.canaux_IRC)):
            # print self.canaux_IRC[i], str(len(self.canaux_IRC))
            # self.listeW_canaux.addItem(self.canaux_IRC[i])
            item = QtGui.QListWidgetItem(self.listeW_canaux)
            item.setText(self.canaux_IRC[i])
            self.listeW_canaux.addItem(item)
            self.change_couleur_canal(i)

        # Connection de la boite de dialogue IRC:
        self.textEdit_chat.connect(
            self.textEdit_chat,
            QtCore.SIGNAL("textChanged()"),
            self.rafraichi_IRC)

        # Demande à la configuration la couleur de fond du client IRC.
        if config(info=13) == '1':
            self.info_13 = 1
        else:
            self.info_13 = 0

    def active_client(self):
        '''On vient d'être connecté, on active le client IRC'''
        # Défini la position du curseur actuel, servira plus tard pour ajouter le texte à la fin.
        #self.curseur_chat = self.textEdit_chat.textCursor()

        self.textEdit_chat.setEnabled(True)
        self.line_Edit_chat.setEnabled(True)
        self.pushButton_chat.setEnabled(True)
        self.listWidget_chat.setEnabled(True)
        self.listeW_canaux.setEnabled(True)  # Liste des canaux
        self.listeW_canaux.setCurrentRow(0)
        self.line_Edit_chat.setText("")
        self.canal_courant = self.canaux_IRC[0]
        self.insert_txt_irc(i18n.traduc("Connecte !") + "<br />", 1)

        self.change_canal()

        variables.connecte = 2

    def desactive_client(self):
        '''On vient de se deconnecter, on désactive le client'''
        #self.connecte = 0
        self.textEdit_chat.setText("")
        self.textEdit_chat.insertPlainText(i18n.traduc("Deconnecte") + "\n")
        self.listWidget_chat.clear()
        self.listeW_canaux.clear()
        # self.textEdit_chat.setEnabled(False)
        self.line_Edit_chat.setEnabled(False)
        self.pushButton_chat.setEnabled(False)
        self.listWidget_chat.setEnabled(False)
        self.listeW_canaux.setEnabled(False)  # Liste des canaux

    def change_couleur_canal(self, canal, couleur="gris"):
        '''Change la couleur de fond lorsque l'on recoi un message privé ou
        quand l'on recoi un message dans un autre canal que le canal courant
        va variable canal peut aussi bien être l'id du canal (un entier) ou son nom (chaine)'''

        if type(canal) == int:
            # Si on donne comme canal son entier...
            id_canal = canal
        else:
            # Si on ne donne que son nom, on trouve son id
            try:
                id_canal = self.canaux_IRC.index(canal)
            except ValueError:
                return

        if couleur == "bleu":
            c_rvb = QtGui.QColor(100, 100, 250)  # Couleur RVB recoimessage privé (hl)
        elif couleur == "rouge":
            c_rvb = QtGui.QColor(250, 100, 100)  # Couleur RVB message non privé
        else:
            c_rvb = QtGui.QColor(230, 230, 230)  # Couleur RVB standard

        self.listeW_canaux.item(id_canal).setBackground(c_rvb)

    def connexion_irc(self):
        '''Connexion/deconnexion du canal IRC'''
        if self.etat_irc == 1:
            # On est pas connecté, on se connecte...
            self.Prepare_IRC()
            self.textEdit_chat.setText("")
            self.textEdit_chat.insertPlainText(i18n.traduc("En cours de connexion..."))
            self.Button_connect_chat.setText(i18n.traduc("Deconnection"))

            try:
                self.th_irc._exitfunc()
            except:
                pass

            self.th_irc = connexion_IRC(serveur_IRC, self.canaux_IRC, 6667, self.pseudo)
            self.th_irc.start()

            self.etat_irc = 0
        else:  # Si on est déjà connecté, on se déconnecte...
            self.Button_connect_chat.setText(i18n.traduc("Connection"))
            #variables.recoi_irc = ''
            self.deco_irc()

            # On remet les variables à zero
            variables.liste_canaux = [""] * len(self.canaux_IRC)
            variables.liste_utilisateurs = {}
            variables.recoi_irc = ["", "", ""]
            variables. even_irc = ["", "", ""]

            self.desactive_client()
            self.etat_irc = 1

    def redemarre_IRC(self):
        '''Deco/reco du client IRC'''
        self.deco_irc()
        self.pseudo = self.pseudo + "_"
        time.sleep(0.3)
        self.etat_irc = 1
        self.connexion_irc()

    def rafraichi_IRC(self):
        '''Descend automatiquement la barre de défilement quand du texte s'ajoute dans le boite de dialogue'''
        val = int(self.textEdit_chat.verticalScrollBar().maximum())
        self.textEdit_chat.verticalScrollBar().setValue(val)

    def recoi_msg_irc(self):
        '''Quand on recoi un message sur IRC, on créé la chaine qui contient le pseudo et le message et on l'ajoute ensuite dans la liste'''
        texte, canal, pseudo = variables.recoi_irc[
            0], variables.recoi_irc[1], variables.recoi_irc[2]
        # Si il y a le pseudo de l'utilisateur dans le message...
        if self.pseudo in texte[0]:
            couleur = "255, 0, 0"
            # On fait clignoter le client si l'utilisateur n'affiche pas le client ou
            # que djl est minimisé.
            if self.tabWidget.currentIndex() != self.tabWidget.indexOf(self.tab_3) or self.isHidden() == True:
                self.clignote_IRC = 1

            # Si on a pas le focus sur le bon canal, on le marque en bleu:
            if self.canal_courant != canal:
                # print "Couleur: Bleu"
                self.change_couleur_canal(canal, "bleu")

        # Sinon c'est un message normal
        else:
            if self.info_13 == 1:
                # Banc si le fond est noir
                couleur = "255, 255, 255"
            else:
                # Noir si le fond est blanc
                couleur = "0, 0, 0"
            #couleur = "255, 255, 255"
            # Si on recoi un message quelconque et qu'on affiche pas le canal qui le
            # recoi, on marque le canal en rouge:
            if self.canal_courant != canal:
                # print "Couleur: Rouge"
                self.change_couleur_canal(canal, "rouge")
        chaine = QtGui.QApplication.translate(
            "MainWindow",
            "<span style='color: rgb(" + couleur + ");'>" + pseudo + ": " + texte[0] + "</span>",
            None,
            QtGui.QApplication.UnicodeUTF8) + "\n"

        self.Aliste_txt_irc(chaine, canal)

    def trouve_canal_courant(self):
        '''Trouve le canal IRC en cours d'utilisation'''
        return self.canaux_IRC[self.listeW_canaux.currentRow()]

    def Aliste_txt_irc(self, texte, canal, envoi=0):
        '''Ajoute dans la liste du canal courant le texte donné'''
        try:
            # Trouve l'index du canal en fonction de son nom
            id = self.canaux_IRC.index(canal)
        except ValueError, x:
            print "Problème ajout texte:", str(x)
            id = 0
        #texte=texte.replace("\n", "")
        #texte=texte.replace("<br>", "")
        if variables.liste_canaux[id] == "":
            variables.liste_canaux[id] = variables.liste_canaux[id] + texte
        else:
            variables.liste_canaux[id] = variables.liste_canaux[id] + "<br />" + texte
        self.insert_txt_irc(texte, envoi)  # On affiche le texte dans la boite de dialogue

    # Si envoi=1, ça veut dire que c'est l'utilisateur qui envoi le texte, on
    # ne vérifi donc pas si il est sur le bon canal.
    def insert_txt_irc(self, chaine, envoi=0):
        '''Insere le texte donné dans la boite de texte sur IRC'''
        # Uniquement si on a le focus sur le bon canal:
        # print ">"+str(self.canal_courant)+"<",  ">"+variables.even_irc[1]+"<", str(envoi)

        #!!! variables.recoi_irc != variables.even_irc
        if self.canal_courant == variables.recoi_irc[1] or self.canal_courant == variables.even_irc[1] or envoi == 1:
            # Ajoute le texte à la position du curseur précedemment sauvegardé
            # self.textEdit_chat.setTextCursor(self.curseur_chat)

            self.textEdit_chat.append(chaine)
            # Garde une copie de la position du curseur pour pouvoir afficher le texte à la fin lors du prochain appel à la fonction
            #self.curseur_chat = self.textEdit_chat.textCursor()

    def message_pv_irc(self):
        '''Quand on clique sur un nom d'utilisateur dans le canal IRC, on ajoute son pseudo dans la ligne d'envoi de texte'''
        #nom_utilisateur = self.liste_utilisateurs[self.listWidget_chat.currentRow()]
        nom_utilisateur = variables.liste_utilisateurs[
            self.canal_courant][self.listWidget_chat.currentRow() + 1]

        if nom_utilisateur[0] == "@":
            nom_utilisateur = nom_utilisateur[1:]
        elif nom_utilisateur[0] == "+":
            nom_utilisateur = nom_utilisateur[1:]

        # On supprime ": " à la fin, il sera ajouté à la fin de la fonction.
        self.line_Edit_chat.setText(self.line_Edit_chat.text().replace(": ", ""))

        # Si il n'y a pas le pseudo on l'ajoute.
        if not nom_utilisateur in self.line_Edit_chat.text():
            if self.line_Edit_chat.text() == '':
                self.line_Edit_chat.setText(nom_utilisateur)
            else:
                self.line_Edit_chat.setText(self.line_Edit_chat.text() + " " + nom_utilisateur)
            self.line_Edit_chat.setText(self.line_Edit_chat.text() + ": ")
        # Si il y est déjà, on le supprime
        else:
            if " " + nom_utilisateur in self.line_Edit_chat.text():
                self.line_Edit_chat.setText(
                    self.line_Edit_chat.text(
                    ).replace(
                        " " +
                        nom_utilisateur,
                        " "))
            else:
                self.line_Edit_chat.setText(
                    self.line_Edit_chat.text(
                    ).replace(
                        nom_utilisateur,
                        " "))

            if "  " in self.line_Edit_chat.text():
                self.line_Edit_chat.setText(self.line_Edit_chat.text().replace("  ", " "))

            if len(self.line_Edit_chat.text()) <= 1:
                if self.line_Edit_chat.text()[0] == "" or self.line_Edit_chat.text()[0] == " ":
                    if self.line_Edit_chat.text()[0] == " ":
                        self.line_Edit_chat.setText(self.line_Edit_chat.text()[1:])
            else:
                self.line_Edit_chat.setText(self.line_Edit_chat.text() + ": ")

        self.line_Edit_chat.setFocus()  # On redonne le focus à la ligne de texte

    def change_canal(self):
        '''Quand on sélectionne un nouveau canal dans la partie client IRC'''
        # print "Canal actuel:", str(self.canaux_IRC[self.listeW_canaux.currentRow()])

        self.canal_courant = self.trouve_canal_courant()
        # Vide la boite de texte
        self.textEdit_chat.clear()

        # Envoi le texte dans la boite en fonction du canal séléctionné
        self.textEdit_chat.setHtml(variables.liste_canaux[self.listeW_canaux.currentRow()])

        # Fait descendre la zone de chat
        self.rafraichi_IRC()

        # Créé la nouvelle liste d'utilisateurs
        if len(variables.liste_utilisateurs) > 0:
            self.cree_liste_utilisateurs_irc(self.canal_courant)

        # On remet la couleur de fond du canal par defaut
        # Elle a put être changée après un message privé ou autre
        self.change_couleur_canal(self.canal_courant)

        self.line_Edit_chat.setFocus()  # Donne le focus à la ligne de texte

    def envoi_irc(self):
        '''Fonction pour envoyer les messages sur IRC (le contenu de self.line_Edit_chat.text()'''
        if self.line_Edit_chat.text() != '':
            texte = (unicode(self.line_Edit_chat.text())).encode('utf-8')

            if texte[0] != "/":  # On envoi rien si c'est une commande
                # Si c'est un message normal...
                if self.info_13 == 1:
                    # niveau de gris si le fond est noir
                    couleur = "150, 150, 150"
                else:
                    couleur = "100, 100, 100"

                chaine = i18n.encode(
                    "--><span style='color: rgb(" + couleur + ");'> " + str(self.pseudo) + ': ' + texte + '\n' + "</span>")

                #variables.liste_canaux[variables.canal_courant] = variables.liste_canaux[variables.canal_courant] + chaine
                # self.insert_txt_irc(chaine,1)
                canal = self.trouve_canal_courant()
                self.Aliste_txt_irc(chaine, canal, envoi=1)
                self.th_irc.envoi(texte, canal)

            self.line_Edit_chat.setText("")

    def ajout_utilisateur_irc(self):
        '''Ajoute un utilisateur dans la liste sur le canal IRC donné'''
        canal = variables.even_irc[1]
        nom_utilisateur = variables.even_irc[2]

        # print "Ajout utiliseur:", canal, self.canal_courant

        # Ajoute de la liste des utilisateurs celui qui vient de se connecter:
        if not self.pseudo in nom_utilisateur:
            if self.canal_courant == canal:
                img_b = QtGui.QPixmap(dossier_racine + '/icone.png')
                item = QtGui.QListWidgetItem(self.listWidget_chat)
                item.setIcon(QtGui.QIcon(img_b))
                item.setText(str(nom_utilisateur))
                self.listWidget_chat.addItem(item)

            chaine = "--><span style='color: rgb(0, 255, 0);'> " + \
                i18n.traduc(
                    "Utilisateur connecte") + ': ' + nom_utilisateur + '\n' + "</span>"
            self.Aliste_txt_irc(chaine, canal, 0)

            try:
                variables.liste_utilisateurs[canal].append(nom_utilisateur)
            except KeyError, x:
                print("ajout_utilisateur_irc():" + str(x))
                pass
                # print "Message d'erreur",  str(x)
                # print "Canal",  str(canal)
                # print "Nom d'utilisateur",  str(nom_utilisateur)
                # print "liste des utilisateurs",  str(variables.liste_utilisateurs)
                #self.clignote_IRC = 1

    def supprime_utilisateur_irc(self):
        '''Supprime un utilisateur de la liste sur IRC et affiche la nouvelle liste'''
        canal = variables.even_irc[1]
        nom_utilisateur = variables.even_irc[2]

        # print canal,  self.canal_courant

        chaine = "--><span style='color: rgb(187, 111, 61);'> " + \
            i18n.traduc(
                "Utilisateur deconnecte") + ': ' + nom_utilisateur + '\n' + "</span>"

        # print ">0", variables.liste_utilisateurs[canal]
        # Enlève l'utilisateur déconnecté de la liste:

        if canal is None:  # Si l'utilisateur a quitté complètement IRC (commande /quit)
            # Rappel, liste_utilisateur est un dico, id est une chaine.
            for id in variables.liste_utilisateurs:
                if nom_utilisateur in variables.liste_utilisateurs[id]:
                    # On donne à la fonction d'envoi des message des notifications le nom du
                    # canal où l'utilisateur vient que faire /quit:
                    variables.even_irc[1] = id
                    try:
                        variables.liste_utilisateurs[id].remove(str(nom_utilisateur))
                    except ValueError:
                        print "Problème de deconexion>>>", nom_utilisateur
                    self.Aliste_txt_irc(chaine, id)

                    if id == self.canal_courant:
                        self.cree_liste_utilisateurs_irc(id)
        else:
            try:
                self.Aliste_txt_irc(chaine, canal)
                variables.liste_utilisateurs[canal].remove(str(nom_utilisateur))
            except ValueError:
                print "Problème de deconexion>>>", nom_utilisateur

            # Créé une nouvelle liste d'utilisateurs
            # print ">1", variables.liste_utilisateurs[canal]
            if canal == self.canal_courant:
                self.cree_liste_utilisateurs_irc(canal)
            # print ">2", variables.liste_utilisateurs[canal]

    def cree_liste_utilisateurs_irc(self, canal):
        '''Affiche la liste des utilisateurs du canal sur IRC dans la QlistBox'''
        # print canal
        self.listWidget_chat.clear()

        # print variables.liste_utilisateurs

        # Problème, on affiche le nouvel utilisateur sur le canal courant et non
        # celui qui vientde réélement recevoir l'utilisateur.
        liste_utilisateurs = variables.liste_utilisateurs[canal]
        liste_utilisateurs.sort()
        # print str(liste_utilisateurs), str(self.canal_courant)

        for i in range(len(liste_utilisateurs)):
            if liste_utilisateurs[i] != '\n' and liste_utilisateurs[i] != '':
                if '\r' in liste_utilisateurs[i]:
                    liste_utilisateurs[i] = liste_utilisateurs[i].replace('\r', '')

                if '+' in liste_utilisateurs[i]:
                    liste_utilisateurs[i] = liste_utilisateurs[i].replace('+', '')

                # Si l'utilisateur est un op, on ajoute l'icone adéquate en face
                if liste_utilisateurs[i][0] == "@":
                    img_b = QtGui.QPixmap(dossier_racine + '/res/b_oxygen.png')
                    item = QtGui.QListWidgetItem(self.listWidget_chat)
                    item.setIcon(QtGui.QIcon(img_b))
                    self.listWidget_chat.setIconSize(QtCore.QSize(8, 8))
                    item.setText(liste_utilisateurs[i][1:])

                    # print item, liste_utilisateurs[i]

                    self.listWidget_chat.insertItem(i, item)

                # Si c'est un utilisateur de djl, on ajoute l'icone adéquate en face
                else:
                    img_b = QtGui.QPixmap(dossier_racine + '/icone.png')
                    item = QtGui.QListWidgetItem(self.listWidget_chat)
                    item.setIcon(QtGui.QIcon(img_b))
                    self.listWidget_chat.setIconSize(QtCore.QSize(8, 8))
                    item.setText(liste_utilisateurs[i])

                    # print item, liste_utilisateurs[i]

                    self.listWidget_chat.insertItem(i, item)

        # self.listWidget_chat.setCurrentRow(canal)
        self.listWidget_chat.setCurrentRow(0)

    def deco_irc(self):
        '''On se deconnecte d'IRC'''
        variables.connecte = 0
        try:
            self.th_irc.deco()
        except AttributeError:
            pass
        time.sleep(0.1)
        try:
            # Ferme le thread du client IRC:
            # if self.th_c.isAlive:
            self.th_irc._Thread__stop()
        except AttributeError, x:
            pass
            # print x
        time.sleep(0.1)


class connexion_IRC(threading.Thread):

    def __init__(self, serveur="irc.freenode.com", canaux=["#djl"], port=6667, pseudo="nul"):
        '''Thread, connexion au serveur IRC et aux canaux'''
        self.serveur = serveur
        self.port = port
        self.conn = DialogueServeurIRC(canaux)

        # Si on a pas de pseudo, on en trouve un aléatoire
        if pseudo == "nul":
            import random
            self.pseudo = "djl-" + str(random.randint(1, 99999))
        else:
            self.pseudo = pseudo

        threading.Thread.__init__(self)

    def run(self):
        '''Envoi la connexion'''
        #self.conn = DialogueServeurIRC(canaux)
        try:
            self.conn.connect(self.serveur, self.port, self.pseudo)
        except irclib.ServerConnectionError, x:
            print "Impossible de se connecter"
            print x
        self.conn.start()  # On demarre la boucle

    def envoi(self, message, canal):
        '''Envoi un message sur IRC'''
        self.conn.envoi(message, canal)

    def deco(self):
        '''On se deconnecte d'IRC'''
        self.conn.deco()


class DialogueServeurIRC(irclib.SimpleIRCClient):

    def __init__(self, canaux):
        '''Dialogue avec la librairie irclib et le client de djl'''
        irclib.SimpleIRCClient.__init__(self)
        self.canaux = canaux

    def on_welcome(self, connection, event):
        '''Evenement: On vient de se connecter'''
        # On parcours la liste des canaux pour les rejoindre.
        for i in range(len(self.canaux)):
            if irclib.is_channel(self.canaux[i]):
                connection.join(self.canaux[i])

    # def on_disconnect(self, connection, event):
        #'''Evenement: On vient de se deconnecter'''
        # print "Deconnecté"
        # pass

    def on_pubmsg(self, connection, event):
        '''Evenement: On vient de recevoir un message'''
        #recoi_irc > ["texte", "canal",  "source"]
        variables.recoi_irc = [
            event.arguments(), event.target(), self.split_source(event.source())]

    def on_namreply(self, connection, event):
        '''Evenement: On vient de recevoir la liste des utilisateurs'''
        liste = event.arguments()[2].split(' ')
        canal = event.arguments()[1].lower()
        variables.liste_utilisateurs[canal] = liste

        # print "Liste des utilisateurs:",  str(liste)

    def on_join(self, connection, event):
        '''Evenement: Un utilisateur vient de joindre le canal'''

        # print "Join: Canal:",  str(event.target()),  "utilisateur:",
        # self.split_source(event.source())

        variables.even_irc = ["join", event.target().lower(), self.split_source(event.source())]
        # try:
            # print ">>>Nombre d'utilisateurs sur le canal",  str(event.target().lower()) + ":",  str(len(variables.liste_utilisateurs[event.target().lower()]))
        # except KeyError:
            # pass

        if variables.connecte == 0:
            variables.connecte = 1

    def on_part(self, connection, event):
        '''Evenement: Un utilisateur vient de partir du canal'''

        # print "Part: Canal:",  str(event.target()),  "utilisateur:",
        # self.split_source(event.source())

        variables.even_irc = ["part", event.target().lower(), self.split_source(event.source())]
        # try:
            # print ">>>Nombre d'utilisateurs sur le canal",  str(event.target().lower()) + ":",  str(len(variables.liste_utilisateurs[event.target().lower()]))
        # except KeyError:
            # pass

    def on_quit(self, connection, event):
        '''Evenement: Un utilisateur vient de quitter le serveur'''
        # print "Quit: utilisateur:", self.split_source(event.source())
        variables.even_irc = ["quit", None, self.split_source(event.source())]

    def envoi(self, message, canal):
        '''Envoi le message donné sur le canal'''
        # print "Envoi..."
        self.connection.privmsg(canal, message)

    def on_nicknameinuse(self, message, canal):
        '''Le pseudo semble déjà utilisé'''
        variables.even_irc = ["err_pseudo", "", ""]

    def deco(self):
        '''On demannde la deconexion'''
        try:
            self.connection.disconnect()
            # self.connection.send_raw("quit")
        except irclib.ServerNotConnectedError, x:
            pass
            # print x

    def split_source(self, source):
        '''Renvoi uniquement le pseudo de la source IRC données'''
        return source.split("!")[0]
