from dynamixel import CommandeAX12, ErreurDynamixel
from calcul_cinematique_directe import cinématique_directe
from calcul_cinematique_inverse import cinématique_inverse

from math import pi as π

AXES = tuple(range(6))
MIN_AXES = -60, -25, -110, -150, -100, -150  # degrés
MAX_AXES = 60, 70, 110, 150, 100, 150  # degrés
# MIN_AXES = (-180,) * 6
# MAX_AXES = (+180,) * 6
COORDONNÉES_CIBLE = "x", "y", "z", "α", "β", "γ"
DIMENSIONS = 66, 40, 165, 109.8, 55.3, 54.5, 0  # millimètres
Z0, L0, L1, L2, L3, L4, L5 = DIMENSIONS


class ErreurCinématique(Exception):
    pass


RAPPORT_MOTEUR_1 = -25 / 12
DÉCALAGE_MOTEUR_1 = 35


def degrés_en_pas(d, axe):
    if axe == 1:
        return \
            int(RAPPORT_MOTEUR_1 * (d - DÉCALAGE_MOTEUR_1) / 300 * 1023 + 511)
    else:
        return int(d / 300 * 1023 + 511)


def pas_en_degrés(p, axe):
    if axe == 1:
        return (p - 511) / 1023 * 300 / RAPPORT_MOTEUR_1 + DÉCALAGE_MOTEUR_1
    return (p - 511) / 1023 * 300


def encadrer(inf, v, sup):
    return min(sup, max(inf, v))


def degrés_en_radians(d):
    return d * 2 * π / 360


def radians_en_degrés(r):
    return r * 360 / (2 * π)


class ContrôleBrasRobot:
    def __init__(self):
        self.commande = CommandeAX12()
        self.angles_axes = [0] * len(AXES)
        self.coordonnées_cible = [0] * len(COORDONNÉES_CIBLE)
        self.état = "Déconnecté."
        self.dimensions = DIMENSIONS
        self.min_axes = MIN_AXES
        self.max_axes = MAX_AXES
        self.bornes = tuple(zip(map(degrés_en_radians, self.min_axes),
                                map(degrés_en_radians, self.max_axes)))
        self.ordre = list(range(8))
        self.solutions_cinématique_inverse = [None] * 8

    def lire_position_bras(self):
        for i in AXES:
            moteur = self.commande[i]
            self.angles_axes[i] = pas_en_degrés(moteur.present_position, i)
        self.cinématique_directe()

    def connexion(self, interface):
        self.commande.connecter(interface)
        self.lire_position_bras()
        self.commande[AXES].torque_enable = 1
        self.commande[AXES].moving_speed = 64
        self.commande[AXES].punch = 20

    def déconnexion(self):
        if self.commande.connectée:
            self.commande[AXES].torque_enable = 0
            self.commande.déconnecter()

    def modifier_angles_axes(self, angles_modifiés):
        for i, θi in angles_modifiés:
            self.angles_axes[i] = θi
        self.cinématique_directe()

    def modifier_coordonnées_cible(self, coordonnées_modifiées):
        for i, c in coordonnées_modifiées:
            self.coordonnées_cible[i] = c
        self.cinématique_inverse()

    def cinématique_inverse(self):
        x, y, z, α, β, γ = self.coordonnées_cible
        α, β, γ = map(degrés_en_radians, (α, β, γ))
        solutions = cinématique_inverse(
            self.dimensions, self.bornes, (x, y, z, α, β, γ))
        for solution in solutions:
            if solution is not None:
                solution[:] = map(radians_en_degrés, solution)
                solution[:] = map(encadrer, MIN_AXES, solution, MAX_AXES)
        self.solutions_cinématique_inverse[:] = solutions
        if all(s is None for s in self.solutions_cinématique_inverse):
            message = "Aucune solution de cinématique inverse trouvée."
            raise ErreurCinématique(message)
        for i, s in enumerate(solutions):
            if s is not None:
                self.angles_axes[:] = \
                    self.solutions_cinématique_inverse[self.ordre[i]]
                break

    def cinématique_directe(self):
        angles = map(degrés_en_radians, self.angles_axes)
        x, y, z, α, β, γ = cinématique_directe(self.dimensions, angles)
        α, β, γ = map(radians_en_degrés, (α, β, γ))
        self.coordonnées_cible[:] = x, y, z, α, β, γ

    def activer_configuration(self):
        if self.commande.connectée:
            self.commande[AXES].goal_position = \
                map(degrés_en_pas, self.angles_axes, AXES)
