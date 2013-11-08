# -*- coding: utf-8 -*-*

# djl (Dépot jeux Linux)
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

'''Code qui s'occupe du téléchargement, de l'installation et le lancement des jeux'''

import urllib
import os
import shutil
import subprocess
import time
import threading
import tarfile
import zipfile
from cStringIO import StringIO  # Nouvelle methode zipfile

from config import config
from variables import variables, dossier_racine, home
import gdep  # , i18n
import interface

import i18n
# i18n.i18n_init()

try:
    from PyQt4 import QtCore, QtGui
except:
    print _('Erreur lors de l\'import des librairies, vous devez installer le paquet python-qt4')

# Modifi le user-agent:


class Modif_URLopener(urllib.FancyURLopener):
    version = "djl (Depot jeux linux)/Linux"
urllib._urlopener = Modif_URLopener()

#import diff


class Annule(Exception):
    pass


class Telechargement(threading.Thread):

    def __init__(self, lien_telechargement, nom_archive, nom_jeu, commande, version):
        '''Télécharge le jeu voulu dans un processus léger'''
        threading.Thread.__init__(self)
        self.stop = False

        self.lien_telechargement = lien_telechargement
        self.nom_archive = nom_archive
        self.nom_jeu = nom_jeu

        self.commande_jeu = commande  # Sera ensuite utilisé pour l'installation
        self.version = version  # Pareil /\

        self.taille_fichier = 1
        self.nb_blocs = 0
        self.taille_bloc = 0

        print lien_telechargement

    def run(self):
        '''Appelé lors de l'__init__() du Thread'''
        try:
            # Le téléchargement est lancé ici:
            # print self.lien_telechargement
            urllib.urlretrieve(
                self.lien_telechargement,
                filename=(config(info=2) + '/jeux/') + self.nom_archive,
                reporthook = self.reporthook)
        except Annule:
            # print _('Telechargement annule')
            return  # On quitte la fonction, sinon l'installation sera lancé après !
        except:
            self.annule = True
        time.sleep(1)
        # Lance l'installation (Sans forcément lancer dans un nouveau Thread):
        inst = installe(self.nom_archive, self.nom_jeu, self.commande_jeu, self.version)
        inst.run()

    def reporthook(self, nb_blocs, taille_bloc, taille_fichier):
        '''A chaque téléchargement de bloc, on met à jours les variables pour pouvoir rafraichir la fenêtre de téléchargement'''

        # Si on stop le téléchargement, lève une exception (Annule) pour fermer le thread:
        if self.stop == True:
            raise Annule

        if self.taille_fichier == 1:
            self.taille_fichier = taille_fichier

        if self.taille_bloc == 0:
            self.taille_bloc = taille_bloc

        self.nb_blocs = nb_blocs

        # Converti la taille de l'archive Octets > Mo (la valeure est arrondie à l'unité, on est pas à 500Ko près):
        #variables.taille_archive =  (taille_fichier)/1048576

    def renvoi_infos(self):
        '''Renvoi les informations qui vont bien pour pouvoir être accessible au processus léger de téléchargement'''
        return (self.nb_blocs, self.taille_bloc, self.taille_fichier)

    def annule(self):
        '''Fonction pour annuler le téléchargement, il sera stoppé au prochain lancement de reporhook...'''
        self.stop = True


class installe(threading.Thread):

    def __init__(self, nom_archive, nom_jeu, commande_jeu, version):
        '''Installe localement le jeu qui vient d'être téléchargé'''
        threading.Thread.__init__(self)

        self.nom_archive = nom_archive
        self.nom_jeu = nom_jeu
        self.commande_jeu = commande_jeu
        self.version = version

    def run(self):
        '''Appelé lors de l'__init__() du Thread'''
        # Petit temps d'attente pour s'assurer que l'archive soit bien téléchargé (il peut y avoir des problèmes avec les grosses archives)
        # time.sleep(2)
        # On utilise: variables.installe
        # Trouve l'adresse de l'archive:
        addr_archive = config(info=2) + '/jeux/' + self.nom_archive
        nom_fichier = self.nom_archive

        # On a le fichier, trouve le type de fichier pour le décompresser
        ext_fichier_1 = nom_fichier.split('.')[-2]
        ext_fichier_2 = nom_fichier.split('.')[-1]

        tar_gz = 0

        # Si il s'agit d'une archive tar:
        if ext_fichier_1 == 'tar':
            try:
                # Créé le dossier pour le jeu:
                os.mkdir(config(info=2) + '/jeux/' + self.nom_jeu)
            except OSError:
                print i18n.traduc_ascii("Le dossier de l'archive n'a pas ete cree")

            # Si c'est un archive tar.bz2:
            if ext_fichier_2 == 'bz2':
                fichier_tar = tarfile.open(addr_archive, 'r:bz2')
            # Si c'est une archive tar.gz
            if ext_fichier_2 == 'gz':
                fichier_tar = tarfile.open(addr_archive, 'r:gz')
            tar_gz = 1

        # print ext_fichier_2

        # Si il s'agit d'une archive zip:
        if ext_fichier_2 == 'zip':
            nom_dossier = self.nom_jeu
            try:
                # Créé un dossier pour le jeu:
                repertoire = config(info=2) + '/jeux/' + self.nom_jeu
                os.mkdir(repertoire)
            except:
                print i18n.traduc_ascii("Le dossier de l'archive n'a pas ete cree")
            try:
                self.extrait_zip(addr_archive, repertoire)
            except MemoryError, x:
                print x
            #
            #dossier = ''
            # try:
                #fichier_zip = zipfile.ZipFile(addr_archive, 'r')
            # except zipfile.BadZipfile:
                # print "Problème lors de l'extraction, l'archive du jeu sera supprimée"
                # supprime_archive(self.nom_archive)
                # return
                #
            # for filename in fichier_zip.namelist():
                #
                # Créé l'arborescence des fichiers:
                # if '/' in filename:
                    #filename_p = filename
                    #dossier_p = filename_p.split('/', -1)
                    # print '>>>>>>>>>>>', dossier_p
                    #nb_sous_dossiers = len(dossier_p)
                    # dossier=''
                    #dossier_ancien = ''
                    #boucle_t = 0
