#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Script de lancement de djl, le vrai client est dans djl_main.py'''

# djl (Dépot jeux Linux)
# Copyright (C) 2008-2009 Florian Joncour - Diablo150 <diablo151@wanadoo.fr
#
# This file is part of djl (Dépot jeux Linux)
#
# [EN]
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

# [FR]
# Ce programme est un logiciel libre: vous pouvez le redistribuer et/ou le modifier
# selon les termes de la "GNU General Public License", tels que publiés par la
#"Free Software Foundation"; soit la version 2 de cette licence ou (à votre choix)
# toute version ultérieure.

# Ce programme est distribué dans l'espoir qu'il sera utile,
# mais SANS AUCUNE GARANTIE, ni explicite ni implicite; sans même les garanties de
# commercialisation ou d'adaptation dans un but spécifique.
# Se référer à la "GNU General Public License" pour plus de détails.

# Vous devriez avoir reçu une copie de la "GNU General Public License"
# en même temps que ce programme; sinon, consulter le site <http://www.gnu.org/licenses/>.

import os
import sys
import time
import urllib
import locale
import socket
import subprocess
import threading

sys.path.append("libs")
# import Fopen #Servira à capturer la sortie de djl
import cPickle
import SOAPpy  # Pour le dépôt en cache

import config

try:
    from PyQt4 import QtGui
except ImportError, x:
    print "Error: You must have python-qt4 libraries installed to run djl, you have to install them with your package manager"
    print "Erreur lors de l\'import des librairies, vous devez installer le paquet python-qt4, merci de l'installer depuis votre gestionnaire de paquets"
    print x
    sys.exit()

home = os.path.expanduser('~')
racine = os.getcwd()

socket.setdefaulttimeout(5)  # Si le serveur ne répond pas après x seconde(s), on passe

# Si le fichier de configuration n'existe pas, on affichera par la suite la fenêtre de configuration au lancement
# if not os.path.exists(home + '/.djl/config'):
    #from configuration import *
# else:
    # Sinon on aura besoin de l'interface principale
    #from djl_main import *

# Serveurs pour le téléchargement des fichiers manquants.
# Actuellement seul les deux premiers serveurs sont pris en compte
serveur_fichiers = ["http://djl-linux.org", "http://djl.jeuxlinux.fr", "http://djl.tuxfamily.org"]

try:
    import i18n
    # i18n.i18n_init()
except ImportError:
    try:
        _
    except NameError:
        def _(s):
            return s

# def trouve_repertoire():
    #'''Trouve le répertoire courant du script (Pour que l'on puisse lancer djl n'importe comment sans problème'''
    # if "/" in sys.argv[0]:
        # liste=sys.argv[0].split("/")
        #script = liste[len(liste)-1]
        #repertoire=sys.argv[0].replace(script, "")
        # print repertoire + " - " + script
        # os.chdir(repertoire) #On se place donc dans le répertoire


def r_date():
    '''Renvoi la date actuelle'''
    t_ = time.localtime()
    secondes = t_[5]
    if secondes < 10:
        secondes = str('0') + str(t_[5])

    t = str(t_[3]) + ':' + str(t_[4]) + ':' + str(secondes) + \
        ' - ' + str(t_[2]) + '/' + str(t_[1]) + '/' + str(t_[0])
    return t


def verif_config():
    '''Fonction pour s'assuer que le fichier de configuration est à jour'''
    fichier = open(home + '/.djl/config', 'r')
    liste_fichier = fichier.readlines()
    fichier.close()

    if len(liste_fichier) < 10:
        fichier = open(home + '/.djl/config', 'a+')
        if not '\n' in liste_fichier[8]:
            fichier.write('\n')
        fichier.write('langue = ' + locale.getdefaultlocale()[0])
        # fichier.write('\n')
        fichier.close()

    if len(liste_fichier) < 11:
        fichier = open(home + '/.djl/config', 'a+')
        fichier.write('\ntype_gui = 1')
        # fichier.write('\n')
        fichier.close()

    if len(liste_fichier) < 12:
        fichier = open(home + '/.djl/config', 'a+')
        fichier.write('\npseudo = ' + str(os.environ["USER"]).capitalize())
        fichier.close()

    if len(liste_fichier) < 13:
        fichier = open(home + '/.djl/config', 'a+')
        fichier.write('\nconn_irc_demarrage = 1')
        fichier.close()

    if len(liste_fichier) < 14:
        fichier = open(home + '/.djl/config', 'a+')
        fichier.write('\nfond_irc = 0')
        fichier.close()

    if len(liste_fichier) < 15:
        fichier = open(home + '/.djl/config', 'a+')
        fichier.write('\ntaille_police = 9')
        fichier.close()

    if len(liste_fichier) < 16:
        fichier = open(home + '/.djl/config', 'a+')
        fichier.write('\ncanaux_IRC = #djl')
        fichier.close()


