<?php

/******************************************************************************************
 djl (Dépot jeux Linux)
 Copyright (C) 2008 Le Floch ludovic - Lululaglue <lululaglue@jeuvinux.fr

 This file is part of djl (Dépot jeux Linux)

 [EN]
 djl is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 djl is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

 [FR]
 Ce programme est un logiciel libre: vous pouvez le redistribuer et/ou le modifier 
 selon les termes de la "GNU General Public License", tels que publiés par la 
 "Free Software Foundation"; soit la version 2 de cette licence ou (à votre choix) 
 toute version ultérieure. 

 Ce programme est distribué dans l'espoir qu'il sera utile,
 mais SANS AUCUNE GARANTIE, ni explicite ni implicite; sans même les garanties de
 commercialisation ou d'adaptation dans un but spécifique.
 Se référer à la "GNU General Public License" pour plus de détails. 

 Vous devriez avoir reçu une copie de la "GNU General Public License"
 en même temps que ce programme; sinon, consulter le site <http://www.gnu.org/licenses/>.
******************************************************************************************/

//--
$hote="localhost";
$user="djl_ws";
$password="xxxxxx";
$base="djl";
$url_ws="http://domain.tld/djl.php";
//--

mysql_pconnect($hote, $user, $password);
mysql_query("SET NAMES UTF8");
mysql_select_db($base) or die("Ouverture de la base impossible");

// Display list of games in database
// Affiche la liste des jeux présents dans la base.
function listeJeux()
{
        $requete = mysql_query("SELECT id_jeu,name,version,revision,codename,logo,comd_jeu,type_jeu,url_site,valide FROM jeux ORDER BY name");
        while($result=mysql_fetch_array($requete))
                {
                $i=$result[0];
                $listejeux[$i]['nom']=$result[1];
		$listejeux[$i]['version']=$result[2].'-r'.$result[3];
                $listejeux[$i]['codename']=$result[4];
                $listejeux[$i]['icone']=$result[5];
                $listejeux[$i]['commande']=$result[6];
                $listejeux[$i]['type']=$result[7];
                $listejeux[$i]['id_jeu']=$result[0];
		$listejeux[$i]['url_site']=$result[8];
		$listejeux[$i]['valide']=$result[9];
                }
        return $listejeux;
}

// Display list of games in database by type
// Affiche la liste des jeux présents dans la base pour un type donné.
function listeJeuxByType($type)
{
        $requete = mysql_query("SELECT id_jeu,name,version,revision,codename,logo,comd_jeu,type_jeu FROM jeux WHERE jeux.id_type = '$type' ORDER BY name");
        while($result=mysql_fetch_array($requete))
                {
                $i=$result[0];
                $listejeux[$i]['nom']=$result[1];
                $listejeux[$i]['version']=$result[2].'-r'.$result[3];
                $listejeux[$i]['codename']=$result[4];
                $listejeux[$i]['icone']=$result[5];
                $listejeux[$i]['commande']=$result[6];
                $listejeux[$i]['type']=$result[7];
                $listejeux[$i]['id_jeu']=$result[0];

                }
        return $listejeux;
}

// Display list of game's types in database
// Affiche la liste des types de jeux présent dans la base.
function listeType($id_langue)
{
	$listetype[0]['id_type']="0";
	$listetype[0]['type']="Tous";
        $requete = mysql_query("SELECT type_jeu.id_type, traductions.traduction FROM type_jeu, traductions WHERE traductions.id_divers = type_jeu.id_type AND traductions.type_traduct = 'type_jeu' AND traductions.lang = '$id_langue' ORDER BY type_jeu.id_type");
        while($result=mysql_fetch_array($requete))
        {
            $id_type = $result[0];
            $listetype[$id_type]['id_type']=$result[0];
            $listetype[$id_type]['type']=$result[1];
        }
        return $listetype;
}

// Display list of licenses
// Affiche la liste des différentes licences.
function listeLicence()
{
        $requete = mysql_query("SELECT id_licence, licence FROM type_licence ORDER BY id_licence");
	$listelicence[0]['id_licence']="0";
        $listelicence[0]['licence']="Toutes";
        while($result=mysql_fetch_array($requete))
        {
                $id_licence = $result[0];
                $listelicence[$id_licence]['id_licence']=$result[0];
                $listelicence[$id_licence]['licence']=$result[1];
        }
        return $listelicence;
}

// Display list of supported languages
// Affiche la liste des langues supportées.
function listeLang()
{
	$i="";
	$requete = mysql_query("SELECT id_lang, lang FROM lang ORDER BY id_lang");
	while($result=mysql_fetch_array($requete))
	{
		$i++;
		$listelang[$i]['id']=$result[0];
		$listelang[$i]['lang']=$result[1];
	}
        return $listelang;
}

// Return a list of images
// Renvoi la liste des images à télécharger
function listeImage()
{
    $i="0";
    $requete = mysql_query("SELECT logo FROM jeux");
    while($result=mysql_fetch_array($requete))
        {
                $i++;
                $listeimage[$i]['type']="1";
                $listeimage[$i]['name']=$result[0];
        }
    $requete = mysql_query("SELECT screenshot FROM jeux");
    while($result=mysql_fetch_array($requete))
        {
                $i++;
                $listeimage[$i]['type']="2";
                $listeimage[$i]['name']=$result[0];
        }
    return $listeimage;
}

