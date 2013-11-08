-- 
-- Base de données: `djl`
-- 

-- --------------------------------------------------------

-- 
-- Structure de la table `desc_jeux`
-- 

DROP TABLE IF EXISTS `desc_jeux`;
CREATE TABLE IF NOT EXISTS `desc_jeux` (
  `id_desc_jeu` int(11) NOT NULL auto_increment,
  `id_jeu` int(3) NOT NULL,
  `id_lang` int(2) NOT NULL,
  `description` text collate utf8_unicode_ci NOT NULL,
  `url_site_local` varchar(256) collate utf8_unicode_ci NOT NULL,
  `url_info` varchar(256) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id_desc_jeu`),
  KEY `id_jeu` (`id_jeu`),
  KEY `id_lang` (`id_lang`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Table de description spécifique par langue' AUTO_INCREMENT=258 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `jeux`
-- 

DROP TABLE IF EXISTS `jeux`;
CREATE TABLE IF NOT EXISTS `jeux` (
  `id_jeu` int(3) NOT NULL auto_increment,
  `codename` varchar(64) collate utf8_unicode_ci NOT NULL,
  `name` varchar(64) collate utf8_unicode_ci NOT NULL,
  `version` varchar(64) collate utf8_unicode_ci NOT NULL,
  `revision` int(11) NOT NULL default '1',
  `url_site` varchar(256) collate utf8_unicode_ci NOT NULL,
  `url_dl` varchar(256) collate utf8_unicode_ci NOT NULL,
  `type_jeu` int(2) NOT NULL,
  `type_licence` int(2) NOT NULL,
  `taille` char(4) collate utf8_unicode_ci NOT NULL,
  `plateforme` int(2) NOT NULL,
  `valide` int(1) NOT NULL,
  `logo` varchar(256) collate utf8_unicode_ci NOT NULL,
  `screenshot` varchar(256) collate utf8_unicode_ci NOT NULL,
  `comd_jeu` varchar(64) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id_jeu`),
  KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Liste des jeux' AUTO_INCREMENT=135 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `jeux_annonyme`
-- 

DROP TABLE IF EXISTS `jeux_annonyme`;
CREATE TABLE IF NOT EXISTS `jeux_annonyme` (
  `id_jeu` int(3) NOT NULL auto_increment,
  `codename` varchar(64) collate utf8_unicode_ci NOT NULL,
  `name` varchar(64) collate utf8_unicode_ci NOT NULL,
  `version` varchar(64) collate utf8_unicode_ci NOT NULL,
  `revision` int(11) NOT NULL default '1',
  `url_site` varchar(256) collate utf8_unicode_ci NOT NULL,
  `url_dl` varchar(256) collate utf8_unicode_ci NOT NULL,
  `type_jeu` int(2) NOT NULL,
  `type_licence` int(2) NOT NULL,
  `taille` char(4) collate utf8_unicode_ci NOT NULL,
  `plateforme` int(2) NOT NULL,
  `valide` int(1) NOT NULL,
  `logo` varchar(256) collate utf8_unicode_ci NOT NULL,
  `screenshot` varchar(256) collate utf8_unicode_ci NOT NULL,
  `comd_jeu` varchar(64) collate utf8_unicode_ci NOT NULL,
  `pseudo` char(16) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id_jeu`),
  KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Liste des jeux' AUTO_INCREMENT=32 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `lang`
-- 

DROP TABLE IF EXISTS `lang`;
CREATE TABLE IF NOT EXISTS `lang` (
  `id_lang` int(2) NOT NULL auto_increment,
  `lang` char(2) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id_lang`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Table des langues' AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `logs`
-- 

DROP TABLE IF EXISTS `logs`;
CREATE TABLE IF NOT EXISTS `logs` (
  `id_logs` int(11) NOT NULL auto_increment,
  `utilisateurs` char(16) collate utf8_unicode_ci NOT NULL,
  `action` char(16) collate utf8_unicode_ci NOT NULL,
  `objet` int(11) NOT NULL,
  `date` timestamp NOT NULL default '0000-00-00 00:00:00',
  `ip` varchar(15) collate utf8_unicode_ci NOT NULL,
  `oldname` varchar(64) collate utf8_unicode_ci NOT NULL,
  KEY `id_logs` (`id_logs`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Table des logs' AUTO_INCREMENT=466 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `plateforme`
-- 

DROP TABLE IF EXISTS `plateforme`;
CREATE TABLE IF NOT EXISTS `plateforme` (
  `id_plat` int(2) NOT NULL auto_increment,
  `plateforme` char(8) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id_plat`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=3 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `traductions`
-- 

DROP TABLE IF EXISTS `traductions`;
CREATE TABLE IF NOT EXISTS `traductions` (
  `id_traduct` int(4) NOT NULL auto_increment,
  `type_traduct` varchar(16) collate utf8_unicode_ci NOT NULL,
  `traduction` varchar(256) collate utf8_unicode_ci NOT NULL,
  `lang` int(2) NOT NULL,
  `id_divers` int(3) NOT NULL,
  PRIMARY KEY  (`id_traduct`),
  KEY `type_traduct` (`type_traduct`),
  KEY `lang` (`lang`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Table des traductions' AUTO_INCREMENT=99 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `type_jeu`
-- 

DROP TABLE IF EXISTS `type_jeu`;
CREATE TABLE IF NOT EXISTS `type_jeu` (
  `id_type` int(3) NOT NULL auto_increment,
  `type` varchar(10) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id_type`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Table des types de jeux' AUTO_INCREMENT=16 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `type_licence`
-- 

DROP TABLE IF EXISTS `type_licence`;
CREATE TABLE IF NOT EXISTS `type_licence` (
  `id_licence` int(2) NOT NULL auto_increment,
  `licence` char(10) collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id_licence`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Table des licences' AUTO_INCREMENT=7 ;

-- --------------------------------------------------------

-- 
-- Structure de la table `utilisateurs`
-- 

DROP TABLE IF EXISTS `utilisateurs`;
CREATE TABLE IF NOT EXISTS `utilisateurs` (
  `id_utilisateur` int(3) NOT NULL auto_increment,
  `pseudo` char(16) collate utf8_unicode_ci NOT NULL,
  `password` varchar(32) collate utf8_unicode_ci NOT NULL,
  `lang` int(2) NOT NULL,
  `admin` int(1) NOT NULL,
  PRIMARY KEY  (`id_utilisateur`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Table des utilisateurs' AUTO_INCREMENT=22 ;