class avertissement(QtGui.QWidget):

    def __init__(self, titre, message, quitte=0):
        '''Affiche une boite de dialogue avec le titre et texte donné'''
        QtGui.QMessageBox.__init__(self)
        QtGui.QMessageBox.information(self, titre, message)
        if quitte == 1:
            sys.exit()


class main(object):

    def verif_root(self):
        '''Vérifi que ça ne soit pas le root qui lance djl'''

        if home == '/root' or home == '/Root':  # or home == '/home/diablo150': #<< Pour tests
            #app = QtGui.QApplication(sys.argv)
            titre = i18n.traduc("Attention")
            message = i18n.traduc("Using djl as root user is NOT recommended.")
            ui = avertissement(titre, message, quitte=0)
            ui.show()

    def verif_processus(self):
        '''Vérifi si un processus djl n'est pas déjà lancé'''

        processus = os.popen('ps -ef |grep djl_main |grep python')
        retour = processus.readlines()

        retour_final = []
        for i in range(len(retour)):
            if not 'ps -ef' in retour[i]:
                retour_final.append(retour[i])

        if len(retour_final) >= 1:
            app = QtGui.QApplication(sys.argv)
            titre = i18n.traduc("Attention")
            #message=i18n.traduc("djl est deja lance")
            message = i18n.traduc("djl est deja lance")
            avertissement(titre, message, quitte=i)
        # except: pass

    def cree_repertoires(self):
        '''Créé les répertoires indispensables au démarrage de djl (ignore si ils existent dejà)'''
        if not os.path.exists(home + '/.djl'):
            os.mkdir(home + '/.djl')

        if not os.path.exists(home + '/.djl/cache'):
            os.mkdir(home + '/.djl/cache')

    def verif_demarrage(self):
        '''Affiche la fenêtre de configuration si c'est le premier demarrage'''
        print i18n.traduc_ascii("Ceci est le premier lancement de djl")
        # try:
            # verif_config() #Vérifi le fichier de configuration
        # except: pass

        #from configuration import *
        import configuration

        # Envoi l'affichage de la fenêtre de configuration
        app = QtGui.QApplication(sys.argv)
        window = configuration.Ui_Configuration()
        window.show()
        sys.exit(app.exec_())

    def lance(self):
        '''Lance le "vrai" client djl'''

        verif_config()  # Vérifi si le fichier de configuration est à jour

        if os.path.exists("/usr/bin/python2.6") == True:
            commande_python = "python2.6"
        elif os.path.exists("/usr/bin/python2.5") == True:
            commande_python = "python2.5"
        else:
            commande_python = "python"

        commande_python = commande_python + " -O"

        # Si on utilise le paramètre -dev; on réinstalle pour la version de développement
        argument = ""
        # if len(sys.argv) > 1:
            # if str((sys.argv[1])) == '-dev':
        if self.version_dev == 1:
            print ">djl-dev"
            argument = "-dev"
            # Active le mode "verbose" de Python
            #commande_python = commande_python + " -v"

        # Si le code source est dans le répetoire personnel, on le lance dedans:
        if os.path.exists(home + '/.djl/src/djl/djl/djl_main.py'):
            commande = commande_python + " " + home + '/.djl/src/djl/djl/djl_main.py'
            #p=subprocess.Popen(commande_python +" "+ home + '/.djl/src/djl/djl/djl_main.py' + " " + argument, executable=None, shell=True, cwd=str(racine))

        # Sinon on prend le répertoire d'installation de djl:
        else:
            commande = commande_python + " djl_main.py"
            #p=subprocess.Popen(commande_python + ' djl_main.py' + " " + argument, executable=None, shell=True, cwd=str(racine))

        lance_djl(commande, argument)

    def verif_liste_fichiers(self, addr, liste_fichiers):
        '''Parcours la liste des fichiers en ligne et vérifi si ils existent en dur'''
        boucle = 0
        while boucle < len(liste_fichiers):
            liste_fichiers[boucle] = liste_fichiers[boucle].replace('\n', '')
            # Vérifi si les fichiers existent:
            if os.path.exists(racine + '/' + liste_fichiers[boucle]) == False or self.restaure == 1:
                print i18n.traduc_ascii("Le fichier:"), liste_fichiers[boucle], i18n.traduc("est manquant, il sera telecharge")
                # Sinon, on les téléchargent:
                # Si les fichiers sont contenus dans un dossier:
                if '/' in liste_fichiers[boucle]:
                    dossier = liste_fichiers[boucle].split('/')
                    # Vérifi si le dossier n'existe pas déjà
                    # if os.path.exists(racine + '/' + dossier[0]) == False:
                    boucle_ = 0
                    ancienne_var = ''
                    # Créé l'arborescence de fichiers avant le téléchargements:
                    while boucle_ < len(dossier) - 1:
                        # Sinon, on le créé:
                        var = ancienne_var + '/' + dossier[boucle_]
                        try:
                            os.mkdir(racine + '/' + var)
                        except:
                            pass
                        ancienne_var = var
                        boucle_ = boucle_ + 1
                # Télécharge les fichiers:
                urllib.urlretrieve(
                    addr + '/' + liste_fichiers[boucle],
                    filename=racine + '/' + liste_fichiers[boucle],
                    reporthook=None)
            # else: print '>', liste_fichiers[boucle]
            boucle = boucle + 1

    def verif_fichiers(self):
        '''Vérifi si tous les fichiers de djl existent, sinon on les télécharges'''
        connection_ok = 1
        adresse = serveur_fichiers[0] + '/maj_djl/djl/'
        if len(sys.argv) > 1:
            # Si l'on utilise le paramètre -dev, on utilise le serveur de développement:
            # if str((sys.argv[1])) =='-dev':
            if self.version_dev == 1:
                adresse = serveur_fichiers[0] + '/dev/maj_djl/djl/'

        try:
            print ">", serveur_fichiers[0]
            #adresse = serveur_fichiers[0] + '/maj_djl/djl/'
            liste_fichiers = (home + '/.djl/fichiers_djl.tmp')
            urllib.urlretrieve(adresse + 'fichiers_djl', filename=liste_fichiers, reporthook=None)
            liste_fichiers = open(liste_fichiers, 'r')
        except IOError:  # Si ça déconne avec le premier serveur, on essai le second:
            try:
                print ">:", serveur_fichiers[1]
                adresse = serveur_fichiers[1] + '/maj_djl/djl/'
                liste_fichiers = (home + '/.djl/fichiers_djl.tmp')
                urllib.urlretrieve(
                    adresse +
                    'fichiers_djl',
                    filename=liste_fichiers,
                    reporthook=None)
                liste_fichiers = open(liste_fichiers, 'r')
            except IOError:
                print i18n.traduc_ascii("Impossible de se connecter au serveur principal")
                # Si le téléchargement merde, on créé un fichier vide:
                liste_fichiers = open(home + '/.djl/fichiers_djl.tmp', 'w')
                liste_fichiers.close()
                liste_fichiers = open(home + '/.djl/fichiers_djl.tmp', 'r')
                connection_ok = 0

        liste_fichiers = liste_fichiers.readlines()

        if connection_ok == 1 and self.version_dev == 0:
            self.verif_liste_fichiers(adresse, liste_fichiers)

    def l_jeux(self):
        '''Affiche la liste des jeux installés (appelé si on donne -l en argument)'''
        #rep = home + "/.djl/etat_jeux"

        rep = config.config(info=2) + "/etat_jeux"

        rep_racourcis = config.config(info=2) + "/raccourcis"

        try:
            liste = os.listdir(rep) + os.listdir(rep_racourcis)
        except OSError, x:
            print x
            return 0

        if '-l' in sys.argv:  # Si on demande la liste des jeux
            aff = True
        else:
            aff = False

        #liste_installe = []

        # Parcours la liste des fichier d'état
        for i in range(len(liste)):
            if not '.desktop' in liste[i]:  # Si ça n'est pas un raccourcis .desktop
                f = open(rep + '/' + liste[i])
                etat = f.read()
            else:  # Si c'est un raccourcis, on considère qu'il est installé
                etat = '1'
            if etat == '1':  # Si le jeu est installé, on l'ajoute à la liste
                # liste_install.append(liste[i])
                if aff:
                    print liste[i].replace('.desktop', '')  # Si on demande juste de l'afficher...
                else:  # Sinon...
                    # Vérifi si l'argument est un nom de jeu:
                    for it in range(len(sys.argv)):
                        if liste[i] == sys.argv[it] or liste[i] == sys.argv[it] + ".desktop":
                            # Si on le trouve, on le lance puis on quitte djl
                            print ">>>", sys.argv[it]
                            lance_jeu(liste[i])
                            return 1
            if not '.desktop' in liste[i]:
                f.close()
        if aff:
            return 1  # Si on retourne 1, djl quittera

        return 0  # Si rien n'est trouvé, djl se lancera normalement

    def __init__(self):
        '''Initalisation...'''
        self.verif_root()  # Vérifi que ça ne soit pas le root qui lance djl
        # print sys.argv
        if '-aide' in sys.argv:
            print """
    Lancer le script sans argument pour lancer djl.

    Arguments (optionnels):
        -dev: l'utilisateur aura accès aux mises à jours de développement.
        -zconf: Supprime le fichier de configuration ~/.djl/config
        -res: retélécharge tous les fichiers source de djl (uniquement version stable).
            """
            sys.exit()

        # S'occupe de la gestion des jeux en ligne de commande, si un nom de jeu est donné en argument on le lance et on quitte.
        # Si -l est donné en argument, on affiche la liste des jeux et on quitte
        if os .path.exists(home + '/.djl/config'):
            if '-l' in sys.argv:
                if self.l_jeux() == 1:
                    return

        if '-dev' in sys.argv:
            self.version_dev = 1
        else:
            self.version_dev = 0
            if not "-r" in sys.argv:  # Si il y a l'argument -r, c'est un redemarrage.
                self.verif_processus()  # Vérifi qu'un processus djl ne soit pas déjà lancé

        self.cree_repertoires()  # Vérifi que les répertoires indispensables à djl existent bien

        if '-zconf' in sys.argv:
            print "On supprime le fichier de configuration"
            try:
                os.remove(home + '/.djl/config')
            except:
                pass
        if '-res' in sys.argv:
            # Force le téléchargement des fichiers sources (même si ils existent)
            self.restaure = 1
            print "On re-télécharge toutes les sources"
            self.verif_fichiers()

        # Commenter la ligne suivante pour ne pas vérifier au démarrage si tous les fichiers de djl son présents
        # self.verif_fichiers()

        self.cree_repertoires()  # Vérifi que les répertoires indispensables à djl existent bien

        # Maintenant qu'on est sûr d'avoir tous les fichiers, on lance le programme:
        # Si c'est le premier démarrage de djl (le fichier de config n'existe
        # pas), on lance la fenêtre de configuration:
        if not os.path.exists(home + '/.djl/config'):
            self.verif_demarrage()
        else:
            # Sinon on lance l'interface principale dans un processus séparé:
            self.lance()


