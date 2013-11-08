#!/usr/bin/env python
# coding: utf-8

# Fopen
# Copyright (C) 2009 Florian Joncour - Diablo150 <diablo151@wanadoo.fr
#
# This file is the source code of Fopen, a fake object file for Python
#
# Fopen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fopen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

# Make a list as fake object file, usefull for (in exemple) get the stdout on a list (see the test function).
# Créé une liste comme un faux objet fichier, peut être utilisé (par
# exemple) pour récupérer la sortie standard dans une liste (voir la
# fonction test).

# Only open, write, read, readlines and close function are available.
# Seul les methodes open, write, read, readlines et close s'appliquent


# A faire: Support unicode

class Fopen(object):

    def __init__(self, nom='nom_fichier.txt', mode='w'):
        self.DEBOG = False  # Affiche ou non les messages de deboguage
        # Liste, contiendra tout ce qu'on voudra écrire dans l'objet fichier fictif
        self.liste = []

        self.nom = nom
        self.mode = mode

        # Malgré le fait que l'on récupère les donnés dans une liste, on écrit
        # également dans un fichier ("a l'ancienne")
        # Si le nom de fichier vaut None, on écrit pas les donnés dans un fichier,
        # sinon on le fait.
        if self.nom:
            try:
                self.fok = True
                self.fichier = open(nom, mode)
            except IOError, x:
                self.fok = False
                print x
        else:
            self.fok = False

        if self.DEBOG:
            sys.stderr.write("Fopen.open(%s, '%s')\n" % (self.nom, self.mode))

        # return self.liste

    def write(self, txt):
        '''Ajoute les donnés dans la liste et les écris sur le fichier'''
        if self.DEBOG:
            sys.stderr.write('Fopen.write(%s)\n' % (txt))
        self.liste.append(txt)
        if self.fok:
            self.fichier.write(txt)

    def close(self):
        '''Ferme le "vrai" fichier'''
        if self.DEBOG:
            sys.stderr.write("Fopen.close()\n")
        if self.fok:
            self.fichier.close()

    def read(self):
        '''Renvoi le contenu de la liste sous forme de chaine'''
        if 'r' in self.mode:
            if self.fok:
                return self.fichier.read()
            else:
                return ''
        else:
            chaine = ''
            for i in range(len(self.liste)):
                chaine = chaine + self.liste[i]
            return chaine
            # return unicode(chaine).encode('utf-8')

    def readlines(self):
        '''Renvoi la liste'''
        # Si le fichier a été ouvert en écriture seul, on renvoi le texte du fichier
        if 'r' in self.mode:
            if self.fok:
                return self.fichier.readlines()
            else:
                return ''
        else:  # Sinon on renvoi la liste
            return self.liste

    def fileno(self):
        '''Renvoi un numéro de fichier'''
        if self.fok:
            return self.fichier.fileno()
        else:
            # Les descripteurs de fichier no 0, 1 et 2 sont respectivement stdin, stdout et stderr.
            return 3


def test():
    # Créé une fausse sortie standard, si on donne un nom au premier argument,
    # les donnés seront également écrites dessus (en plus de la capture):
    sys.stdout = Fopen(None, 'w')
    sys.stdout.DEBOG = True  # Active le mode debogage.

    print('test1')
    print('test2')
    print('file no: ' + str(sys.stdout.fileno()))

    ch_std = str(sys.stdout.readlines())  # Récupère dans une chaine de char la sortie standard
    sys.stderr.write("Capture: " + ch_std + '\n')  # Et l'affiche sur la sortie d'erreur.

    sys.stdout.close()

if __name__ == '__main__':
    test()
