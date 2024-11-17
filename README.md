Ce projet a été réalisé pour la société technique Formule Polytechnique Montréal durant ma première année d’études. Initialement développé sur un GitLab privé, j’ai choisi de le sauvegarder sur mon GitHub personnel. À ce jour, le projet est inactif et n’a malheureusement pas été utilisé par la société.

Bien que je sois fier de ce travail, je reconnais que l’application n’atteint pas le niveau requis pour répondre aux besoins d’une organisation aussi complexe que Formule. Je tiens à exprimer ma gratitude envers Alexis Fadei, qui a joué un rôle clé dans la réalisation de ce projet, ainsi qu’à l’équipe informatique pour leur soutien et leur aide précieuse lors des moments difficiles.

Pour ce projet, j’ai utilisé Python avec la bibliothèque Kivy pour développer une application compatible Android et Windows. J’ai également intégré Google-Auth pour permettre la connexion via un compte Google et Gspread pour accéder aux informations du BOM (Bill of Materials) géré via Google Sheets par l’équipe.

# inventory-tracker
But du projet: Faire une application python qui permet de voir et modifier les valeurs dans le BOM du google sheets à travers l'utilisation de codes QR. De plus, intégrer un système d'impression de codes QR. 
Cette application utilise Kivy pour le front-end et gspread pour le back-end. On utilise aussi google-auth pour l'authentification.
# Librairies nécessaires 
Se retrouvent dans requirements.txt (certaines sont déjà installées avec python, tandis que d'autres sont nécessaires seulement pour certaines fonctionnalités, par exemple, l'impression de codes QR)

# Structure du projet
1. Android  
   a. main.py : fichier principal de l'application, contient le code pour l'interface graphique.  
   b. google_sheets.py : contient le code pour la connexion à google sheets et les fonctions pour lire et écrire dans le BOM.  
   c. history.txt: fichier qui permet de sauvegarder toutes les modifications faites dans le BOM à partir de l'application.  
   d. client_secret_dev.json: fichier qui contient les informations pour l'authentification à l'api de google sheets.  
   e. camerax_provide: "An Android camera provider for Camera4Kivy."  
#
2. Desktop  
   a. main.py : fichier principal de l'application, contient le code pour l'interface graphique.  
   b. google_sheets.py : contient le code pour la connexion à google sheets et les fonctions pour lire et écrire dans le BOM.  
   c. history.txt: fichier qui permet de sauvegarder toutes les modifications faites dans le BOM à partir de l'application.  
   d. client_secret_dev.json: fichier qui contient les informations pour l'authentification à l'api de google sheets.   
   e. client_key.json: fichier qui contient les informations pour l'authentification à un "service account". Ceci est utilisé pour chercher l'information lorsqu'on imprime les codes QR; on peut remplacer cette méthode en utlisant le google-auth, mais ceci riskerait de limit le api. Donc on essaie de minimiser l'utilisation de google-auth.  
   f. id.txt: fichier où l'utilisateur peut rentrer une liste de id (un par ligne) pour imprimer en bulk les codes QR.  
   g. qr_codes.py: contient le code pour générer les codes QR.  
   h. qr_printing.py: contient le code pour imprimer les codes QR.  
   i. qrs: dossier qui contient les codes QR générés.  
   (j.) credentials.storage: fichier qui contient les informations pour l'authentification à l'api de google sheets. Ceci est généré automatiquement lors de la première connexion à l'api. Si il est supprimé, l'application va demander de se reconnecter.
#
3. Building  
    a. buildozer.spec: fichier qui contient les informations pour compiler l'application pour android.  
    b. FSAE-Scanner.spec: fichier qui contient les informations pour compiler l'application pour desktop.  
#
4. Testing  
    a. Collection de fichiers pour tester les différentes fonctionnalités de l'application.
#
# notes
- Si vous voulez compilez pour IOS, vous devez utiliser un mac avec Xcode 13 ou plus installé. Pour le moment, ceci n'est pas une priorité, donc ceci sera une section à venir.
#
# Compiler le code pour android
1. Pour le moment, compiler l'application pour android est seulement disponible sur Linux. Si vous avez Windows (et vous ne voulez pas faire de machine virtuelle), continuer de suivre les instructions, si vous êtes déjà sur Linux (préférablement Ubuntu, sautez à l'étape 3.)
2. ATTENTION: Ceci prendra environ 2GB d'espace disque. Excécuter wsl --install dans powershell pour installer wsl. (https://learn.microsoft.com/en-us/windows/wsl/install)
3. Ouvrez une session Ubuntu et excécutez les commandes suivantes (https://buildozer.readthedocs.io/en/latest/installation.html):
   - sudo apt update
   - sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   - pip3 install --user --upgrade Cython==0.29.33 virtualenv
4. Installer le package buildozer:
   - pip3 install --user --upgrade buildozer
5. Copier le buildozer.spec file du dossier android_compile et le mettre dans le même dossier que le main file.
6. Ouvrez le projet avec le main file dans un terminal et excécutez:
   - buildozer -v android debug
7. Buildozer va compiler le code et créer un fichier .apk dans le dossier bin (Dépendament de la puissance de votre ordi, cela peut facilement prendre environ 1 heure. Par contre, les prochaines fois que vous le compilez, cela prendra beaucoup moins de temps, soit 2 min à 10min). Vous pouvez installer ce fichier sur un téléphone android pour tester l'application. Suivre les instructions sur le wiki pour testez l'application. (https://wiki.fsae.polymtl.ca/x/OgCBBw)
- NOTE: La version de KivyMD sur android est différente que celle sur Windows (kivymd==1.0.2), mais cela est déjà pris en compte dans le buildozer.spec file. C'est juste une particularité à noter.
#
# Compiler le code pour desktop
1. Ouvrez un terminal et excécutez les commandes suivantes:
   - pip install pyinstaller
2. Copier le FSAE-Scanner.spec file du le dossier desktop_compile et le mettre dans le même dossier que le main file.
3. Ouvrez le projet avec le main file dans un terminal et excécutez:
   - pyinstaller -m PyInstaller FSAE-Scanner.spec