// Return list of install directory
// Renvoi la liste des répertoires d'installation (plutot que de devoir aller les chercher dans les details
function liste_rep($nom_jeu)
{
    $requete = mysql_query("SELECT jeux.codename FROM jeux WHERE jeux.name = '$nom_jeu'");
    $repertoire=mysql_fetch_array($requete);
    return $repertoire;
}

// Display a detailed description of a game depending on the language
// Affiche le descriptif détaillé d'un jeu en fonction de la langue.
function detailJeux($id_jeu,$langue)
{
	$detailjeux="";
	$validjeux="";
	#$id_jeu++;
	$requete = mysql_query("SELECT jeux.version, jeux.url_site, jeux.url_dl, type_jeu.id_type, type_licence.licence, jeux.taille, jeux.plateforme, jeux.logo, jeux.screenshot, jeux.comd_jeu, jeux.codename, jeux.revision, jeux.valide FROM jeux, type_jeu, type_licence WHERE jeux.id_jeu ='$id_jeu' AND jeux.type_jeu = type_jeu.id_type AND jeux.type_licence = type_licence.id_licence LIMIT 1");
	while($result=mysql_fetch_array($requete))
        {
                $detailjeux['version']=$result[0].'-r'.$result['11'];
                $detailjeux['url']=$result[1];
                $detailjeux['url_dl']=$result[2];
                $detailjeux['type']=$result[3];
                $detailjeux['licence']=$result[4];
                $detailjeux['taille']=$result[5];
                $detailjeux['plateforme']=$result[6];
                $detailjeux['logo']=$result[7];
                $detailjeux['screenshot']=$result[8];
                $detailjeux['commande']=$result[9];
		$detailjeux['codename']=$result[10];
		$validjeux=$result[11];
        }
	if ($validjeux) {
		$requete2 = mysql_query("SELECT COUNT(id_jeu) FROM desc_jeux WHERE id_jeu ='$id_jeu' AND desc_jeux.id_lang = '$langue' LIMIT 1");
        	list($nb_desc) = mysql_fetch_row($requete2);
        	if ($nb_desc < "1") {
        	        $langue="3";
        	}
        	$requete = mysql_query("SELECT description, url_site_local, url_info FROM desc_jeux WHERE desc_jeux.id_jeu= '$id_jeu' AND id_lang='$langue' LIMIT 1");
        	while($result=mysql_fetch_array($requete))
        	{
		        $detailjeux['description']=$result[0];
        	        $detailjeux['url_site_local']=$result[1];
        	        $detailjeux['url_info']=$result[2];
		}
        	if (!$detailjeux['description']) {
			$detailjeux['description']="pas de description !";
	       	}
	}
        return $detailjeux;
}

function detailJeux2($id_jeu,$langue)
{
        $detailjeux="";
        $validjeux="";
        $id_jeu++;
        $requete = mysql_query("SELECT jeux.url_site, jeux.url_dl, jeux.taille, jeux.plateforme, jeux.screenshot, jeux.valide FROM jeux, type_jeu, type_licence WHERE jeux.id_jeu ='$id_jeu' AND jeux.type_jeu = type_jeu.id_type AND jeux.type_licence = type_licence.id_licence LIMIT 1");
        while($result=mysql_fetch_array($requete))
        {
                $detailjeux['url']=$result[0];
                $detailjeux['url_dl']=$result[1];
                $detailjeux['taille']=$result[2];
                $detailjeux['plateforme']=$result[3];
                $detailjeux['screenshot']=$result[4];
                $validjeux=$result[11];
        }
        if ($validjeux) {
                $requete2 = mysql_query("SELECT COUNT(id_jeu) FROM desc_jeux WHERE id_jeu ='$id_jeu' AND desc_jeux.id_lang = '$langue' LIMIT 1");
                list($nb_desc) = mysql_fetch_row($requete2);
                if ($nb_desc < "1") {
                        $langue="3";
                }
                $requete = mysql_query("SELECT description, url_site_local, url_info FROM desc_jeux WHERE desc_jeux.id_jeu= '$id_jeu'id_lang='$langue' LIMIT 1");
                while($result=mysql_fetch_array($requete))
                {
                        $detailjeux['description']=$result[1];
                        $detailjeux['url_site_local']=$result[2];
                        $detailjeux['url_info']=$result[3];
                }
                if (!$detailjeux['description']) {
                        $detailjeux['description']="pas de description !";
                }
        }
        return $detailjeux;
}

// Number of games
// Compte les jeux dans la base.
function nbJeux()
{
        $requete = mysql_query("SELECT COUNT(*) FROM jeux");
        list($nb_jeux) = mysql_fetch_row($requete);
        return $nb_jeux;
}

// Create server
// Création du serveur
$server = new SoapServer(null, array('uri'=>$url_ws, 'encoding'=>'UTF-8'));

$server->addFunction("listeJeux");
$server->addFunction("listeJeuxByType");
$server->addFunction("listeLang");
$server->addFunction("listeImage");
$server->addFunction("listeType");
$server->addFunction("listeLicence");
$server->addFunction("detailJeux");
$server->addFunction("detailJeux2");
$server->addFunction("nbJeux");
$server->addFunction("liste_rep");

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
	// launch service
	// On lance le service en attente des données du client
	$server -> handle();
} else {
	// else display list of methodes
	// sinon, on affiche une liste des méthodes que peut gérer ce serveur
	echo '<strong>This SOAP server can handle following functions : </strong>';    
	echo '<ul>';
	foreach($server -> getFunctions() as $func) {        
	        echo '<li>' , $func , '</li>';
	}
	echo '</ul>';
}
?>