#
                    # while boucle_t < nb_sous_dossiers-1:
                        # if dossier != '':
                            #dossier = dossier_ancien + '/' + dossier_p[boucle_t]
                        # else:
                            #dossier = dossier_p[boucle_t]
                        #dossier_ancien = dossier
                        # print dossier
                        #
                        # Créé le dossier:
                        # try:
                            #os.mkdir(config(info=2) + '/jeux/' + self.nom_jeu + '/' + dossier)
                        # except:
                            # pass
                            # print "Le dossier n'a pas été créé: ", dossier
                        #
                        # boucle_t=boucle_t+1
                # try:
                    #data = fichier_zip.read(filename)
                # except MemoryError, x:
                    # print x
                    # continue
                #
                # try:
                # Ecrit les données:
                    #file = open(config(info=2) + '/jeux/' + self.nom_jeu + '/' + filename, 'w+b')
                    # file.write(data)
                    # file.close()
                # except IOError: #Si ça merde, c'est qu'il n'arrive pas à extraire un fichier qui est en réalité un dossier.
                    # Donc, on le créé à la main:
                    # try:
                        #os.mkdir(config(info=2) + '/jeux/' + self.nom_jeu + '/' + filename)
                    # except OSError: #Si le dossier existe déjà on annule
                        # pass
                        # print 'Dossier du jeu existant', filename
            # fichier_zip.close()

        # Si l'on a affaire à une archive tgz:
        if ext_fichier_2 == 'tgz':
            fichier_tar = tarfile.open(addr_archive, 'r:gz')
            tar_gz = 1

        # Si c'est une archive tar, tgz, ou bz2, on, décompresse:
        if tar_gz == 1:
            fichier_tar.debug = 1  # Affiche les fichiers pendant la décompression:
            # Attention, la fonction extractall n'est (apparemment) compatible qu'avec
            # Python 2.5 ou supérieur
            try:
                fichier_tar.extractall(config(info=2) + '/jeux/' + self.nom_jeu)
                fichier_tar.close()
            except (IOError, EOFError), x:
                print "Probleme lors de l'extraction:", x
                os.remove(addr_archive)

        # Si c'est un installateur .bin, utilise un shell, avec les options qui
        # vont bien sur l'archive pour le décompresser:
        if ext_fichier_2 == 'bin':
            print addr_archive
            os.system('chmod +x ' + addr_archive)
            os.system(
                addr_archive +
                '  --prefix ' +
                config(
                    info=2) +
                '/jeux/' +
                self.nom_jeu +
                ' --usergroup games --deskcut no --menu no --syswide no --installer-language fr --perms no --mode unattended')

        # Si c'est un installateur "InstallJammer" comme pour Regnum Online:
        if ext_fichier_2 == 'inj':
            os.system('chmod +x ' + addr_archive)
            os.system(
                addr_archive +
                '  --prefix ' +
                config(
                    info=2) +
                '/jeux/' +
                self.nom_jeu +
                ' --mode silent')

        # Si c'est un fichier .package, utilise un shell, avec l'option -x sur
        # l'archive pour la décompresser:
        if ext_fichier_2 == 'package':
            os.system('bash ' + addr_archive + ' -x ' + config(info=2) + '/jeux')

        # Si c'est un fichier.run ('type installateur loki, utilise une commande
        # shell pour décompresser
        if ext_fichier_2 == 'run':
            # Envoi la décompression du jeu dans un répertoire temporaire:
            #os.system('sh ' + addr_archive + ' --target ' + config(info=2) + '/jeux/' +  self.nom_jeu +  ' --noexec')
            #retour = os.popen('sh ' + addr_archive + ' --target ' + config(info=2) + '/jeux/' +  self.nom_jeu +  ' --noexec')
            # print retour.readlines()
            # Lancle l'installation dans un terminal,os.popen ne fonctionne pas chez
            # certains utilisateurs
            if os.path.exists('/usr/bin/xterm'):
                os.popen(
                    'xterm -e sh ' +
                    addr_archive +
                    ' --target ' +
                    config(
                        info=2) +
                    '/jeux/' +
                    self.nom_jeu +
                    ' --noexec')
            elif os.path.exists('/usr/bin/konsole'):
                os.popen(
                    'konsole -e sh ' +
                    addr_archive +
                    ' --target ' +
                    config(
                        info=2) +
                    '/jeux/' +
                    self.nom_jeu +
                    ' --noexec')
            elif os.path.exists('/usr/bin/gnome-terminal'):
                os.popen(
                    'gnome-terminal -e sh ' +
                    addr_archive +
                    ' --target ' +
                    config(
                        info=2) +
                    '/jeux/' +
                    self.nom_jeu +
                    ' --noexec')
            else:
                os.popen(
                    'sh ' +
                    addr_archive +
                    ' --target ' +
                    config(
                        info=2) +
                    '/jeux/' +
                    self.nom_jeu +
                    ' --noexec')

            # Si le fichier utilise bz2, ce n'est pas une archive loki, donc on ne
            # tente pas ce type d'installation
            if ext_fichier_1 == 'bz2':
                try:
                    os.rename(
                        config(info=2) + '/jeux/' + self.nom_jeu + '-tmp',
                        config(info=2) + '/jeux/' + self.nom_jeu)
                except:
                    pass
            else:
                # Envoi la fonction dédié à l'installation des archives loki:
                self.loki_installe(self.nom_jeu)

        # Renomme le dossier décompressé par le nom du jeu:
        if ext_fichier_2 == 'bz2':
            nom_dossier = addr_archive.replace('.tar.bz2', '')
        if ext_fichier_2 == 'gz':
            nom_dossier = addr_archive.replace('.tar.gz', '')
        if ext_fichier_2 == 'tgz':
            nom_dossier = addr_archive.replace('.tgz', '')
        if ext_fichier_2 == 'package':
            nom_dossier = addr_archive.replace('.package', '')
        if ext_fichier_2 == 'run':
            nom_dossier = addr_archive.replace('.run', '')
        if ext_fichier_2 == 'bin':
            nom_dossier = self.nom_jeu
        if ext_fichier_2 == 'inj':
            nom_dossier = self.nom_jeu

        # Tente de renommer le dossier contenant le jeu, par le nom du jeu dans le fichier 'def'
        try:
            if nom_dossier != '':
                os.rename(nom_dossier, config(info=2) + '/jeux/' + self.nom_jeu)
        # Si le dossier existe deja, on ne renomme pas
        except OSError:
            print 'Dossier existant'

        # Le jeu est décompréssé/installé, on supprime ou pas l'archive en
        # fonction de la configuration
        if int(config(info=1)) == 1:
            supprime_archive(self.nom_archive)

        # Le jeu est installé, on peut le lancer, si la configuration le permet
        if int(config(info=0)) == 1:
            th_lance = lance(self.nom_jeu, self.commande_jeu)
            th_lance.start()

        # Demande le rafraichissement de l'interface principale:
        variables.maj_listejeux = True

        # A la fin, modifi l'état du jeu, il doit être installé (etat = 1)
        modif_etat(self.nom_jeu, val_etat=1)

        # On écrit le fichier qui contient la version du jeu dans le dossier du jeu:
        try:
            fichier = config(info=2) + '/jeux/' + self.nom_jeu + '/version'
            fichier_v = open(fichier, 'w')
            fichier_v.write(self.version)
            print fichier, _('ecrit')
            fichier_v.close()
        except:
            print i18n.traduc_ascii("Le fichier de version n'a put etre ecrit")

        # On a terminé l'installation, on le signale
        variables.installe[self.nom_jeu] = True

    def extrait_zip(self, fichier, destination):
        '''Extrait dans le répertoire de destination l'archive zip donnée en argument
        Récupéré depuis cette source: http://code.activestate.com/recipes/465649/
        Semble fonctionner pour les grosses archives zip, contrairement à ma première fonction.'''

        zf = zipfile.ZipFile(fichier)
        namelist = zf.namelist()
        dirlist = filter(lambda x: x.endswith('/'), namelist)
        filelist = filter(lambda x: not x.endswith('/'), namelist)
        # make base
        pushd = os.getcwd()
        if not os.path.isdir(destination):
            os.mkdir(destination)
        os.chdir(destination)
        # create directory structure
        dirlist.sort()
        for dirs in dirlist:
            dirs = dirs.split('/')
            prefix = ''
            for destination in dirs:
                dirname = os.path.join(prefix, destination)
                if destination and not os.path.isdir(dirname):
                    os.mkdir(dirname)
                prefix = dirname
        # extract files
        for fn in filelist:
            try:
                out = open(fn, 'wb')
                buffer = StringIO(zf.read(fn))
                buflen = 2 ** 20
                datum = buffer.read(buflen)
                while datum:
                    out.write(datum)
                    datum = buffer.read(buflen)
                out.close()
            finally:
                print fn
        os.chdir(pushd)

    def loki_installe(self, nom_dossier):
        '''Fonction dédié à l'installation 'transparente' des archives loki (ces derniers étant normalement des installateurs graphiques)'''
        # Prend comme répertoire courant le dossier des jeux
        os.chdir(config(info=2) + '/jeux')
        # On commence par créer le dossier du jeu:
        try:
            os.mkdir(nom_dossier)
        except OSError:
            print i18n.traduc_ascii("Le dossier du jeu n'a pas ete cree (Loki)")

        # On liste les fichiers qui nous interessent:
        liste_fichiers = os.listdir(nom_dossier)

        # On parcours la liste des fichiers pour ne garder que ceux qui nous interessent:
        #boucle_fichiers = 0
        # while boucle_fichiers < len(liste_fichiers):
            # On déplace les fichiers:
            #shutil.move(nom_dossier + '/' + liste_fichiers[boucle_fichiers], nom_dossier + '/' +  liste_fichiers[boucle_fichiers])
            #boucle_fichiers = boucle_fichiers+1

        boucle_fichiers = 0

        # On a les donnés, on va chercher les binaire du jeu:
        try:
            liste_binaires = os.listdir(nom_dossier + '/bin')
        except OSError:
            print nom_dossier + "/bin n'existe pas (ou plus)"
        try:
            while boucle_fichiers < len(liste_binaires):
                try:
                    shutil.move(
                        nom_dossier +
                        '/bin/' +
                        liste_binaires[
                            boucle_fichiers],
                        nom_dossier +
                        '/')
                except:
                    print i18n.traduc_ascii("Attention, un fichier binaire n'a put etre copie, ceci est inherent a la non uniformitee des archives, ca n'est probablement pas trop grave ("), liste_binaires[boucle_fichiers] + ')'

                # On rend le ou les binaires executable:
                try:
                    os.chmod(nom_dossier + '/' + liste_binaires[boucle_fichiers], 0755)
                except OSError:
                    print i18n.traduc_ascii("Le binaire du jeu n'a pas ete rendu executable suite a la levee d'une exception")

                boucle_fichiers = boucle_fichiers + 1
        except UnboundLocalError:
            print i18n.traduc_ascii("Les binaires ont ete ignores")

        boucle_fichiers = 0

         # On finit par décompresser les archives:
        liste_fichiers = os.listdir(nom_dossier)  # On liste tous les fichiers

        while boucle_fichiers < len(liste_fichiers):
            # On tri les archives tar:
            if 'tar' in liste_fichiers[boucle_fichiers]:
                # On décompresse:
                fichier_tar = tarfile.open(
                    config(info=2) + '/jeux/' + nom_dossier +
                    '/' + liste_fichiers[boucle_fichiers],
                    'r')
                fichier_tar.debug = 1  # Affiche les fichiers pendant la décompression:

                # Clause particulière pour le jeu World of padman:
                if nom_dossier == 'worldofpadman' and not 'wop-engine' in liste_fichiers[boucle_fichiers]:
                    fichier_tar.extractall(nom_dossier + '/wop')
                else:
                    fichier_tar.extractall(nom_dossier)

                # On supprime l'archive:
                os.remove(nom_dossier + '/' + liste_fichiers[boucle_fichiers])

            boucle_fichiers = boucle_fichiers + 1

        # On tente de supprimer les dossiers spécifiques aux installations loki
        # (désormais inutiles)
        try:
            os.remove(config(info=2) + '/jeux/' + nom_dossier + '/setup.sh')
        except OSError:
            pass
        try:
            shutil.rmtree(config(info=2) + '/jeux/' + nom_dossier + '/setup.data')
        except OSError:
            pass

        if os.path.exists(config(info=2) + '/jeux/' + nom_dossier + '/bin'):
            liste_bin = os.listdir(config(info=2) + '/jeux/' + nom_dossier + '/bin')
            try:
                liste_bin = liste_bin.remove('.directory')
            except:
                pass

            if len(liste_bin) == 0:
                #shutil.rmtree(dossier_racine + '/jeux/' + nom_dossier + '/bin')
                shutil.rmtree(config(info=2) + '/jeux/' + nom_dossier + '/bin')

        # Retourne dans le dossier racine
        os.chdir(dossier_racine)

        # On a terminé l'installation, on le signale
        variables.installe[self.nom_jeu] = 2