class lance_djl():

    '''Lance djl, puis capture la sortie d'erreur pour pouvoir afficher un message d'erreur en cas de plantage'''

    def __init__(self, commande, arguments):
        self.commande = commande
        self.arguments = arguments

        self.message = ""
        self.lance()

    def pid_log(self):
        '''Enregistre l'id du processus dans le journal'''

        t = r_date()

        fichier_log = open(home + '/.djl/djl_log.txt', 'w')
        fichier_log.write('>>> ' + str(t) + '\n')
        fichier_log.write('>>> process id:' + str(self.p.pid) + '\n')
        fichier_log.close()

    def parse_err(self, mesg):
        '''Parse le contenu de mesg (qui doit être le texte de la sortie d'erreurs standard sous forme de liste) et renvoi la dernière erreur'''

        retour = ""
        lg = len(mesg)

        for i in range(lg):
            if "Traceback (most recent call last):" in mesg[i]:
                position = i  # Recupère la position du dernier message d'erreur.

        # Créé la sortie en recupérant les donnés depuis la position du dernier
        # message d'erreur jusqu'a la fin de la liste
        while(position < lg):
            retour += mesg[position]
            position += 1
        return retour

    def c_err(self):
        '''Recherche une éventuelle exception dans la sortie d'erreur'''

        app = QtGui.QApplication(sys.argv)
        nb_err_copie = 0

        while (1):
            # Compte le nombre d'erreurs reperés dans le fichier:
            nb_err = 0

            f = open(home + '/.djl/stderr', 'r')
            fichier = f.readlines()

            for it in range(len(fichier)):
                if "Traceback (most recent call last):" in fichier[it]:
                    nb_err += 1

            # Si le nombre d'erreurs reperés dans le fichier diffère du nombre
            # d'erreurs déjà affichés, on affiche un message d'erreur avec le contenu
            # de la sortie d'erreur.
            if nb_err_copie != nb_err:
                msg_err = self.parse_err(fichier)
                chaine = msg_err + '\n' + \
                    i18n.traduc("Merci de rapporter le probleme au developpeur.")
                #message = QtGui.QApplication.translate("MainWindow", chaine, None, QtGui.QApplication.UnicodeUTF8)

                print msg_err

                avertissement("stderr " + r_date(), chaine, 0)
                nb_err_copie = nb_err
            f.close()

            # Si djl est fermé on quitte la boucle et donc le thread
            if self.p.poll() is not None:
                break

            time.sleep(1)

    def lance(self):
        '''Lance djl dans un sous processus'''
        self.f_err = open(home + '/.djl/stderr', 'w')

        # Lance le processus de djl.
        self.p = subprocess.Popen(
            self.commande + " " + self.arguments,
            executable=None,
            stdin=None,
            stdout=None,
            stderr=self.f_err,
            shell=True,
            cwd=str(racine))

        self.pid_log()  # Enregistre l'id du processus dans le journal

        self.c_err()

       # Envoi la capture des messages d'erreurs, avant de lancer djl:
       #th = threading.Thread(name=None, target=self.c_err)
       # th.start()

       # while (1):
           #etat = th.isAlive()
           # time.sleep(1)
           # if etat == 0:
               # print "Etat du thread: %i" % (etat)
               # break

       # ret = self.p.wait() #Attends que le processus se termine.


