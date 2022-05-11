from dynamixel import CommandeAX12
import sys
import time
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

ID=3
interface = "COM5" # valable sous Linux, pour Windows : "COM1", pour macOS : chercher un chemin commençant par "/dev/tty.usbserial-"
commande = CommandeAX12(interface)
moteur = commande[ID]
commande.connecter(interface)
# X=[0,100,200,300,400,500,600,700,800,900]
#
# domain=np.linspace(0,900,50)
# print(domain.type)
domain = [i for i in range(0,800,25)]
v1=[i for i in range(0,200,12)]
v2=[i for i in range(200,0,-12)]
v=v1+v2
print('nombre de vitesses',len(v))
print('nombre de point',len(domain))
# assert(len(v)==len(domain)

# for j in v :
#     print(j)
pdf_norm = norm.pdf(domain, loc=400, scale=300)*20000
# print('the moving speed',moteur.moving_speed)
for x,y in zip(domain,v):
        moteur.goal_position=x
        moteur.moving_speed=y
        # print(x)
        time.sleep(0.1)
# for x,y in zip(domain,pdf_norm) :
#         moteur.goal_position=x
#         moteur.moving_speed=y
#         time.sleep(0.51)
#    moteur.goal_position = 500
commande[ID].led = 1 # voir la documentation plus bas pour tous les champs disponibles
commande.déconnecter()
