turbine
=======

Turbine is a fork of the djl game manager. djl is open soure (GPL 3), written in Python 2.5, for GNU/Linux, inspired by Valve's Steam.

The plan is to upgrade the code to Python 2.7 or 3.4 and continue development.


More about DJL (from the old README file)
=========================================

It makes it possible to download, install (via a repository) and remove a reasonable number of games placed in a subdirectory in an absolutely invisible way (but without dealing with any dependencies).
It can also execute .desktop shortcuts located in another directory (this way, it's possible to launch games which were already installed).

Several games are available in the repository. Anyone can submit new games to developers via a web page (http://djl.jeuxlinux.fr/djl_addgame_en.php).
The list of games is regularly updated from the internet, so it's not static.

djl is able to download and extract/install tar, tar.gz (or tgz), tar.bz2, zip packages or even graphical installers like .packages or .run (Loki packages). But these are extracted only, the user doesn't 'see' the user interface: its goal is to make the setup happen under the hood, without any user action.

Games are then completely removable with a single click.

About games themselves, each one comes with its description (which is mostly ingloriously stolen from jeuxlinux.fr), an icon, an image and some additional information in order to help you choose which to install.

Once they are installed, they can be launched from main window, which not only contains games that are installed from the repository, but also shortcuts as .desktop files.

It is possible to create shortcuts from a menu in the main window; they will be placed directly in the correct automatically then displayed in djl. 
