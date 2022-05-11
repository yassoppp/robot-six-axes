import sys

# import PyQt6 as PySide6
from PySide6.QtCore import \
    Property, QObject, Signal, QAbstractAnimation, QVariantAnimation, QTimer
from PySide6.QtGui import QGuiApplication, QMatrix4x4, QVector3D
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras

from controle_bras import AXES, RAPPORT_MOTEUR_1, pas_en_degrés

UNITÉ_X = QVector3D(1, 0, 0)
UNITÉ_Y = QVector3D(0, 1, 0)
UNITÉ_Z = QVector3D(0, 0, 1)


class ContrôleBras(QObject):
    def __init__(self, dimensions, angles, transformations):
        super().__init__()
        self.dimensions = dimensions
        self.transformations = transformations
        self.matrices = [QMatrix4x4() for _ in range(6)]
        self.angles = angles

    def get_angles(self):
        return self._angles

    def set_angles(self, angles_axes):
        self._angles = list(angles_axes)
        θ0, θ1, θ2, θ3, θ4, θ5 = self._angles
        Z0, L0, L1, L2, L3, L4, L5 = self.dimensions
        m0, m1, m2, m3, m4, m5 = self.matrices
        for m in self.matrices:
            m.setToIdentity()
            m.translate(Z0 * UNITÉ_Z)
            m.rotate(θ0, UNITÉ_Z)
        for m in self.matrices[1:]:
            m.translate(L0 * UNITÉ_X)
            m.rotate(θ1, UNITÉ_Y)
        for m in self.matrices[2:]:
            m.translate(L1 * UNITÉ_Z)
            m.rotate(θ2, UNITÉ_Y)
        for m in self.matrices[3:]:
            m.translate(L2 * UNITÉ_Z)
            m.rotate(θ3, UNITÉ_Z)
        for m in self.matrices[4:]:
            m.translate(L3 * UNITÉ_Z)
            m.rotate(θ4, UNITÉ_Y)
        for m in self.matrices[5:]:
            m.translate(L4 * UNITÉ_Z)
            m.rotate(θ5, UNITÉ_Z)
        for t, m in zip(self.transformations, self.matrices):
            t.setMatrix(m)

    angles_modifiés = Signal()
    angles = Property(list, get_angles, set_angles, notify=angles_modifiés)


class ContrôleCible(QObject):
    def __init__(self, coordonnées, transformation):
        super().__init__()
        self.transformation = transformation
        self.matrice = QMatrix4x4()
        self.coordonnées = coordonnées

    def get_coordonnées(self):
        return self._coordonnées

    def set_coordonnées(self, coordonnées):
        self._coordonnées = list(coordonnées)
        x, y, z, α, β, γ = self._coordonnées
        m = self.matrice
        m.setToIdentity()
        m.translate(QVector3D(x, y, z))
        m.rotate(α, UNITÉ_Z)
        m.rotate(β, UNITÉ_Y)
        m.rotate(γ, UNITÉ_Z)
        self.transformation.setMatrix(m)

    coordonnées_modifiées = Signal()
    coordonnées = Property(
        list, get_coordonnées, set_coordonnées, notify=coordonnées_modifiées)


