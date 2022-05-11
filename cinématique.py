#!/usr/bin/env python3
from sympy import \
    symbols, Matrix, pi as π, sin, cos, acos, atan2, Piecewise, And, Eq, \
    latex, pycode, cse

# Solutions analytiques pour la cinématique inverse d’un bras à six axes dont
# les trois derniers axes s’intersectent en un seul point. Cette condition
# permet d’imposer la position de ce point avec les trois premiers axes, puis
# d’utiliser les trois derniers axes pour imposer l’orientation.

# Initialement le bras est orienté verticalement et les axes de rotations sont
# parallèles soit à Oz, soit à Oy.

# Longueurs des différents segments du bras
l0, l1, l2, l3, l4, l5 = symbols("l_:6", positive=True)
# Distances entre les « coudes »
d0, d1, d2, d3 = symbols("d_:4", positive=True)

# Hauteur du plan horizontal contenant le deuxième axe de rotation
z0 = symbols("z_0", real=True)

# Position cible de l’extrémité du bras
x, y, z = symbols("x y z", real=True)
position_cible = Matrix((x, y, z))

# Orientation cible de l’extrémité du bras. À la position initiale, α est un
# angle autour de Oz, β autour de Oy et γ autour de Oz
α, β, γ = symbols("α β γ", real=True)
orientation_cible = Matrix((sin(β) * cos(α), sin(β) * sin(α), cos(β)))
# (orientation_cible est un vecteur unitaire)

# Angles des six axes du bras à partir de la base
θ0, θ1, θ2, θ3, θ4, θ5 = symbols("θ_:6", real=True)

# Variables intermédiaires
d, η, θ, φ1, φ2, ψ1, ψ2 = symbols("d η θ φ_1 φ_2 ψ_1 ψ_2")

# Ces deux dictionnaires permettent d’associer à un ou plusieurs symboles la ou
# les valeurs qu’ils peuvent prendre
notations = dict()
solutions = dict()

notations[d0] = l0
notations[d1] = l1
notations[d2] = l2 + l3
notations[d3] = l4 + l5

# L’intersection des trois derniers axes ne dépend que de la position et de
# l’orientation ciblées
intersection_derniers_axes = position_cible - d3 * orientation_cible
x_, y_, z_ = intersection_derniers_axes

# θ0
# Deux orientations possibles pour un même plan de positions accessibles
notations[η] = atan2(y_, x_)
solutions[θ0] = η, η + π

# θ1 et θ2
# Distance entre le deuxième axe et l’intersection des trois derniers axes
notations[d] = (intersection_derniers_axes
                - d0 * Matrix((cos(θ0), sin(θ0), 0))
                - Matrix((0, 0, z0))).norm()
notations[θ] = acos((z_ - z0) / d)
notations[φ1] = acos((d1 ** 2 + d ** 2 - d2 ** 2) / (2 * d1 * d))
notations[φ2] = acos((d1 ** 2 + d2 ** 2 - d ** 2) / (2 * d1 * d2))

# Configurations « coude haut » et « coude bas »
cas_un = (θ - φ1, π - φ2), (θ + φ1, φ2 - π)
cas_deux = (-θ + φ1, φ2 - π), (-θ - φ1, π - φ2)
condition = And(Eq(θ0, η), d0 < Matrix(intersection_derniers_axes[:2]).norm())
solutions[θ1, θ2] = Piecewise((cas_un, condition),
                              (cas_deux, True))


# θ3 et θ4
# Construction de matrices de rotation en trois dimensions
def matrice_rotation_y(θ):
    return Matrix(((cos(θ), 0, sin(θ)), (0, 1, 0), (-sin(θ), 0, cos(θ))))


def matrice_rotation_z(θ):
    return Matrix(((cos(θ), -sin(θ), 0), (sin(θ), cos(θ), 0), (0, 0, 1)))


# Calcul de coordonnées sphériques pour connaître θ3 et θ4
def longitude_colatitude_vecteur_unitaire(v):
    x, y, z = v
    return atan2(y, x), acos(z)


# Matrice de passage pour connaître l’orientation relative à l’intersection des
# trois derniers axes
R = matrice_rotation_y(-θ2 - θ1) * matrice_rotation_z(-θ0)
notations[ψ1], notations[ψ2] = \
    longitude_colatitude_vecteur_unitaire(R * orientation_cible)

# Deux orientations possibles sur une sphère si on ne restreint pas la
# colatitude à un demi-cercle
solutions[θ3, θ4] = (ψ1, ψ2), (ψ1 - π, -ψ2)

# θ5
solutions[θ5] = γ


