#!/usr/bin/env python

from dynamixel_sdk import \
    PortHandler, PacketHandler, GroupSyncWrite, \
    DXL_LOWORD, DXL_HIWORD, DXL_LOBYTE, DXL_HIBYTE, COMM_SUCCESS
from serial.serialutil import SerialException


def similitude(a, b, t, α, β, τ):
    def f(x):
        return τ((x - a) * (β - α) / (b - a) + α)

    def g(y):
        return t((y - α) * (b - a) / (β - α) + a)

    return f, g


conversions_angle = similitude(0, 1023, int, -300, 300, float)
conversions_vitesse_angulaire = \
    similitude(0, 1023, int, 0, 360 * 114 / 60, float)
conversions_pourcentage = similitude(0, 1023, int, 0, 100, float)


class Intervalle:
    def __init__(self, minimum, maximum):
        assert minimum <= maximum
        self.minimum = minimum
        self.maximum = maximum

    def __contains__(self, valeur):
        return self.minimum <= valeur <= self.maximum


class LectureSeule:
    def __init__(self, adresse, taille):
        self.adresse = adresse
        self.taille = taille

    def __get__(self, instance, owner=None):
        # pas de lecture groupée synchrone dans le protocole 1,
        # mais cela pourrait être simulé
        assert instance.nb_moteurs == 1
        commande, id_moteur = instance.commande, instance.id_moteurs
        adresse, taille = self.adresse, self.taille
        return commande.accès_mémoire(id_moteur, adresse, taille)

    def __set__(self, instance, value):
        raise AttributeError(
            "Impossible de modifier une variable en lecture seule")


class LectureÉcriture(LectureSeule):
    def __init__(self, adresse, taille, domaine=None):
        self.adresse = adresse
        self.taille = taille
        if domaine is None:
            domaine = range(0, 2 ** (taille * 8))
        self.domaine = domaine

    def __set__(self, instance, value):
        if instance.nb_moteurs == 1:
            return instance.commande.accès_mémoire(
                instance.id_moteurs, self.adresse, self.taille, value)
        else:
            try:
                iter(value)
                value = tuple(value)
                if any(v not in self.domaine for v in value):
                    return
            except TypeError:
                if value not in self.domaine:
                    return
                value = (value,) * instance.nb_moteurs
            return instance.commande.écriture_synchrone(
                instance.id_moteurs, self.adresse, self.taille, value)


class ConversionLecture:
    def __init__(self, propriété, conversion):
        self.propriété = propriété
        self.conversion_lecture = conversion

    def __get__(self, instance, owner=None):
        return self.conversion_lecture(self.propriété.__get__(instance, owner))


class ConversionLectureÉcriture(ConversionLecture):
    def __init__(self, propriété, conversion_lecture, conversion_écriture):
        super().__init__(propriété, conversion_lecture)
        self.conversion_écriture = conversion_écriture

    def __set__(self, instance, value):
        try:
            iter(value)
            value = map(self.conversion_écriture, value)
        except TypeError:
            value = self.conversion_écriture(value)
        self.propriété.__set__(instance, value)


class ErreurDynamixel(Exception):
    pass


class CommandeAX12:
    def __init__(self, interface=None):
        self.port_handler = PortHandler(interface)
        self.packet_handler = PacketHandler(1.0)

    @property
    def connectée(self):
        return self.port_handler.is_open

    @property
    def interface(self):
        return self.port_handler.getPortName()

    def déconnecter(self):
        if self.connectée:
            self.port_handler.closePort()

    def connecter(self, interface):
        if self.connectée:
            self.déconnecter()
        self.port_handler.setPortName(interface)
        try:
            port_ouvert = self.port_handler.openPort()
        except SerialException:
            message = f"Impossible d’ouvrir le périphérique {self.interface}"
            raise ErreurDynamixel(message)
        if not port_ouvert:
            message = f"Impossible d’ouvrir le périphérique {self.interface}"
            raise ErreurDynamixel(message)
        if not self.port_handler.setBaudRate(10**6):
            message = "Impossible de configurer le débit de symboles à 1 MHz"
            raise ErreurDynamixel(message)

    def __enter__(self):
        self.connecter(self.interface)
        return self

    def __exit__(self, type_ex, val_ex, trace_ex):
        self.déconnecter()

    def __getitem__(self, id_moteurs):
        return MoteursAX12(self, id_moteurs)

    def lire(self, id_moteur, adresse, taille):
        fonctions = {
            1: self.packet_handler.read1ByteTxRx,
            2: self.packet_handler.read2ByteTxRx,
            4: self.packet_handler.read4ByteTxRx
        }
        return fonctions[taille](self.port_handler, id_moteur, adresse)

    def écrire(self, id_moteur, adresse, taille, nouvelle_valeur):
        fonctions = {
            1: self.packet_handler.write1ByteTxRx,
            2: self.packet_handler.write2ByteTxRx,
            4: self.packet_handler.write4ByteTxRx
        }
        return fonctions[taille](
            self.port_handler, id_moteur, adresse, nouvelle_valeur)

    def accès_mémoire(self, id_moteur, adresse, taille, nouvelle_valeur=None):
        if not self.connectée:
            raise ErreurDynamixel("Bras non connecté")
        if nouvelle_valeur is None:
            valeur_lue, résultat, erreur = \
                self.lire(id_moteur, adresse, taille)
        else:
            résultat, erreur = \
                self.écrire(id_moteur, adresse, taille, nouvelle_valeur)
        if résultat != COMM_SUCCESS:
            message = self.packet_handler.getTxRxResult(résultat)
            raise ErreurDynamixel(f"Échec de communication : {message}")
        elif erreur != 0:
            message = self.packet_handler.getRxPacketError(erreur)
            raise ErreurDynamixel(f"Erreur : {message}")
        if nouvelle_valeur is None:
            return valeur_lue

    def écriture_synchrone(
            self, id_moteurs, adresse, taille, nouvelles_valeurs):
        if not self.connectée:
            raise ErreurDynamixel("Bras non connecté")
        gsw = GroupSyncWrite(
            self.port_handler, self.packet_handler, adresse, taille)
        for i, v in zip(id_moteurs, nouvelles_valeurs):
            gsw.addParam(i, découper(taille, v))
        r = gsw.txPacket()


