# -*- coding: utf-8 -*-

"""
gaedu is a google app engine daemon launcher on ubuntu so how to create a daemon?
I'll explain in french, :-)

NB: un demon est un service qui s'exécute au démarage de la machine

→ créer demon.py dans lequel vous écrirez le script que vous voulez exécuter

→ créer le fichier demon en modifiant le fichier /etc/init.d/skeleton
    NAME est le nom du fichier script ici demon.py
    DAEMON /chemin/vers/fichier/$NAME
    DAEMON_ARGS="/etc/init.d/demon start"

→ déplacer le fichier demon en tapant sudo cp /chemin/fichier/demon /etc/init.d/.

→ configurer les droits d'exécution de chaque fichier
    sudo chmod 755 /etc/init.d/demon
    sudo chmod 755 /path/to/demon.py
    
→ tester en tapant
    sudo /etc/init.d/demon start pour lancer le demon
    sudo /etc/init.d/demon stop pour arrêter le demon

→ configurer le lancement au démarage en tapant
    sudo update-rc.d demon defaults
    
→ pour supprimer le demon, 
    taper sudo update-rc.d -f gaedu remove
    puis effacer le demon en tapant sudo rm /etc/init.d/demon
"""
