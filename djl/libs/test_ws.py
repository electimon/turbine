#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SOAPpy
from os import system

class test_ws(object):
    def __init__(self):
        #system('clear')
        self.connection()

        #self.liste_id=self.creer_liste_id()
        #print self.liste_id
        
        
        #1= fr 2=ru 3=en 4=su 5=pt
        langue = 1 #Défini la langue à utiliser pour récupérer les informations du dépôt.

	id_ = self.recherche_jeu("Dwarf Fortress")
	self.detail_jeu(id_, langue)

        #self.affiche_langues()
        #self.detail_jeu(159, langue)
        #print '\n'
        #self.detail_jeu(116, langue) #Cet id n'existe pas
        #self.liste_jeux()
        #self.liste_images()
        #self.liste_genre(langue)
	
	#self.liste_license(langue)
        
	##Affiche la description rapide de tous les jeux du dépôt:
        #for i in range(len(self.clientSOAP.listeJeux()[0])):
            #self.detail_jeu(i+1)
            ##print '>>>', str(i+1)
	
	print("Fin")
    
    def liste_license(self, langue):
	'''Affiche la liste des licenses'''
	liste = self.clientSOAP.listeLicence(langue)
	for i in range(len(liste)):
	    print liste[i][0][0]['value'] + " - " + liste[i][0][1]['value']

    def recherche_jeu(self, nom):
	'''Recherche un jeu dans la base de donnée depuis son nom et retourne sont id'''
	#Parcours le dépôt:
	listejeux = self.clientSOAP.listeJeux()
	for i in range(len(listejeux[0])):
	    rn = listejeux[0][i]['value'][0][0]['value']
	    if (nom.lower() == rn.lower()):
		id_ = listejeux[0][i]['value'][0][6]['value']
		print("Trouvé: %s, no dans la liste: %i, id dans le dépôt: %s" % (nom, i, id_))
		return int(id_)

    def connection(self):
        '''création du client SOAP'''
	#self.clientSOAP = SOAPpy.SOAPProxy("http://djl.jeuxlinux.fr/webservice/djl.php")
	self.clientSOAP = SOAPpy.SOAPProxy("http://djl.jeuxlinux.fr/webservice/djl_dev_bdd_dev.php")
        #self.clientSOAP = SOAPpy.SOAPProxy("http://djl.jeuxlinux.fr/webservice/djl_dev.php")
        self.clientSOAP.config.dict_encoding = "utf8"
        self.clientSOAP.config.debug = 0
        self.clientSOAP.config.dumpSOAPIn = 0
        self.clientSOAP.config.dumpSOAPOut = 0 
        # exécution des fonctions distantes 

        print "Init du client terminé."
        
    def creer_liste_id(self):
	'''Créé la liste des ids de jeux'''
        print "On créé la liste des ids:"
        liste=[]
        listejeux = self.clientSOAP.listeJeux()
        for i in range(len(listejeux[0])):
            liste.append(listejeux[0][i]['value'][0][6]['value'])
        return liste

    def affiche_langues(self):
	'''Affiche toutes les langues du dépôt'''
        liste = self.clientSOAP.listeLang()
        print "Liste des langues:"
        for i in range(len(liste[0])):
            print liste[0][i]['value'][0][0]['value'], liste[0][i]['value'][0][1]['value']
            
    def detail_jeu(self, no=1, lang=0):
	'''Affiche le detail du jeu no avec en se basant sur la langue donnée'''
        #Demande les details d'un jeu en particulier, ici l'id no avec la langue 1
        detailjeux = self.clientSOAP.detailJeux(no,lang)	
        #print detailjeux
	
	try:
	    detail = detailjeux['item']
	except TypeError, x:
	    print("Erreur lors de la lecture de la fiche du jeu n° %i, il n'existe probablement pas." % (no))
	    return

	print("\nid du jeu: %s, langue: %s:" % (str(no), str(lang)))

        for i in range(len(detail)):
            print(str(i) + ': ' + detailjeux['item'][i]['key'] + ': ' + detailjeux['item'][i]['value'])
            
    def liste_jeux(self, parse=1):
	'''Affiche la liste complète des jeux avec quelques details'''
        listejeux = self.clientSOAP.listeJeux()

	print "Nombre de jeux dans la base :", str(len(listejeux))
	print "Liste des jeux :"
	for i in range(len(listejeux[0])):
	    #print listejeux[i][0][0]['value']  #Affiche que le nom
	    print "Nom:", listejeux[0][i]['value'][0][0]['value'], \
	    "Version:", listejeux[0][i]['value'][0][1]['value'], \
	    "\n", \
	    "Repertoire:", listejeux[0][i]['value'][0][2]['value'], \
	    "Icone:", listejeux[0][i]['value'][0][3]['value'], \
	    "Commande:", listejeux[0][i]['value'][0][4]['value'], \
	    "Genre:", listejeux[0][i]['value'][0][5]['value'], \
	    "Id:", listejeux[0][i]['value'][0][6]['value'], \
	    "Site:", listejeux[0][i]['value'][0][7]['value'], \
	    "\n", \
	    "Version dev:", listejeux[0][i]['value'][0][8]['value'], \
	    "Licence:", listejeux[0][i]['value'][0][9]['value']
	    print "Index boucle:", i
	    print '---'
            
    def liste_images(self):
	'''Affiche toutes les icones et images de djl'''
        liste = self.clientSOAP.listeImage()
        for i in range(len(liste[0])):
            type_= liste[0][i]['value'][0][0]['value']
            nom = liste[0][i]['value'][0][1]['value']
	    if int(type_) == 1:
		print "Icone:", nom
	    else:
		print "Image:", nom

    def liste_genre(self, no=1):
	'''Affiche la liste des genres de jeux:'''
        #1= fr 2=ru 3=en 4=su
        liste_type = self.clientSOAP.listeType(no)
        print "Liste des types de jeux :"
        for i in range (len(liste_type[0])):
            print liste_type[0][i]['value'][0][0]['value'], liste_type[0][i]['value'][0][1]['value']

if __name__ == '__main__':
    test_ws()