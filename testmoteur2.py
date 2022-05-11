from dynamixel import CommandeAX12
import sys
import time

ID=1
interface = "COM5" # valable sous Linux, pour Windows : "COM1", pour macOS : chercher un chemin commençant par "/dev/tty.usbserial-"
commande = CommandeAX12(interface)
moteur = commande[ID]
commande.connecter(interface)
X=[0,100,200,300,400,500,600,700,800,900]
V=[0,30,30,40,50,120,60,50,40,30]
print('the moving speed',moteur.moving_speed)
for moteur.goal_position,moteur.moving_speed in zip(X,V) :
        time.sleep(0.51)
#    moteur.goal_position = 500
commande[ID].led = 1 # voir la documentation plus bas pour tous les champs disponibles
commande.déconnecter()