def découper(taille, valeur):
    assert taille in (1, 2, 4)
    if taille == 1:
        return (valeur,)
    elif taille == 2:
        return (DXL_LOBYTE(valeur), DXL_HIBYTE(valeur))
    elif taille == 4:
        lo_word = DXL_LOWORD(valeur)
        hi_word = DXL_HIWORD(valeur)
        return (DXL_LOBYTE(lo_word), DXL_HIBYTE(lo_word),
                DXL_LOBYTE(hi_word), DXL_HIBYTE(hi_word))


class MoteursAX12:
    def __init__(self, commande, id_moteurs):
        try:
            self.nb_moteurs = len(id_moteurs)
            assert self.nb_moteurs >= 2
        except TypeError:
            self.nb_moteurs = 1
        self.id_moteurs = id_moteurs
        self.commande = commande
    model_number = LectureSeule(0, 2)
    firmware_version = LectureSeule(2, 1)
    # attention, cela ne modifie pas self.id_moteurs
    id = LectureÉcriture(3, 1)
    baud_rate = LectureÉcriture(4, 1)
    return_delay_time = LectureÉcriture(5, 1)
    cw_angle_limit = LectureÉcriture(6, 2)
    ccw_angle_limit = LectureÉcriture(8, 2)
    temperature_limit = LectureÉcriture(11, 1)
    min_voltage_limit = LectureÉcriture(12, 1)
    max_voltage_limit = LectureÉcriture(13, 1)
    max_torque = LectureÉcriture(14, 2)
    status_return_level = LectureÉcriture(16, 1)
    alarm_led = LectureÉcriture(17, 1)
    shutdown = LectureÉcriture(18, 1)
    torque_enable = LectureÉcriture(24, 1)
    led = LectureÉcriture(25, 1)
    cw_compliance_margin = LectureÉcriture(26, 1)
    ccw_compliance_margin = LectureÉcriture(27, 1)
    cw_compliance_slope = LectureÉcriture(28, 1)
    ccw_compliance_slope = LectureÉcriture(29, 1)
    goal_position = LectureÉcriture(30, 2)
    moving_speed = LectureÉcriture(32, 2)
    torque_limit = LectureÉcriture(34, 2)
    present_position = LectureSeule(36, 2)
    present_speed = LectureSeule(38, 2)
    present_load = LectureSeule(40, 2),
    present_voltage = LectureSeule(42, 1)
    present_temperature = LectureSeule(43, 1)
    registered = LectureSeule(44, 1)
    moving = LectureSeule(46, 1)
    lock = LectureÉcriture(47, 1)
    punch = LectureÉcriture(48, 2)

    cw_compliance_margin_deg = \
        ConversionLectureÉcriture(cw_compliance_margin, *conversions_angle)
    ccw_compliance_margin_deg = \
        ConversionLectureÉcriture(ccw_compliance_margin, *conversions_angle)
    goal_position_deg = \
        ConversionLectureÉcriture(goal_position, *conversions_angle)
    moving_speed_dps = \
        ConversionLectureÉcriture(moving_speed, *conversions_vitesse_angulaire)
    torque_limit_pct = \
        ConversionLectureÉcriture(torque_limit, *conversions_pourcentage)
    present_position_deg = \
        ConversionLectureÉcriture(present_position, *conversions_angle)
    ...  # ajouter d’autres conversions au besoin
