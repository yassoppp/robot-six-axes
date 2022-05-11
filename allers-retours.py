#!/usr/bin/env python3
from dynamixel import CommandeAX12
import sys
import time

# exemple adapté de la documentation de Dynamixel
ID = 1
cible, cible_suivante = 0, 1023
if len(sys.argv) != 2:
    print("Utilisation : <programme> <interface> (Windows : COM1, "
          "macOS : /dev/tty.usbserial-*, Linux : /dev/ttyUSB0)")
interface = sys.argv[1]
with CommandeAX12(interface) as commande:
    moteur = commande[ID]
    moteur.torque_enable = 1
    while True:
        moteur.goal_position = cible
        cible, cible_suivante = cible_suivante, cible
        time.sleep(1)
    moteur.torque_enable = 0
