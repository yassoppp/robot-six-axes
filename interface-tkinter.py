#!/usr/bin/env python3

# Ce programme est conçu pour six Dynamixel AX-12A numérotés de 0 à 5 et
# configurés avec un débit symbols de 1 Mbauds

from dynamixel import CommandeAX12, ErreurDynamixel
import tkinter as tk

MIN = -150, -150, -90, -90, -90, -150
MAX = 150, 150, 90, 95, 95, 150
AXES = tuple(range(6))
CONNECTÉ, DÉCONNECTÉ = "État : connecté.", "État : déconnecté."

racine = tk.Tk()

périphérique = tk.StringVar()
périphérique.set("/dev/ttyUSB0")
état_connexion = tk.StringVar()
état_connexion.set(DÉCONNECTÉ)
angles = tuple(tk.DoubleVar() for _ in AXES)
commande = CommandeAX12()


def degrés_en_pas(d):
    return int(d / 300 * 1023 + 511)


def pas_en_degrés(p):
    return round((p - 511) / 1023 * 300, 1)


def gestion_erreurs_dynamixel(f):
    def avec_gestion_erreurs_dynamixel(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except ErreurDynamixel as e:
            état_connexion.set(f"{e}")
    return avec_gestion_erreurs_dynamixel


@gestion_erreurs_dynamixel
def connexion():
    commande.connecter(périphérique.get())
    état_connexion.set(CONNECTÉ)
    for i in AXES:
        angles[i].set(pas_en_degrés(commande[i].present_position))
    commande[AXES].torque_enable = 1


@gestion_erreurs_dynamixel
def déconnexion():
    if commande.connectée:
        commande[AXES].torque_enable = 0
        commande.arrêter()
        état_connexion.set(DÉCONNECTÉ)


def fermeture():
    déconnexion()
    racine.destroy()


racine.title("Commande bras robot à six axes")
racine.protocol("WM_DELETE_WINDOW", fermeture)
cadre = tk.Frame(racine)
cadre.pack()
ligne1 = tk.Frame(cadre)
ligne1.grid(row=0, column=0)
ligne2 = tk.Frame(cadre)
ligne2.grid(row=1, column=0)

tk.Label(ligne1, text="Périphérique").grid(row=0, column=0)
tk.Entry(ligne1, textvariable=périphérique).grid(row=0, column=1)
tk.Button(ligne2, text="Connexion", command=connexion).grid(row=0, column=0)
tk.Button(ligne2, text="Déconnexion", command=déconnexion) \
  .grid(row=0, column=1)
tk.Label(cadre, textvariable=état_connexion).grid(row=2, column=0)


def encadrer(inf, v, sup):
    return min(sup, max(inf, v))


@gestion_erreurs_dynamixel
def valider(*axes):
    nouveaux_angles = []
    for axe in axes:
        nouvel_angle = encadrer(MIN[axe], angles[axe].get(), MAX[axe])
        angles[axe].set(nouvel_angle)
        nouveaux_angles.append(nouvel_angle)
    if commande.connectée:
        if len(axes) == 1:
            commande[axes[0]].goal_position = degrés_en_pas(nouveaux_angles[0])
        else:
            commande[axes].goal_position = map(degrés_en_pas, nouveaux_angles)


def tout_valider():
    valider(*AXES)


def incrément(axe, delta):
    def action():
        angles[axe].set(angles[axe].get() + delta)
        valider(axe)
    return action


for axe in AXES:
    ligne = tk.Frame(cadre)
    ligne.grid(row=axe + 3, column=0)
    tk.Label(ligne, text=f"Angle {axe}").grid(row=0, column=0)
    tk.Entry(ligne, textvariable=angles[axe]).grid(row=0, column=1)
    tk.Button(ligne, text="−10", command=incrément(axe, -10)) \
      .grid(row=0, column=2)
    tk.Button(ligne, text="−1", command=incrément(axe, -1)) \
      .grid(row=0, column=3)
    tk.Button(ligne, text="+1", command=incrément(axe, +1)) \
      .grid(row=0, column=4)
    tk.Button(ligne, text="+10", command=incrément(axe, +10)) \
      .grid(row=0, column=5)

tk.Button(cadre, text="Valider", command=tout_valider) \
  .grid(row=len(AXES) + 3, column=0)
racine.mainloop()