class Vue3DBras(Qt3DExtras.Qt3DWindow):
    def __init__(self, dimensions, angles, coordonnées_cible, interface):
        super().__init__()

        self.camera().lens().setPerspectiveProjection(60, 4 / 3, 1e-4, 1e4)
        self.camera().setPosition(QVector3D(0, -600, 600))
        self.camera().setViewCenter(QVector3D(0, 0, 200))

        self.racine = Qt3DCore.QEntity()
        self.setRootEntity(self.racine)

        self.contrôle_caméra = Qt3DExtras.QOrbitCameraController(self.racine)
        self.contrôle_caméra.setLinearSpeed(400)
        self.contrôle_caméra.setLookSpeed(360)
        self.contrôle_caméra.setCamera(self.camera())

        self.matériau = Qt3DExtras.QPhongMaterial(self.racine)

        self.références = []
        self.transformations_bras = []

        def cylindre_vertical(rayon, longueur):
            entité = Qt3DCore.QEntity(self.racine)
            sous_entité = Qt3DCore.QEntity(entité)
            repère = Qt3DExtras.QSphereMesh()
            repère.setRadius(12)
            maillage = Qt3DExtras.QCylinderMesh()
            maillage.setRadius(rayon)
            maillage.setLength(longueur)
            transformation = Qt3DCore.QTransform()
            sous_transformation = Qt3DCore.QTransform()
            sous_transformation.setRotationX(90)
            sous_transformation.setTranslation(QVector3D(0, 0, longueur / 2))
            entité.addComponent(transformation)
            entité.addComponent(repère)
            entité.addComponent(self.matériau)
            sous_entité.addComponent(maillage)
            sous_entité.addComponent(sous_transformation)
            sous_entité.addComponent(self.matériau)
            self.références.extend(
                (entité, maillage, repère, sous_transformation))
            self.transformations_bras.append(transformation)

        Z0, L0, *longueurs_segments = dimensions
        cylindre_vertical(80, 15)
        for longueur in longueurs_segments:
            cylindre_vertical(10, longueur)
        entité_cible = Qt3DCore.QEntity(self.racine)
        sous_entité = Qt3DCore.QEntity(entité_cible)
        maillage_cible = Qt3DExtras.QCuboidMesh()
        maillage_cible.setXExtent(30)
        maillage_cible.setYExtent(30)
        maillage_cible.setZExtent(30)
        sous_transformation = Qt3DCore.QTransform()
        sous_entité.addComponent(maillage_cible)
        sous_entité.addComponent(sous_transformation)
        sous_entité.addComponent(self.matériau)
        self.transformation_cible = Qt3DCore.QTransform()
        entité_cible.addComponent(self.transformation_cible)
        self.références.extend(
            (entité_cible, sous_entité, maillage_cible, sous_transformation))
        self.contrôle_cible = \
            ContrôleCible(coordonnées_cible, self.transformation_cible)
        self.contrôle_bras = \
            ContrôleBras(dimensions, angles, self.transformations_bras)
        self.interface = interface
        self.animation_angles = AnimationAngles(
            self.contrôle_bras.angles, self.contrôle_bras.set_angles,
            self.interface)
        self.rappels_fin_animation = []
        self.animation_angles.finished.connect(self.fin_animation)

    def modifier_angles(self, nouveaux_angles):
        if self.interface.bras.commande.connectée:
            self.contrôle_bras.set_angles(nouveaux_angles)
        else:
            return self.animation_angles.animer(nouveaux_angles)

    def modifier_coordonnées_cible(self, nouvelles_coordonnées, durée=1):
        self.contrôle_cible.coordonnées = nouvelles_coordonnées

    def attendre_fin_animation(self, rappel):
        if self.animation_angles.state() == QAbstractAnimation.Stopped:
            rappel()
        else:
            self.rappels_fin_animation.append(rappel)

    def fin_animation(self):
        rappels = self.rappels_fin_animation
        self.rappels_fin_animation = []
        for f in rappels:
            f()


class AnimationAngles(QVariantAnimation):
    def __init__(self, départ, mise_à_jour_valeur, interface):
        super().__init__()
        self.mise_à_jour_valeur = mise_à_jour_valeur
        self.interface = interface
        self.setStartValue(départ)

    def vitesse(self, i):
        if i == 1:
            return self.interface.réglages_moteurs.vitesse[i].value() \
                / abs(RAPPORT_MOTEUR_1)
        return self.interface.réglages_moteurs.vitesse[i].value()

    def animer(self, arrivée):
        if self.state() == QAbstractAnimation.Running:
            self.stop()
        départ = self.currentValue()
        if départ is not None:
            self.setStartValue(départ)
        else:
            départ = self.startValue()
        durée_max = max(abs(a - d) / self.vitesse(i)
                        for i, (a, d) in enumerate(zip(départ, arrivée)))
        self.setDuration(durée_max * 1000)
        self.setEndValue(arrivée)
        self.start()

    def updateCurrentValue(self, valeur):
        self.mise_à_jour_valeur(valeur)

    def interpolated(self, début, fin, avancement):
        liste = []
        for i, (d, f) in enumerate(zip(début, fin)):
            déplacement = self.vitesse(i) * self.duration() / 1000 * avancement
            if f > d:
                liste.append(min(f, d + déplacement))
            else:
                liste.append(max(f, d - déplacement))
        return liste

if __name__ == "__main__":
    application = QGuiApplication(sys.argv)
    vue = Vue3DBras([66, 40, 165, 109.8, 55.3, 54.5, 50],
                    [45, 30, 30, 30, 30, 30])
    vue.show()
    sys.exit(application.exec_())