class lance_jeu(object):

    '''Lance le jeu donné en argument indépendamment de djl (pour être utilisé en ligne de commande)'''

    def __init__(self, nom_jeu):
        #self.fichier_cache = config.config(info=2) + '/cache/liste_jeux.txt'
        self.fichier_cache = config.config(info=2) + '/cache/liste_jeux.cPickle'
        self.nom_jeu = nom_jeu

        # Si c'est un raccourci .desktop:
        if '.desktop' in nom_jeu:
            # print "Raccourci .desktop"
            raccourci = 1
            retour = [None, None]  # Argument 0: répertoire, 1: commande de lancement
            # Lit le raccourci pour récupérer le répertoire de lancement et la commande
            self.lit_raccourcis(config.config(info=2) + '/raccourcis/' + nom_jeu, retour)
            repertoire = retour[0]
            cmd = retour[1]
        else:  # Si c'est un jeu du dépôt...
            raccourci = 0
            repertoire = nom_jeu
            if os.path.exists(self.fichier_cache):  # memo
                cmd = self.pcmd()
            else:
                return

        # Lance le jeu
        self.lance(repertoire, cmd, raccourci)

    def lit_raccourcis(self, fichier, retour):
        cfichier = open(fichier, 'r')
        tf = cfichier.readlines()
        cfichier.close()

        for i in range(len(tf)):
            # print tf[i].replace('\n', '')
            tf[i] = tf[i].replace('\n', '')
            if "Path=" in tf[i]:
                retour[0] = tf[i].split('=')[-1]
            elif "Exec=" in tf[i]:
                retour[1] = tf[i].split('=')[-1]

        # Si on a pas trouvé la comande de lancement, on ferme
        if retour[1] is None:
            print "Failed to launch the .desktop shortcut"

    def lance(self, repertoire, cmd, raccourci):
        '''Lance le jeu'''
        from installe import lance
        th_lance = lance(repertoire, cmd, "", raccourci)
        th_lance.start()

    def pcmd(self):
        '''Trouve la commande de lancement dans le cache du dépôt, en utilisant cPickle'''
        fichier = open(self.fichier_cache, 'r')
        liste = [cPickle.load(fichier)]
        fichier.close()

        # Parcours le fichier de cache
        for i in range(len(liste[0])):
            # Si le nom du jeu correspond avec le nom dans le cache:
            if liste[0][i]['value'][0][2]['value'] == self.nom_jeu:
                cmd = liste[0][i]['value'][0][4]['value']
                return cmd

   # def pcmd(self):
       #'''Trouve la commande de lancement dans le cache du dépôt, en utilisatant liste_jeux.txt'''
       #fichier = open(self.fichier_cache, 'r')
       #liste = fichier.readlines()
       # fichier.close()

       # Parcours le fichier de cache
       # for i in range(len(liste)):
           #sliste = liste[i].split(';')
           #nom_jeu = sliste[2]
           # Si le nom du jeu correspond avec le nom dans le cache:
           # if self.nom_jeu == nom_jeu:
               # Récupère la commande dans le fichier de cache la retourne
               #cmd = sliste[4]
               # return cmd

if __name__ == "__main__":
    main()
