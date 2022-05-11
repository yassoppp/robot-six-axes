from math import pi as π, sin, cos, atan2, acos, hypot


def solution_invalide(valeur, bornes):
    inf, sup = bornes
    return not (inf <= valeur <= sup)


def solution_double_invalide(valeur1, bornes1, valeur2, bornes2):
    (inf1, sup1), (inf2, sup2) = bornes1, bornes2
    return not (inf1 <= valeur1 <= sup1 and inf2 <= valeur2 <= sup2)


def complémentaire(angle):
    assert -π <= angle <= π
    if angle < 0:
        return angle + π
    else:
        return angle - π


def cinématique_inverse(dimensions, bornes, coordonnées):
    z0, l0, l1, l2, l3, l4, l5 = dimensions
    d0, d1, d2, d3 = l0, l1, l2 + l3, l4 + l5
    bornes_θ0, bornes_θ1, bornes_θ2 = bornes[:3]
    bornes_θ3, bornes_θ4, bornes_θ5 = bornes[3:]
    x, y, z, α, β, γ = coordonnées
    solutions = []
    if γ < bornes_θ5[0] or γ > bornes_θ5[1]:
        return [None] * 8
    sα, cα = sin(α), cos(α)
    sβ, cβ = sin(β), cos(β)
    sαsβ = sα * sβ
    cαsβ = cα * sβ
    η = atan2(-d3 * sαsβ + y, -d3 * cαsβ + x)
    solutions_θ0 = [η, complémentaire(η)]
    solutions_θ1θ2 = []
    for θ0 in solutions_θ0:
        if solution_invalide(θ0, bornes_θ0):
            solutions.extend([None] * 4)
            continue
        sθ0, cθ0 = sin(θ0), cos(θ0)
        d = hypot(d3 * cβ - z + z0, d0 * sθ0 + d3 * sαsβ - y,
                  d0 * cθ0 + d3 * cαsβ - x)
        θ = acos((-d3*cβ+z-z0)/d)
        if d >= d1 + d2 or d1 >= d + d2 or d2 >= d + d1:
            solutions.extend([None] * 4)
            continue
        φ1 = abs(acos((d**2 + d1**2 - d2**2) / (2 * d * d1)))
        φ2 = abs(acos((-d**2 + d1**2 + d2**2) / (2 * d1 * d2)))
        if θ0 == η and d0 < hypot(d3*sαsβ-y, d3*cαsβ-x):
            solutions_θ1θ2 = \
                [(θ - φ1, -complémentaire(φ2)), (θ + φ1, complémentaire(φ2))]
        else:
            solutions_θ1θ2 = \
                [(-θ + φ1, complémentaire(φ2)), (-θ - φ1, -complémentaire(φ2))]
        for θ1, θ2 in solutions_θ1θ2:
            if solution_double_invalide(θ1, bornes_θ1, θ2, bornes_θ2):
                solutions.extend([None] * 2)
                continue
            sθ1θ2, cθ1θ2 = sin(θ1 + θ2), cos(θ1 + θ2)
            ψ1 = atan2(sαsβ * cθ0 - cαsβ * sθ0,
                       sαsβ * sθ0 * cθ1θ2 + cαsβ * cθ0 * cθ1θ2 - cβ * sθ1θ2)
            ψ2 = acos(sαsβ * sθ0 * sθ1θ2 + cαsβ * cθ0 * sθ1θ2 + cβ * cθ1θ2)
            solutions_θ3θ4 = [(ψ1, ψ2), (complémentaire(ψ1), -ψ2)]
            for θ3, θ4 in solutions_θ3θ4:
                if solution_double_invalide(θ3, bornes_θ3, θ4, bornes_θ4):
                    solutions.append(None)
                    continue
                θ5 = γ
                solutions.append([θ0, θ1, θ2, θ3, θ4, θ5])
    return solutions
