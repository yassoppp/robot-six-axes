# généré par cinématique.py
import math


def cinématique_directe(dimensions, angles):
    (z_0, l_0, l_1, l_2, l_3, l_4, l_5) = dimensions
    (θ_0, θ_1, θ_2, θ_3, θ_4, θ_5) = angles
    x0 = l_4 + l_5
    x1 = math.sin(θ_0)
    x2 = math.sin(θ_4)
    x3 = x2*math.sin(θ_3)
    x4 = x1*x3
    x5 = math.cos(θ_0)
    x6 = math.cos(θ_1)
    x7 = math.cos(θ_2)
    x8 = x2*math.cos(θ_3)
    x9 = x7*x8
    x10 = math.sin(θ_2)
    x11 = math.cos(θ_4)
    x12 = l_2 + l_3 + x0*x11
    x13 = x0*x9 + x10*x12
    x14 = math.sin(θ_1)
    x15 = x10*x8
    x16 = l_1 - x0*x15 + x12*x7
    x17 = l_0 + x13*x6 + x14*x16
    x18 = x3*x5
    x19 = x10*x11 + x9
    x20 = -x11*x7 + x15
    x21 = -x14*x20 + x19*x6
    x = -x0*x4 + x17*x5
    y = x0*x18 + x1*x17
    z = -x13*x14 + x16*x6 + z_0
    α = math.atan2(x1*x21 + x18, x21*x5 - x4)
    β = math.acos(-x14*x19 - x20*x6)
    γ = θ_5
    return (x, y, z, α, β, γ)
