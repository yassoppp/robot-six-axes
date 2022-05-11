from dynamixel import CommandeAX12
import sys
import time
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# ID=int(input("donner l ID dumoteur a manipuler"))
# ID=[2,3]
ID=3
def variationgauss(ID):
    print("ID dumoteur est ",ID)
    interface = "COM5" # valable sous Linux, pour Windows : "COM1", pour macOS : chercher un chemin commençant par "/dev/tty.usbserial-"
    commande = CommandeAX12(interface)
    moteur = commande[ID]
    commande.connecter(interface)

    domain=np.linspace(0,900,200)
    # print(domain.type)

    pdf_norm = norm.pdf(domain, loc=400, scale=200)*100000
    # print('the moving speed',moteur.moving_speed)
    moteur.moving_speed=300
    moteur.goal_position = 0

    time.sleep(3)
    for x,y in zip(domain,pdf_norm):


            moteur.goal_position=int(x)
            # moteur.goal_position=int(x),int(x)
            # print('la valeur de x est ',int(x))

            if(int(y)+10)<30 :
                moteur.moving_speed=30
            else :
                moteur.moving_speed=int(y)+10
            # moteur.moving_speed=int(y)+50,int(y)+50
            # print('la valeur de y est ',int(y)+10)
            # print(x)
            time.sleep(0.0002)
    # for x,y in zip(domain,pdf_norm) :
    #         moteur.goal_position=x
    #         moteur.moving_speed=y
    #         time.sleep(0.51)
    #    moteur.goal_position = 500
    commande[ID].led = 1 # voir la documentation plus bas pour tous les champs disponibles
    commande.déconnecter()

variationgauss(ID)
print('terminé')
# variationgauss(2)
# variationgauss(4)