# def creer_fichier_maj():
    #'''Créé un fichier temporaire pour demander le rafraichissement de l'interface principale (djl.py)'''
    # print ">>>>Fichier_MAJ"
    #fichier = home + '/.djl/maj_liste'
    #fichier = open(fichier, 'w')
    # fichier.close()


class lance(threading.Thread):

    def __init__(self, nom_jeu, commande_jeu, dir_jeu="", raccourci=0):
        '''Lance le jeu choisi...'''

        threading.Thread.__init__(self)

        # Définition des variables.
        self.nom_jeu = nom_jeu
        self.commande_jeu = commande_jeu
        self.dir_jeu = dir_jeu
        self.raccourci = raccourci

    def run(self):
        '''Appelé lors de l'__init__() du Thread'''
        # if variables.commande_jeu != '':
            #commande_jeu = variables.commande_jeu
            #nom_jeu = variables.nom_jeu
        # elif variables.commande_jeu_p != '':
            #commande_jeu = variables.commande_jeu_p
            #nom_jeu = variables.nom_jeu_p

        nom_jeu = self.nom_jeu
        commande_jeu = self.commande_jeu
        variables.nom_jeu = nom_jeu

        # On supprime si il y a un espace à la fin (uniquement si il n'y a qu'une
        # commande sans arguments):
        cmd_jeu_tmp = commande_jeu.split()
        if len(cmd_jeu_tmp) == 1:
            commande_jeu = cmd_jeu_tmp[0]

        # print '>'+str(commande_jeu) + '< >' + str(nom_jeu) + '< >' +
        # str(variables.commande_jeu_p)

        # Si c'est lancé depuis un fichier .desktop:
        # if '+desktop' in commande_jeu:
        if self.raccourci == 1:
            # Effectue différents formatages dans la ligne de commande:
            #commande_jeu = commande_jeu.replace(" +desktop", '')
            if "'" in commande_jeu:
                commande_jeu = commande_jeu.replace("'", '')
            if '\n' in commande_jeu:
                commande_jeu = commande_jeu.replace('\n', '')

            # Si le répertoire de lancement du jeu est déjà défini, on l'utilise
            if self.dir_jeu != '' and self.dir_jeu is not None:
                chemin_jeu = self.dir_jeu
            # Sinon, trouve le chemin du répertoire du jeu en fonction de la ligne de commande:
            elif '/' in commande_jeu:
                # L'idée est de prendre le chemin vers le binaire (si il contient '/' et
                # d'utiliser son répertoire parent.
                chemin_jeu_ = commande_jeu.split('/')
                chemin_jeu = ''
                for i in range(len(chemin_jeu_) - 1):
                    chemin_jeu = chemin_jeu + '/' + chemin_jeu_[i]
            else:
                # Sinon, on utilise le réperoire personnel de l'utilisateur
                chemin_jeu = os.path.expanduser('~')

            commande_j = commande_jeu

        else:  # N'effectue ce qui suit que si le jeu en cours a été installé depuis le dépot:
            # Repère le répertoire du jeu, sinon bon nombre de jeux ne se lancent pas,
            # puisqu'ils ne trouvent pas leurs données
            chemin_jeu = (config(info=2) + '/jeux/' + nom_jeu)

            # Liste le nombre de fichiers
            nb_fichier = os.listdir(config(info=2) + '/jeux/' + nom_jeu)

            # Ne prend pas en compte les répertoires 'src'
            if 'src' in nb_fichier:
                nb_fichier.remove('src')
                print i18n.traduc_ascii("dossier 'src' ignore")

            # Ne prend pas en compte les répertoires '.directory'
            if '.directory' in nb_fichier:
                nb_fichier.remove('.directory')
                print i18n.traduc_ascii("fichier '.directory' ignore")

            if 'version' in nb_fichier:
                nb_fichier.remove('version')

            # Si n'y a qu'un fichier/dossier, c'est que nous ne sommes pas dans le
            # répertoire racine du jeu, mais dans son répertoire parent
            if len(nb_fichier) == 1:
                # Donc on prend le bon dossier:
                #chemin_jeu = (dossier_racine + '/jeux/' + nom_jeu + '/' + nb_fichier[0])
                chemin_jeu = (config(info=2) + '/jeux/' + nom_jeu + '/' + nb_fichier[0])

            # Créé la ligne de commande finale avec le chemin complet jusqu'au binaire/script:
            commande_j = chemin_jeu + '/' + commande_jeu

         # Récupère l'extension du fichier pour déterminer la manière de le lancer
        type_exec = commande_jeu.split('.', -1)
        try:
            type_exec = type_exec[1]
        except:
            type_exec = type_exec[0]

        # print '>>> ' + str(commande_jeu) + ' lancé !'

        # Journal d'erreurs:
        self.fichier_log = open(home + '/.djl/debog', 'w')
        self.msg = 0
        self.fin = 0

        # Utilisé pour garder l'adresse du binaire, pour le rendre ensuite executable
        commande_jeu_copie = commande_j

        # Si dans le menu configuration on a choisi de lancer le jeu dans un nouveau serveur X:
        if int(config(info=8)) == 1:
            #self.log_x=open('/dev/null', 'w')
            self.log_x = open(home + '/.djl/log_x', 'w')
            # Si le vérrou du serveur X :1 existe déjà, on utilise le port :2
            if os.path.exists('/tmp/.X1-lock'):
                no_x = 2
            else:
                no_x = 1

            # Lance le serveur graphique avec le port adéquat.
            self.x = subprocess.Popen(
                'X :' + str(no_x),
                executable=None,
                shell=True,
                cwd=home,
                stdout=self.log_x,
                stderr=self.log_x)
            # Modifi la commande du jeu pour lancer le processus dans le bon serveur graphique:
            commande_j = 'export DISPLAY=:' + str(no_x) + ' && ' + commande_j
            type_exec = ''

        # print '>>>', type_exec, chemin_jeu

        # Code gestion des dépendances (avant de lancer le jeu)
        # Si il y a un sous-répertoire lib ou libs, on l'utilise pour gérer les dépendances:
        liste_fichiers = os.listdir(chemin_jeu)

        if os.path.exists('/opt/lib32/lib'):  # Répertoire des librairies 32 bits sur Archlinux
            LIBRARY_PATH = "/opt/lib32/lib"
        else:
            # Créé la chaine qui contiendra les répertoires contenant les dépendances:
            LIBRARY_PATH = ""

        # if os.uname()[4] != 'x86_64': #Vérifi que l'on ne tourne pas sur x86_64
        if "lib" in liste_fichiers:
            LIBRARY_PATH = LIBRARY_PATH + ":" + chemin_jeu + "/lib"
        elif "libs" in liste_fichiers:
            LIBRARY_PATH = LIBRARY_PATH + ":" + chemin_jeu + "/libs"
        # Ajoute le répertoire du jeu pour chercher les librairies
        LIBRARY_PATH = LIBRARY_PATH + ":" + chemin_jeu

        # print "1:"
        #os.system("echo $LD_LIBRARY_PATH")

        # Si l'on utilise le paquet de librairies (pour les dépendances) fourni
        # par djl, on l'ajoute à la chaine LIBRARY_PATH:
        if os.path.exists(config(info=2) + "/libs") == True:
            LIBRARY_PATH = LIBRARY_PATH + ":" + config(info=2) + "/libs"

        # Les libraires du systèmes ne sont pas prioritaires sur les librairies fournis par les jeux ou djl:
        #LIBRARY_PATH = LIBRARY_PATH + ":/usr/lib"

        # print LIBRARY_PATH
        # Envoi la configuration de l'environnement pour les librairies avec la chaine créé

        os.putenv("LD_LIBRARY_PATH", LIBRARY_PATH)
        # print os.popen("echo $LD_LIBRARY_PATH").read()

        # print "2:"
        #os.system("echo $LD_LIBRARY_PATH")
        # /Code gestion des dépendances (avant de lancer le jeu)

        # Lance ici le jeu, en fonction que ça soit un script python, sh ou binaire:
        # Si la commande est un script python:
        if type_exec == 'py':
            # os.chdir(chemin_jeu)
            #os.system('python2 ' + commande_j)
            self.p = subprocess.Popen(
                'python2 ' + str(commande_j),
                executable=None,
                shell=True,
                cwd=chemin_jeu,
                stderr=self.fichier_log,
                stdout=self.fichier_log)
            # Lance un timer qui analisera l'état du jeu, afin de repérer les anomalies:
            self.chrono()

            os.chdir(dossier_racine)
            #subprocess.Popen(commande_j, executable = 'python', shell=True, cwd=chemin_jeu)

        # Si c'est un script shell:
        elif type_exec == 'sh':
            try:
                os.chmod(commande_j, 0755)
            except OSError:
                pass
                # print 'Le fichier n\'a pas été rendu exécutable'

            self.p = subprocess.Popen(
                commande_j,
                executable=None,
                shell=True,
                cwd=chemin_jeu,
                stderr=self.fichier_log,
                stdout=self.fichier_log)

            # Lance un timer qui analisera l'état du jeu, afin de repérer les anomalies:
            self.chrono()

        # Sinon, on part du principe que c'est un binaire
        else:
            # Rend le fichier executable, au cas où...
            try:
                os.chmod(commande_jeu_copie, 0775)
            except OSError:
                # print i18n.traduc_ascii("Le fichier n'a pas ete rendu executable") +
                # ':',  commande_j
                pass

            # Si il y a d'autre fichiers binaires dans le répertoire, on les rend
            # executables, (le script est suceptible de les utiliser)
            liste_exec = os.listdir(chemin_jeu)

            for i in range(len(liste_exec)):
                # print liste_exec[i]
                # try:
                if '.bin' in liste_exec[i]:
                    # print '>>>>>>>>>>>>>>>>'
                    os.chmod(chemin_jeu + '/' + liste_exec[i], 0775)
                # except OSError:
                    # pass

            # Lance la commande:
            # temp:
            # print '>>>' + commande_j + '<<<'
            #self.p=subprocess.Popen(commande_j, cwd=chemin_jeu, stderr=None, stdout=None)
            # Lance un timer qui analisera l'état du jeu, afin de repérer les anomalies:
            # self.chrono()
            #

            try:
                self.p = subprocess.Popen(
                    commande_j,
                    cwd=chemin_jeu,
                    stderr=self.fichier_log,
                    stdout=self.fichier_log)
                # Lance un timer qui analisera l'état du jeu, afin de repérer les anomalies:
                self.chrono()
            except:
                # try:
                self.p = subprocess.Popen(
                    commande_j,
                    cwd=chemin_jeu,
                    executable=None,
                    shell=True,
                    stderr=self.fichier_log,
                    stdout=self.fichier_log)
                self.chrono()
                # except:
                    # print "Popen n'a put lancer le jeu, os.system sera utilisé"
                    #os.system('cd ' + chemin_jeu + ' & ' + commande_j)

    def chrono(self):
        '''Envoi la recherche toutes x secondes d'anomalies quand on lance un jeu'''
        chrono = 0.5
        if self.fin == 0:
            # print "Boucle", str(self.p.poll())
            self.t = threading.Timer(chrono, self.retour)
            self.t.start()

    def retour(self):
        '''Vérifi si le jeu ou le serveur graphique n'a pas planté en parsant la sortie du jeu.'''
        if self.p.poll() is not None:
            # Si ça plante (jeu)...
            if int(self.p.poll()) > 0:
                self.fichier_log.close()
                self.fin = 1
                variables.erreur = 1

        # Si le second serveur x plante:
        try:
            if int(config(info=8)) == 1 and self.x.poll() is not None:
                self.log_x.close()
                variables.erreur = 2

                self.fin = 1
                print _('Serveur X plante')
        except TypeError, x:
            print x

        # Si le fichier de débogage a changé de taille (de nouvelles lignes sont ajoutés), on part du principe qu'il y a de nouveaux événéements
        # Si il a un message d'erreur, il n'apparait qu'une fois grace à la variables self.msg
        taille = os.stat(home + '/.djl/debog')[6]
        if int(taille) != 0 and self.msg == 0:
            # Ne lance la boite de dialogue uniquement si le serveur graphique n'a pas déjà planté.
            if self.fin != 1:
                variables.erreur = 1
                self.msg = 1

        # Quand le jeu est fini (application terminée), on ferme le serveur graphique (si la configuration a demandé son lancement):
        # if int(config(info=8)) == 1 and self.p.poll() == 0 :
        if self.p.poll() == 0:
            if int(config(info=8)) == 1:
                try:
                    os.kill(self.x.pid, 2)
                    self.fin = 1
                except:
                    pass
        else:
            # Sinon, tant que l'application tourne, on relance la boucle
            self.chrono()

        # Affiche l'état du processus (jeu)
        # print self.p.poll()


