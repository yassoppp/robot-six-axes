from dynamixel import CommandeAX12
import sys
import time

ID=3
interface = "COM5" # valable sous Linux, pour Windows : "COM1", pour macOS : chercher un chemin commençant par "/dev/tty.usbserial-"
commande = CommandeAX12(interface)
moteur = commande[ID]
commande.connecter(interface)
moteur.moving_speed=30
L=[0,100,200,300,400,500,600,800,900,0]
print('the moving speed',moteur.moving_speed)
for cible in L :
    moteur.torque_enable = 1
    moteur.goal_position = cible

    print(cible)
    time.sleep(1)
#    moteur.goal_position = 500
commande[ID].led = 1 # voir la documentation plus bas pour tous les champs disponibles
commande.déconnecter()
