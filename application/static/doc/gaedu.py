#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess

# subprocess.call() prend en paramètre une liste d'arguments que je passe
# en ligne de commande. Il y'a pas d'espace donc chaque commande est un
# élément de ma liste de commandes!

liste_commande = ["/home/bapetel/google_appengine/dev_appserver.py", "--datastore_path=/home/bapetel/folder/nasserzone.datastore", "/home/bapetel/nasserzone"]
 
subprocess.call(liste_commande)