class erreur_x11():

    def __init__(self):
        '''Boite de dialogue qui s'affiche quand le serveur X plante'''
        # QtGui.QMessageBox.__init__(self)

        self.log_x = open(home + '/.djl/log_x', 'r')
        txt_log = self.log_x.read()

        txt = i18n.traduc("Le serveux X a plante, voici le message d'erreur.\n")

        if 'user not authorized to run the X server' in txt_log:
            suggestion = i18n.traduc(
                "\nVous n'avez pas les droits necessaires pour lancer un second serveur X. \nSur les systemes bases sur Debian, vous pouvez regler le probleme en lancant:\n 'dpkg-reconfigure x11-common' \n Et permettre a tout le monde de lancer X11.")
        else:
            suggestion = ''

        # Envoi une boite de dialogue:
        texte = i18n.encode(txt) + i18n.encode(txt_log) + i18n.encode(suggestion)
        #QtGui.QMessageBox.information(self, titre, texte)
        interface.info_box(texte, i18n.traduc("Le serveux X a plante"))


class msg_erreur():

    def __init__(self):
        '''Boite de dialogue qui s'affiche quand un jeu plante (Avec si possible une suggestion ainsi que les dernières lignes de la sortie standard du jeu'''
        fichier_log = open(home + '/.djl/debog', 'r')

        titre = i18n.traduc("Erreur lors du lancement du jeu")
        texte_log = str(fichier_log.read())

        # Variables pour n'afficher la boite de dialogue que quand c'est nécessaire:
        mesg = 0

        # Si la variable passe à 1, c'est qu'il manque une librairie, djl tentera de la télécharger
        fgest = False

        if str(texte_log) != '':
            texte = i18n.traduc("Une erreur s'est produite avec ") + \
                variables.nom_jeu + \
                i18n.traduc(". \nVoici le message d'erreur: \n")
        else:
            texte = _('Le jeu ') + variables.nom_jeu + \
                i18n.traduc(
                    " n'a put etre lance correctement. Merci de lire les eventuels messages d'erreur dans le terminal et rapporter le bogue au developpeur.")

        suggestion = ''

        if 'Wine failed with return code' in str(texte_log):
            suggestion = i18n.traduc("\n Wine n'a put lancer le jeu.")
            mesg = 1

        elif 'ALSA lib pcm_dmix.c:996:(snd_pcm_dmix_open) unable to open slave' in str(texte_log):
            texte_log = 'ALSA lib pcm_dmix.c:996:(snd_pcm_dmix_open) unable to open slave'
            suggestion = _('\n La carte son est probablement occupee par un autre processus.')
            mesg = 1

        elif 'Device or resource busy' in str(texte_log):
            suggestion = _('\n La carte son est probablement occupee par un autre processus.')
            mesg = 1

        elif 'X Error of failed request:' in str(texte_log):
            mesg = 1

        elif "Traceback (most recent call last)" in str(texte_log):
            mesg = 1

        # Si le message d'erreur contient 'ImportError', c'est que nous lancons un
        # script python auqul il manque une librairie:
        elif 'ImportError:' in str(texte_log):
            if 'No module named' in str(texte_log):
                liste_texte = texte_log.split('\n')
                boucle = 0
                while boucle < len(liste_texte):
                    if 'ImportError' in liste_texte[boucle]:
                        nom_lib = liste_texte[boucle]
                        break
                    else:
                        nom_lib = ''
                    boucle = boucle + 1

                if nom_lib != '':
                    suggestion = nom_lib.split()
                    suggestion = suggestion[len(suggestion) - 1]

                    suggestion = i18n.traduc(
                        "\n Solution possible, installer la librairie python '") + str(suggestion) + "'"
                mesg = 1

        elif "PNG header and library versions do not match" in texte_log:
            mesg = 1

        # Pour les jeux LGP
        elif "This beta has expired" in texte_log:
            mesg = 1

        elif "not found (required by" in texte_log:
            if ".so" in texte_log:
                suggestion = "\n" + \
                    i18n.traduc(
                        "C'est probablement une incompatibilite entre librairies partages.")
            mesg = 1

        elif ": command not found" in texte_log:
            mesg = 1

        elif "error while loading" in texte_log or "Failed to load" in texte_log:
            # Si le binaire (x86) plante parce qu'il n'a qu'une librairie x64 à se
            # mettre sous la dent.
            if "wrong ELF class: ELFCLASS" in texte_log:
                fgest = True
                liste_texte = texte_log.split()
                for i in range(len(liste_texte)):
                    if '.so' in liste_texte[i]:
                        nom_lib = liste_texte[i].replace(':', '')
                        break
                if config(info=17) == 1:
                    suggestion = i18n.traduc(
                        "djl va tenter de trouver la librairie") + ': ' + nom_lib
                else:
                    suggestion = i18n.traduc(
                        "\n Solution possible, installer la librairie ") + nom_lib

                # On affiche le message que si la librairie n'existe pas
                if not os.path.exists(config(info=2) + "/libs/" + nom_lib):
                    mesg = 1

            # Si le message d'erreur contient 'No such file...', c'est qu'une librairie manque. On va l'extraire du message d'erreur
            # Afin de suggérer à l'utilisateur de l'installer:
            elif 'No such file or directory' in texte_log:
                if '.so' in str(texte_log):
                    fgest = True
                    liste_texte = texte_log.split()
                    boucle = 0
                    # Boucle pour parcourir l'enssemble du message d'erreur et trouver le nom
                    # de la librairie manquante
                    while boucle < len(liste_texte):
                        if '.so' in liste_texte[boucle]:
                            nom_lib = liste_texte[boucle]
                            print "1>", nom_lib
                            break
                        boucle = boucle + 1

                    # On applique des traitement sur la variables 'librairie', afin de
                    # supprimer les caractère inutiles:
                    librairie = nom_lib.split('.')
                    version = librairie[len(librairie) - 1]
                    if ':' in version:
                        version = version.replace(':', '')

                    # Parcours la liste contenant le nom de la librairie
                    # Si il y a un élément vide, on le supprime
                    # print librairie, str(len(librairie))
                    librairie_copie = librairie
                    librairie = []
                    for id in range(len(librairie_copie)):
                        # print librairie_copie[id], str(id)
                        if librairie_copie[id] != "":
                            librairie.append(librairie_copie[id])

                    if 'lib' in librairie[0]:
                        librairie = librairie[0].replace('lib', '')
                    else:
                            librairie = librairie[0]

                    # Vérifi si la version est bien un nombre:
                    try:
                        version = int(version)
                    except:
                        version = i18n.traduc("introuvable")

                    #suggestion = i18n.traduc("\n Solution possible, installer la librairie ") + str(librairie) + _(', version ') + str(version) + '.'
                    if config(info=17) == 1:
                        suggestion = i18n.traduc(
                            "djl va tenter de trouver la librairie") + ': ' + nom_lib.replace(':',
                                                                                              '')
                    else:
                        suggestion = i18n.traduc(
                            "\n Solution possible, installer la librairie ") + nom_lib.replace(':',
                                                                                               '')
                    mesg = 1
            else:
                mesg = 1

        elif 'open /dev/sequencer or /dev/snd/seq' in str(texte_log):
            #suggestion = '\nLa carte son est mal configurée ou occupée par un autre processus.'
            mesg = 0

        elif "open /dev/[sound/]dsp: No such file or directory" in str(texte_log):
            mesg = 0

        # Si c'est un problème que l'on ne connait pas, on affiche rien
        else:
            mesg = 0  # modif 0>>1

        # else:
            #suggestion = ''

        if mesg == 1:
            # Envoi l'affichage de la boite de dialogue
            message = texte + "\n" + texte_log

            # Si le message d'erreur fais plus de x charactères, on le coupe.
            x = 700
            if len(message) > x:
                message2 = ""
                for i in range(x):
                    message2 = message2 + message[i]
                message = message2 + "..."

            suggestion = suggestion + "\n\n" + \
                i18n.traduc(
                    "Pour plus d'informations, vous pouvez consulter la sortie d'erreur du jeu dans le menu 'Information/Consulter' la sortie des jeux.")
            texte = message + "\n" + suggestion
            interface.info_box(texte, titre)
            #QtGui.QMessageBox.information(self, titre, texte)

            # Si l'on choisi de lancer le gestionnaire des dépendances après qu'un jeu
            # ait planté parce qu'il manque une librairie.
            if fgest:
                # Récupère la librairie:
                if config(info=17) == 1:
                    gdep.RecupLib(nom_lib.replace(':', ''))

                # Récupère la librairie dans un thread:
                #th = gdep.thRecupLib(nom_lib.replace(':', ''))
                # th.start()


def supprime_archive(nom_archive):
    '''Fonction pour supprimer l'archive du jeu après qu'il soit installé.'''
    archive = config(info=2) + '/jeux/' + nom_archive
    if os.path.exists(archive):
        os.remove(config(info=2) + '/jeux/' + nom_archive)


def modif_etat(nom_jeu, val_etat=0):
    '''Change l'état du jeu (installé ou non)'''
    # print ">>>Modifcation de l'etat", nom_jeu, str(val_etat)
    if nom_jeu != '':
        fichier = config(info=2) + '/etat_jeux/' + nom_jeu
        txt_etat = open(fichier, 'w')
        #etat = txt_etat.write(str(val_etat))
        txt_etat.write(str(val_etat))
        txt_etat.close()
