# Bras robot à six axes

## Prérequis : python 3, git, pilote USB2Dynamixel

### Windows
#### Python 3
Page lisant les installateurs pour Windows <https://www.python.org/downloads/windows/>.

#### Git
<https://git-scm.com/download/win>

### Pilote USB2Dynamixel
<https://www.ftdichip.com/Drivers/CDM/CDM21228_Setup.zip>

### macOS
#### Python 3
Page listant les installateurs pour macOS : <https://www.python.org/downloads/mac-osx/>.

#### Git
<https://git-scm.com/download/mac>

#### Pilote USB2Dynamixel
<https://www.ftdichip.com/Drivers/VCP/MacOSX/FTDIUSBSerialDriver_v2_2_18.dmg>

## Bibliothèque Python pour contrôler les Dynamixels
### Installation
```
git clone https://github.com/ROBOTIS-GIT/DynamixelSDK
pip install --user /DynamixelSDK/python
```

### Désinstallation
```
pip uninstall pyserial dynamixel_sdk
```

### Utilisation

Créer un objet `CommandeAX12`, et utiliser l’indexation pour obtenir une référence à un moteur dont les champs permettent de lire et écrire dans sa mémoire. Par exemple, pour allumer la DEL du moteur 1 :
```
interface = "/dev/ttyUSB0" # valable sous Linux, pour Windows : "COM1", pour macOS : chercher un chemin commençant par "/dev/tty.usbserial-"
commande = CommandeAX12(interface)
commande.démarrer()
commande[1].led = 1 # voir la documentation plus bas pour tous les champs disponibles
commande.arrêter()
```

Voir aussi le fichier `allers-retours.py` pour un autre exemple d’utilisation.

Il est également possible d’utiliser l’écriture groupée synchrone des Dynamixels AX12-A en utilisant plusieurs indices :
```
# écriture de la même valeur dans les trois moteurs
commande[1, 2, 3].torque_enable = 1

# écriture de valeurs différentes
commande[1, 2, 3].goal_position = 0, 511, 1023
```

## Interface Qt
Pour utiliser l’interface Qt il faut installer `pyside6` :
```
pip3 install --user pyside6
```

## Documentation Dynamixel
- [Moteur AX12](https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/) (il y a notamment une description des variables du moteur)
- [SDK](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/)
- [Protocole utilisé pour communiquer avec le moteur](https://emanual.robotis.com/docs/en/dxl/protocol1/)
- Pour tester les moteurs avec une interface graphique : [Dynamixel Wizard 2.0](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/) 

## Bibliographie
- Exemple de projet utilisant des Dynamixels : [Poppy](https://github.com/poppy-project)