# Cinématique directe
def rotation_z(θ):
    return lambda u: matrice_rotation_z(θ) * u


def rotation_y(θ):
    return lambda u: matrice_rotation_y(θ) * u


def translation(v):
    return lambda u: u + v


def translation_z(λ):
    return translation(Matrix((0, 0, λ)))


def translation_x(λ):
    return translation(Matrix((λ, 0, 0)))


def composition(*fonctions):
    def composée(u):
        v = u
        for f in fonctions:
            v = f(v)
        return v
    return composée


TR = [
    translation_z(z0),
    rotation_z(θ0),
    translation_x(l0),
    rotation_y(θ1),
    translation_z(l1),
    rotation_y(θ2),
    translation_z(l2 + l3),
    rotation_z(θ3),
    rotation_y(θ4),
    translation_z(l4 + l5),
    rotation_z(θ5)
]
R = [TR[1], TR[3], TR[5], *TR[7:9], TR[10]]
TR.reverse()
R.reverse()
TR = composition(*TR)
R = composition(*R)
position = TR(Matrix((0, 0, 0)))
orientation = R(Matrix((0, 0, 1)))
valeurs = dict()
valeurs[x], valeurs[y], valeurs[z] = position
valeurs[α], valeurs[β] = longitude_colatitude_vecteur_unitaire(orientation)
valeurs[γ] = θ5


# Formatage des formules
f = open("solutions.tex", "w")


def sortie(*s):
    print(*s, file=f)


def début_équation():
    sortie("\\[")


def fin_équation():
    sortie("\\]")


def égalité(sym, expr):
    sortie(latex(sym), "=", latex(expr))


def sortie1(sym, expr):
    début_équation()
    égalité(sym, expr)
    fin_équation()


def sortie2(sym, expr):
    expr1, expr2 = expr
    début_équation()
    égalité(sym, expr1)
    sortie("\\text{ ou }")
    égalité(sym, expr2)
    fin_équation()


def système(sym1, expr1, sym2, expr2):
    sortie("\\left\\{\\begin{array}{l}")
    égalité(sym1, expr1)
    sortie("\\\\")
    égalité(sym2, expr2)
    sortie("\\end{array}\\right.")


def sortie4_horizontale(sym1, sym2, expr):
    ((expr11, expr12), (expr21, expr22)) = expr
    début_équation()
    sortie("\\begin{array}{lcl}")
    système(sym1, expr11, sym2, expr12)
    sortie("&\\text{ou}&")
    système(sym1, expr21, sym2, expr22)
    sortie("\\end{array}")
    fin_équation()


def sortie4_verticale(sym1, sym2, expr):
    ((expr11, expr12), (expr21, expr22)) = expr
    début_équation()
    système(sym1, expr11, sym2, expr12)
    fin_équation()
    sortie("\\center{ou}")
    début_équation()
    système(sym1, expr21, sym2, expr22)
    fin_équation()


sortie("\\documentclass{article}[nopageno, 12pt, a4paper]")
sortie("\\usepackage[margin=1cm, landscape]{geometry}")
sortie("\\usepackage[french]{babel}")
sortie("\\usepackage{unicode-math}")
sortie("\\begin{document}")
sortie("\\center{\\bfseries\\large Cinématique inverse analytique}")

for sym, expr in notations.items():
    sortie1(sym, expr)

sortie2(θ0, solutions[θ0])
sortie1((θ1, θ2), solutions[θ1, θ2])
sortie4_horizontale(θ3, θ4, solutions[θ3, θ4])
sortie1(θ5, solutions[θ5])

sortie("\\center{\\bfseries\\large Cinématique directe}")
for sym, expr in valeurs.items():
    sortie1(sym, expr)

sortie("\\end{document}")


# Génération du code pour le calcul de la cinématique directe
def affectation(f, symbole, expression):
    f.write("    ")
    f.write(pycode(symbole))
    f.write(" = ")
    f.write(pycode(expression))
    f.write("\n")


with open("calcul_cinematique_directe.py", "w") as f:
    intermédiaires, finales = cse(valeurs.values(), optimizations="basic")
    f.write("# généré par cinématique.py\n")
    f.write("import math\n\n\n")
    f.write("def cinématique_directe(dimensions, angles):\n")
    affectation(f, (z0, l0, l1, l2, l3, l4, l5), "dimensions")
    affectation(f, (θ0, θ1, θ2, θ3, θ4, θ5), "angles")
    for sym, expr in intermédiaires:
        affectation(f, sym, expr)
    for sym, expr in zip(valeurs, finales):
        affectation(f, sym, expr)
    f.write("    return ")
    f.write(pycode((x, y, z, α, β, γ)))
    f.write("\n")
