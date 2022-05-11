#!/usr/bin/env python3

import sys
import random

# import PyQt6 as PySide6
from PySide6.QtCore import \
    QSize, Qt, QTimer, QAbstractListModel, QItemSelectionModel
from PySide6.QtGui import QColor
from PySide6.QtWidgets import \
    QWidget, QApplication, QLabel, QGridLayout, QLineEdit, QHBoxLayout, \
    QVBoxLayout, QDoubleSpinBox, QGroupBox, QPushButton, QSlider, QCheckBox, \
    QComboBox, QSpinBox, QFileDialog, QListView, QAbstractItemView

from controle_bras import \
    ContrôleBrasRobot, AXES, COORDONNÉES_CIBLE, ErreurCinématique, \
    ErreurDynamixel

from bras_3d_qt import Vue3DBras

if sys.platform == "win32":
    NOM_INTERFACE_PAR_DÉFAUT = "COM1"
elif sys.platform == "darwin":
    NOM_INTERFACE_PAR_DÉFAUT = ""  # /dev/tty.usbserial-*
elif sys.platform == "linux":
    NOM_INTERFACE_PAR_DÉFAUT = "/dev/ttyUSB0"
else:
    NOM_INTERFACE_PAR_DÉFAUT = ""


class InterfaceQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bras = ContrôleBrasRobot()
        self.init_widgets()
        self.chronomètre_attente_arrêt = QTimer()
        self.chronomètre_attente_arrêt.timeout.connect(self.attente_arrêt)
        self.en_attente_arrêt = []

    def init_widgets(self):
        colonnes = QHBoxLayout(self)
        gauche = QVBoxLayout()
        droite = QVBoxLayout()
        colonnes.addLayout(gauche)
        colonnes.addLayout(droite)
        droite.addLayout(self.init_gestion_connexion())
        self.état = QLabel("Déconnecté")
        droite.addWidget(self.état)
        vérifier_état = QTimer()
        vérifier_état.timeout.connect(lambda: self.mettre_à_jour_état)
        vérifier_état.start(10_000)
        gauche.addLayout(self.init_formulaire())
        gauche.addWidget(self.init_validation())
        gauche.addLayout(self.init_positions_rapides())
        self.vue3d = Vue3DBras(self.bras.dimensions, self.bras.angles_axes,
                               self.bras.coordonnées_cible, self)
        widget3d = QWidget.createWindowContainer(self.vue3d)
        widget3d.setMinimumSize(QSize(360, 480))
        droite.addWidget(widget3d)
        self.liste_positions = ListePositions(self)
        gauche.addWidget(self.liste_positions)

    def mettre_à_jour_état(self):
        if self.bras.commande.connectée:
            self.état.setText("Connecté")
        else:
            self.état.setText("Déconnecté")

    def init_réglages_moteurs(self):
        self.réglages_moteurs = RéglagesMoteurs(self.bras.commande, self)
        try:
            self.réglages_moteurs.charger_sauvegarde("./réglages_moteurs.tsv")
        except FileNotFoundError:
            pass
        bouton_réglages_moteurs = QPushButton("Réglages moteurs")
        bouton_réglages_moteurs.clicked.connect(
            lambda: self.réglages_moteurs.show())
        return bouton_réglages_moteurs

    def gestion_erreurs_dynamixel(f):
        def avec_gestion_erreurs(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except ErreurDynamixel as e:
                self.état.setText(f"{e}")
        return avec_gestion_erreurs

    @gestion_erreurs_dynamixel
    def lire_position_bras(self):
        self.bras.lire_position_bras()
        self.mettre_à_jour_champs()

    @gestion_erreurs_dynamixel
    def connexion(self):
        self.bras.connexion(self.champ_interface.text())
        self.mettre_à_jour_état()
        self.mettre_à_jour_champs()
        self.réglages_moteurs.écrire()

    @gestion_erreurs_dynamixel
    def déconnexion(self):
        self.bras.déconnexion()
        self.mettre_à_jour_état()

    def closeEvent(self, e):
        self.déconnexion()

    def init_gestion_connexion(self):
        gestion_connexion = QHBoxLayout()
        étiquette = QLabel("Interface")
        champ = QLineEdit(NOM_INTERFACE_PAR_DÉFAUT)
        connexion = QPushButton("Connexion")
        déconnexion = QPushButton("Déconnexion")
        connexion.clicked.connect(self.connexion)
        déconnexion. clicked.connect(self.déconnexion)
        gestion_connexion.addWidget(étiquette)
        gestion_connexion.addWidget(champ)
        gestion_connexion.addWidget(connexion)
        gestion_connexion.addWidget(déconnexion)
        gestion_connexion.addWidget(self.init_réglages_moteurs())
        self.champ_interface = champ
        return gestion_connexion

    def init_formulaire(self):
        colonnes = QHBoxLayout()
        colonnes.addWidget(self.init_entrée_axes())
        colonnes.addWidget(self.init_entrée_cible())
        return colonnes

    def init_positions_rapides(self):
        ligne = QHBoxLayout()
        aléatoire = QPushButton("Aléatoire")
        aléatoire.clicked.connect(self.position_aléatoire)
        ligne.addWidget(aléatoire)
        vertical = QPushButton("Vertical")
        vertical.clicked.connect(self.position_verticale)
        ligne.addWidget(vertical)
        compact = QPushButton("Compact")
        compact.clicked.connect(self.position_compacte)
        ligne.addWidget(compact)
        actuel = QPushButton("Position actuelle")
        actuel.clicked.connect(self.lire_position_bras)
        ligne.addWidget(actuel)
        return ligne

    def position_aléatoire(self):
        self.modifier_angles(
            (i, random.uniform(self.bras.min_axes[i], self.bras.max_axes[i]))
            for i in AXES)

    def position_verticale(self):
        self.modifier_angles(((i, 0) for i in AXES))

    def position_compacte(self):
        min_axes = self.bras.min_axes
        self.modifier_angles(
            enumerate((0, min_axes[1], min_axes[2], 0, min_axes[4], 0)))

    def mettre_à_jour_champs(self):
        for i in AXES:
            champ = self.champs_axes[i]
            champ.valueChanged.disconnect(self._modifier_angle[i])
            champ.setValue(self.bras.angles_axes[i])
            champ.valueChanged.connect(self._modifier_angle[i])
        for i in range(len(COORDONNÉES_CIBLE)):
            champ = self.champs_cible[i]
            champ.valueChanged.disconnect(self._modifier_coordonnée[i])
            champ.setValue(self.bras.coordonnées_cible[i])
            champ.valueChanged.connect(self._modifier_coordonnée[i])

    def mettre_à_jour_vue_3d(self):
        self.vue3d.modifier_angles(self.bras.angles_axes)
        self.vue3d.modifier_coordonnées_cible(self.bras.coordonnées_cible)

    def modifier_angles(self, angles_modifiés):
        self.bras.modifier_angles_axes(angles_modifiés)
        self.état.setText("Cinématique directe.")
        self.mettre_à_jour_champs()
        self.mettre_à_jour_vue_3d()

    def modifier_coordonnées(self, coordonnées_modifiées):
        try:
            self.bras.modifier_coordonnées_cible(coordonnées_modifiées)
            self.état.setText("Cinématique inverse.")
            self.mettre_à_jour_champs()
            self.mettre_à_jour_vue_3d()
        except ErreurCinématique as e:
            self.état.setText(f"{e}")
        self.liste_solutions.nouvelles_solutions()

    def init_entrée_axes(self):
        entrée_axes = QGroupBox("Direct")
        formulaire_axes = QGridLayout(entrée_axes)
        entrée_axes.setLayout(formulaire_axes)
        self.champs_axes = []
        self._modifier_angle = []
        for i, minimum, maximum in \
                zip(AXES, self.bras.min_axes, self.bras.max_axes):
            champ = QDoubleSpinBox()
            champ.setMinimum(minimum)
            champ.setMaximum(maximum)
            self._modifier_angle.append(
                lambda θi, i=i: self.modifier_angles([(i, θi)]))
            champ.valueChanged.connect(self._modifier_angle[i])
            levier = Levier(self, champ, 1/2)
            formulaire_axes.addWidget(QLabel(f"Axe {i} (°)"), i, 0)
            formulaire_axes.addWidget(champ, i, 1)
            formulaire_axes.addWidget(levier, i, 2)
            self.champs_axes.append(champ)
        return entrée_axes

    def init_entrée_cible(self):
        entrée_cible = QGroupBox("Inverse")
        colonnes = QHBoxLayout(entrée_cible)
        formulaire_cible = QGridLayout()
        colonnes.addLayout(formulaire_cible)
        liste_solutions = ListeSolutions(self)
        liste_solutions.setMaximumWidth(32)
        colonnes.addWidget(liste_solutions)
        self.liste_solutions = liste_solutions
        self.champs_cible = []
        self._modifier_coordonnée = []
        for i, nom in enumerate(COORDONNÉES_CIBLE):
            champ = QDoubleSpinBox()
            champ.setMinimum(-999)
            champ.setMaximum(999)
            self._modifier_coordonnée.append(
                lambda c, i=i: self.modifier_coordonnées([(i, c)]))
            champ.valueChanged.connect(self._modifier_coordonnée[i])
            levier = Levier(self, champ, 1/2 if i >= 3 else 1)
            formulaire_cible.addWidget(
                QLabel(nom + (" (mm)" if i < 3 else " (°)")), i, 0)
            formulaire_cible.addWidget(champ, i, 1)
            formulaire_cible.addWidget(levier, i, 2)
            self.champs_cible.append(champ)
        return entrée_cible

    @gestion_erreurs_dynamixel
    def valider(self):
        self.bras.activer_configuration()
        self.mettre_à_jour_vue_3d()

    def init_validation(self):
        bouton = QPushButton("Valider")
        bouton.clicked.connect(self.valider)
        return bouton

    def attente_arrêt(self):
        if all(self.bras.commande[i].moving == 0 for i in AXES):
            self.chronomètre_attente_arrêt.stop()
            for f in self.en_attente_arrêt:
                f()
            self.en_attente_arrêt = []

    def attendre_arrêt(self, rappel):
        self.en_attente_arrêt.append(rappel)
        if not self.chronomètre_attente_arrêt.isActive():
            self.chronomètre_attente_arrêt.start(1000 / 60)


class Levier(QSlider):
    def __init__(self, interface, widget, facteur=1, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setMinimum(-100)
        self.setMaximum(100)
        self.widget = widget
        self.interface = interface
        self.facteur = facteur
        self.métronome = QTimer()
        self.métronome.timeout.connect(self.mettre_à_jour)
        self.métronome_validation = QTimer()
        self.métronome_validation.timeout.connect(self.interface.valider)
        self.sliderPressed.connect(self.activer)
        self.sliderReleased.connect(self.désactiver)

    def mettre_à_jour(self):
        v = self.widget.value()
        self.widget.setValue(v + self.facteur * self.value() / 25)

    def désactiver(self):
        self.métronome.stop()
        self.métronome_validation.stop()
        self.interface.valider()
        self.setValue(0)

    def activer(self):
        self.métronome.start(1000 / 60)
        self.métronome_validation.start(1000 / 60)


class RéglagesMoteurs(QWidget):
    def __init__(self, commande, parent=None):
        super().__init__(parent, Qt.Window)
        self.commande = commande
        lignes = QVBoxLayout(self)
        grille = QGridLayout()
        lignes.addLayout(grille)
        grille.addWidget(QLabel("Moteur"), 0, 0)
        grille.addWidget(QLabel("Activé"), 0, 1)
        grille.addWidget(QLabel("Limite couple (%)"), 0, 2)
        grille.addWidget(QLabel("« Punch »"), 0, 3)
        grille.addWidget(QLabel("Flexibilité"), 0, 4)
        grille.addWidget(QLabel("Vitesse (~°/s)"), 0, 5)
        grille.addWidget(QLabel("Précision (°)"), 0, 6)
        self.activé = []
        self.limite_couple = []
        self.punch = []
        self.pente_couple = []
        self.vitesse = []
        self.précision = []
        for i in AXES:
            grille.addWidget(QLabel(f"{i}"))
            activé = QCheckBox()
            activé.setChecked(True)
            limite_couple = QDoubleSpinBox()
            limite_couple.setMinimum(0)
            limite_couple.setMaximum(100)
            limite_couple.setValue(100)
            punch = QSpinBox()
            punch.setMinimum(20)
            punch.setMaximum(1023)
            punch.setValue(32)
            pente_couple = QComboBox()
            for v in 2, 4, 8, 16, 32, 64, 128:
                pente_couple.addItem(str(v), v)
            pente_couple.setCurrentText("32")
            vitesse = QDoubleSpinBox()
            vitesse.setMinimum(0)
            vitesse.setMaximum(360)
            vitesse.setValue(100)
            précision = QDoubleSpinBox()
            précision.setMinimum(0)
            précision.setMaximum(75)
            grille.addWidget(activé, i + 1, 1)
            grille.addWidget(limite_couple, i + 1, 2)
            grille.addWidget(punch, i + 1, 3)
            grille.addWidget(pente_couple, i + 1, 4)
            grille.addWidget(vitesse, i + 1, 5)
            grille.addWidget(précision, i + 1, 6)
            self.activé.append(activé)
            self.limite_couple.append(limite_couple)
            self.punch.append(punch)
            self.pente_couple.append(pente_couple)
            self.vitesse.append(vitesse)
            self.précision.append(précision)
        ligne = QHBoxLayout()
        lignes.addLayout(ligne)
        charger = QPushButton("Charger sauvegarde")
        charger.clicked.connect(self.charger_sauvegarde_interactif)
        ligne.addWidget(charger)
        enregistrer = QPushButton("Enregistrer sauvegarde")
        enregistrer.clicked.connect(self.enregistrer_sauvegarde_interactif)
        ligne.addWidget(enregistrer)
        actualiser = QPushButton("Actualiser")
        actualiser.clicked.connect(self.lire)
        ligne.addWidget(actualiser)
        valider = QPushButton("Valider")
        valider.clicked.connect(self.écrire)
        ligne.addWidget(valider)

    def lire(self):
        if self.commande.connectée:
            for i in AXES:
                moteur = self.commande[i]
                self.activé[i].setChecked(bool(moteur.torque_enable))
                self.limite_couple[i].setValue(moteur.torque_limit_pct)
                self.punch[i].setValue(moteur.punch)
                self.pente_couple[i].setCurrentText(
                    lecture_flexibilité(moteur.cw_compliance_slope))
                self.vitesse[i].setValue(moteur.moving_speed_dps)
                self.précision[i].setValue(moteur.cw_compliance_margin)

    def écrire(self):
        if self.commande.connectée:
            moteurs = self.commande[AXES]
            moteurs.torque_enable = \
                (int(self.activé[i].isChecked()) for i in AXES)
            moteurs.torque_limit_pct = \
                (self.limite_couple[i].value() for i in AXES)
            moteurs.punch = \
                (self.punch[i].value() for i in AXES)
            moteurs.cw_compliance_slope = \
                (self.pente_couple[i].currentData() for i in AXES)
            moteurs.ccw_compliance_slope = \
                (self.pente_couple[i].currentData() for i in AXES)
            moteurs.moving_speed_dps = \
                (self.vitesse[i].value() for i in AXES)
            moteurs.cw_compliance_margin_deg = \
                (self.précision[i].value() for i in AXES)
            moteurs.ccw_compliance_margin_deg = \
                (self.précision[i].value() for i in AXES)

    def charger_sauvegarde_interactif(self):
        chemin, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir sauvegarde", "réglages_moteurs.tsv", "")
        self.raise_()
        if chemin == "":
            return
        else:
            self.charger_sauvegarde(chemin)

    def charger_sauvegarde(self, chemin):
        with open(chemin, "r") as f:
            for i, ligne in enumerate(f):
                ligne = ligne.strip().split("\t")
                self.activé[i].setChecked(bool(int(ligne[0])))
                self.limite_couple[i].setValue(float(ligne[1]))
                self.punch[i].setValue(int(ligne[2]))
                self.pente_couple[i].setCurrentText(ligne[3])
                self.vitesse[i].setValue(float(ligne[4]))
                self.précision[i].setValue(float(ligne[5]))
            self.écrire()

    def enregistrer_sauvegarde_interactif(self):
        chemin, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer sauvegarde", "./réglages_moteurs.tsv", "")
        self.raise_()
        if chemin == "":
            return
        else:
            self.enregistrer_sauvegarde(chemin)

    def enregistrer_sauvegarde(self, chemin):
        with open(chemin, "w") as f:
            i = 0
            for i in AXES:
                f.write("\t".join(str(v) for v in
                                  (int(self.activé[i].isChecked()),
                                   self.limite_couple[i].value(),
                                   self.punch[i].value(),
                                   self.pente_couple[i].currentText(),
                                   self.vitesse[i].value(),
                                   self.précision[i].value())))
                f.write("\n")
                i += 1
            self.écrire()


def lecture_flexibilité(v):
    v = int(v)
    for i in range(2, 8):
        if 2 ** i > v:
            return str(2 ** (i - 1))
    return str(2 ** 7)


def déplacer_sous_liste(liste, src, dest, taille):
    if src == dest:
        return
    sous_liste = liste[src:src + taille]
    if src < dest:
        liste[src:dest - taille] = liste[src + taille:dest]
        liste[dest - taille:dest] = sous_liste
    else:
        liste[dest + taille:src + taille] = liste[dest:src]
        liste[dest:dest + taille] = sous_liste


GRIS = QColor("grey")


class ModèleListeSolutions(QAbstractListModel):
    def __init__(self, interface):
        super().__init__(interface)
        self.interface = interface

    @property
    def ordre(self):
        return self.interface.bras.ordre

    @property
    def solutions(self):
        return self.interface.bras.solutions_cinématique_inverse

    def __len__(self):
        return len(self.solutions)

    def rowCount(self, indice):
        return len(self)

    def data(self, indice, rôle):
        i = indice.row()
        if rôle == Qt.DisplayRole:
            return f"{self.ordre[i]:03b}"
        if rôle == Qt.ForegroundRole and self.solutions[self.ordre[i]] is None:
            return GRIS

    def moveRows(self, indice_src, début_src, nombre, indice_dest, début_dest):
        fin_src = début_src + nombre
        self.beginMoveRows(indice_src, début_src, fin_src - 1,
                           indice_dest, début_dest)
        déplacer_sous_liste(self.ordre, début_src, début_dest, nombre)
        self.endMoveRows()
        return True

    def supportedDropActions(self):
        return Qt.MoveAction

    def flags(self, indice):
        drapeaux = super().flags(indice)
        if indice.row() == -1:
            return Qt.ItemIsDropEnabled | drapeaux
        else:
            return Qt.ItemIsDragEnabled | drapeaux


class ListeSolutions(QListView):
    def __init__(self, interface, parent=None):
        super().__init__(parent)
        self.setModel(ModèleListeSolutions(interface))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.selectionModel().selectionChanged.connect(self.choix_solution)

    def nouvelles_solutions(self):
        modèle = self.model()
        for i, s in enumerate(modèle.solutions):
            if s is not None:
                self.selectionModel().select(
                    modèle.index(i), QItemSelectionModel.ClearAndSelect)
                break
        else:
            self.selectionModel().clearSelection()
        modèle.dataChanged.emit(
            modèle.index(0), modèle.index(len(modèle) - 1),
            [Qt.ForegroundRole])

    def choix_solution(self):
        sélection = self.selectedIndexes()
        if len(sélection) == 1:
            i = sélection[0].row()
            solution = self.model().solutions[i]
            if solution is not None:
                self.model().interface.modifier_angles(zip(AXES, solution))


class ModèleListePositions(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.noms = []
        self.positions = []

    def __len__(self):
        assert (longueur := len(self.noms)) == len(self.positions)
        return longueur

    def rowCount(self, indice):
        return len(self)

    def data(self, indice, rôle):
        if rôle in (Qt.DisplayRole, Qt.EditRole):
            return self.noms[indice.row()]

    def setData(self, indice, valeur, rôle):
        if rôle in (Qt.DisplayRole, Qt.EditRole):
            self.noms[indice.row()] = valeur
        self.dataChanged.emit(indice, indice, [rôle])

    def insertRows(self, début, nombre, indice):
        self.beginInsertRows(indice, début, début + nombre - 1)
        for i in range(nombre):
            position = début + i
            self.noms.insert(position, f"Nouvelle position {position}")
            self.positions.insert(position, [0] * 6)
        self.endInsertRows()
        return True

    def removeRows(self, début, nombre, indice):
        fin = début + nombre
        self.beginRemoveRows(indice, début, fin - 1)
        del self.noms[début:fin]
        del self.positions[début:fin]
        self.endRemoveRows()
        return True

    def moveRows(self, indice_src, début_src, nombre, indice_dest, début_dest):
        fin_src = début_src + nombre
        self.beginMoveRows(indice_src, début_src, fin_src - 1,
                           indice_dest, début_dest)
        déplacer_sous_liste(self.noms, début_src, début_dest, nombre)
        déplacer_sous_liste(self.positions, début_src, début_dest, nombre)
        self.endMoveRows()
        return True

    def supportedDropActions(self):
        return Qt.MoveAction

    def flags(self, indice):
        drapeaux = super().flags(indice)
        if indice.row() == -1:
            return Qt.ItemIsDropEnabled | drapeaux
        else:
            return Qt.ItemIsDragEnabled | Qt.ItemIsEditable | drapeaux


class ListePositions(QWidget):
    def __init__(self, interface):
        super().__init__(interface)
        self.interface = interface
        colonnes = QHBoxLayout(self)
        vue = QListView(self)
        vue.setSelectionMode(QAbstractItemView.ExtendedSelection)
        vue.setDragDropMode(QAbstractItemView.InternalMove)
        modèle = ModèleListePositions()
        vue.setModel(modèle)
        vue.selectionModel().selectionChanged.connect(
            self.afficher_la_position_sélectionnée)
        colonnes.addWidget(vue)
        droite = QVBoxLayout()
        colonnes.addLayout(droite)
        ajouter = QPushButton("Ajouter position actuelle")
        ajouter.clicked.connect(self.insérer_position)
        droite.addWidget(ajouter)
        retirer = QPushButton("Retirer position sélectionnée")
        retirer.clicked.connect(self.retirer_sélection)
        droite.addWidget(retirer)
        mettre_à_jour = QPushButton("Mettre à jour la position sélectionnée")
        mettre_à_jour.clicked.connect(
            self.mettre_à_jour_la_position_sélectionnée)
        droite.addWidget(mettre_à_jour)
        aller_à_position = QPushButton("Aller à la position sélectionnée")
        aller_à_position.clicked.connect(self.aller_à_la_position_sélectionnée)
        droite.addWidget(aller_à_position)
        lecture = QHBoxLayout()
        droite.addLayout(lecture)
        lire = QPushButton("Lire")
        lire.clicked.connect(self.démarrer_lecture)
        lecture.addWidget(lire)
        arrêter = QPushButton("Arrêter")
        arrêter.clicked.connect(self.arrêter_lecture)
        lecture.addWidget(arrêter)
        options_lecture = QHBoxLayout()
        droite.addLayout(options_lecture)
        options_lecture.addWidget(QLabel("En boucle"))
        en_boucle = QCheckBox()
        options_lecture.addWidget(en_boucle)
        options_lecture.addWidget(QLabel("Pauses (s)"))
        self.durée_pauses = QDoubleSpinBox()
        self.durée_pauses.setMinimum(0)
        self.durée_pauses.setValue(1)
        options_lecture.addWidget(self.durée_pauses)
        revenir_début = QPushButton("Revenir au début")
        revenir_début.clicked.connect(self.revenir_au_début)
        droite.addWidget(revenir_début)
        charger_enregistrer = QHBoxLayout()
        droite.addLayout(charger_enregistrer)
        charger = QPushButton("Charger")
        charger.clicked.connect(self.charger_sauvegarde)
        charger_enregistrer.addWidget(charger)
        enregistrer = QPushButton("Enregistrer")
        enregistrer.clicked.connect(self.enregistrer_sauvegarde)
        charger_enregistrer.addWidget(enregistrer)
        self.modèle = modèle
        self.vue = vue
        self.en_boucle = en_boucle
        self.lecture_après_pause = QTimer()
        self.lecture_après_pause.setSingleShot(True)
        self.lecture_après_pause.timeout.connect(self.lecture)

    def indice_sélection(self):
        sélection = self.vue.selectedIndexes()
        if len(sélection) != 0:
            return sélection[0].row()

    def insérer_position(self):
        i = self.indice_sélection()
        if i is None:
            i = len(self.modèle)
        else:
            i += 1
        self.modèle.insertRow(i)
        self.mettre_à_jour_la_position(i)

    def mettre_à_jour_la_position(self, i):
        self.modèle.positions[i][:] = self.interface.bras.angles_axes

    def mettre_à_jour_la_position_sélectionnée(self):
        i = self.indice_sélection()
        if i is not None:
            self.mettre_à_jour_la_position(i)

    def retirer_sélection(self):
        indices = [indice.row() for indice in self.vue.selectedIndexes()]
        indices.sort(reverse=True)
        for i in indices:
            self.modèle.removeRow(i)

    def afficher_la_position_sélectionnée(self):
        i = self.indice_sélection()
        if i is not None:
            angles = self.modèle.positions[i]
            self.interface.modifier_angles(zip(AXES, angles))

    def aller_à_la_position_sélectionnée(self, rappel=None):
        self.afficher_la_position_sélectionnée()
        self.interface.valider()
        if rappel is not None and self.interface.bras.commande.connectée:
            self.interface.attendre_arrêt(rappel)
        else:
            self.interface.vue3d.attendre_fin_animation(rappel)

    def démarrer_lecture(self):
        if len(self.modèle) == 0:
            return
        self.arrêter = False
        self.lecture()

    def lecture_différée(self):
        self.lecture_après_pause.start(self.durée_pauses.value() * 1000)

    def lecture(self):
        if self.arrêter:
            return
        i = self.indice_sélection()
        if i is not None and i + 1 >= len(self.modèle) \
           and not self.en_boucle.isChecked():
            return
        if i is None \
           or (i + 1 >= len(self.modèle) and self.en_boucle.isChecked()):
            self.revenir_au_début()
        else:
            self.sélectionner(i + 1)
        self.aller_à_la_position_sélectionnée(rappel=self.lecture_différée)

    def arrêter_lecture(self):
        self.arrêter = True

    def sélectionner(self, i):
        if len(self.modèle) > i:
            self.vue.selectionModel().select(
                self.modèle.index(i), QItemSelectionModel.ClearAndSelect)

    def revenir_au_début(self):
        self.sélectionner(0)

    def enregistrer_sauvegarde(self):
        chemin, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer liste de positions", "./liste_positions.tsv",
            "")
        if chemin != "":
            with open(chemin, "w") as f:
                for nom, position in \
                        zip(self.modèle.noms, self.modèle.positions):
                    f.write("\t".join((str(nom), *map(str, position))))
                    f.write("\n")

    def charger_sauvegarde(self):
        chemin, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir liste de positions", "liste_positions.tsv", "")
        if chemin != "":
            with open(chemin, "r") as f:
                for i, ligne in enumerate(f):
                    ligne = ligne.strip().split("\t")
                    self.modèle.noms.append(ligne[0])
                    self.modèle.positions.append(list(map(float, ligne[1:])))
        self.modèle.dataChanged.emit(
            self.modèle.index(0), self.modèle.index(len(self.modèle) - 1),
            [Qt.DisplayRole])


application = QApplication(sys.argv)
racine = InterfaceQt()
racine.show()
application.exec_()
