# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:56:57 2022

@author: sebmo
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d  # Fonction pour la 3D
import numpy as np
 

nbpt = 10 #nombre de points entre 0 et 2pi
dt = (np.pi*0.29/180)/2 #maximum d'erreur possible sur chaque theta (pas de 0,29°)
tmax = np.pi*300/180 #angle maximum

x = 0
y = 0
z = 0

dx = 0 #erreur sur x
dy = 0
dz = 0
dpos = 0 #erreur sur la position
Mdpos = 0 #maximum d'erreur sur la position

res_x  = [] #liste des x
res_y  = []
res_z = []
res_dpos = []

dxt0,dxt1,dxt2,dxt3,dxt4 = 0,0,0,0,0 #dx/dtheta_0, dx/theta_1, ...
dyt0,dyt1,dyt2,dyt3,dyt4 = 0,0,0,0,0

i0,i1,i2,i3,i4 = 0,0,0,0,0
t0,t1,t2,t3,t4 = 0,0,0,0,0


for i0 in range(nbpt):
    for i1 in range(nbpt):
        for i2 in range(nbpt):
            for i3 in range(nbpt):
                for i4 in range(nbpt): #on parcourt tous les angles sur tous les liaisons
                    
                    t0 = i0*(tmax/nbpt)
                    t1 = i1*(tmax/nbpt)
                    t2 = i2*(tmax/nbpt)
                    t3 = i3*(tmax/nbpt)
                    t4 = i4*(tmax/nbpt)
                    
                    x = -5.5*np.sin(t0)*np.sin(t3)*np.sin(t4) \
                        +(6.5+(5.5*np.sin(t4)*np.cos(t2)*np.cos(t3) \
                               +(11+5.5*np.cos(t4))*np.sin(t2))*np.cos(t1) \
                          +(16.5-5.5*np.sin(t2)*np.sin(t4)*np.cos(t3) \
                            +(11+5.5*np.cos(t4))*np.cos(t2))*np.sin(t1))*np.cos(t0)
                    
                    y = 5.5*np.sin(t3)*np.sin(t4)*np.cos(t0) \
                        +(6.5+(5.5*np.sin(t4)*np.cos(t2)*np.cos(t3) \
                               +(11+5.5*np.cos(t4))*np.sin(t2))*np.cos(t1) \
                          +(16.5-5.5*np.sin(t2)*np.sin(t4)*np.cos(t3) \
                            +(11+5.5*np.cos(t4))*np.cos(t2))*np.sin(t1))*np.sin(t0)
                            
                    z = 6.5 -(5.5*np.sin(t4)*np.cos(t2)*np.cos(t3) \
                           +(11+5.5*np.cos(t4))*np.sin(t2))*np.sin(t1) \
                      +(16.5-5.5*np.sin(t2)*np.sin(t4)*np.cos(t3) \
                        +(11+5.5*np.cos(t4))*np.cos(t2))*np.cos(t1)
                    
                    
                    dxt0 = -5.5*np.cos(t0)*np.sin(t3)*np.sin(t4) \
                        -(6.5+(5.5*np.sin(t4)*np.cos(t2)*np.cos(t3) \
                               +(11+5.5*np.cos(t4))*np.sin(t2))*np.cos(t1) \
                          +(16.5-5.5*np.sin(t2)*np.sin(t4)*np.cos(t3) \
                            +(11+5.5*np.cos(t4))*np.cos(t2))*np.sin(t1))*np.sin(t0)

                    dxt1 = (-(5.5*np.sin(t4)*np.cos(t2)*np.cos(t3) \
                               +(11+5.5*np.cos(t4))*np.sin(t2))*np.sin(t1) \
                          +(16.5-5.5*np.sin(t2)*np.sin(t4)*np.cos(t3) \
                            +(11+5.5*np.cos(t4))*np.cos(t2))*np.cos(t1))*np.cos(t0)
                              
                    dxt2 = ((-5.5*np.sin(t4)*np.sin(t2)*np.cos(t3) \
                               +(11+5.5*np.cos(t4))*np.cos(t2))*np.cos(t1) \
                          +(-5.5*np.cos(t2)*np.sin(t4)*np.cos(t3) \
                            -(11+5.5*np.cos(t4))*np.sin(t2))*np.sin(t1))*np.cos(t0)

                    dxt3 = -5.5*np.sin(t0)*np.cos(t3)*np.sin(t4) \
                        +(-5.5*np.sin(t4)*np.cos(t2)*np.sin(t3)*np.cos(t1) \
                          +5.5*np.sin(t2)*np.sin(t4)*np.sin(t3)*np.sin(t1))*np.cos(t0)
                            
                    dxt4 = -5.5*np.sin(t0)*np.sin(t3)*np.cos(t4) \
                        +((5.5*np.cos(t4)*np.cos(t2)*np.cos(t3) \
                               -5.5*np.sin(t4)*np.sin(t2))*np.cos(t1) \
                          +(-5.5*np.sin(t2)*np.cos(t4)*np.cos(t3) \
                            -5.5*np.sin(t4)*np.cos(t2))*np.sin(t1))*np.cos(t0)
                    
                    dx = (0.5*dxt0 + dxt1 + dxt2 + dxt3 + dxt4) * dt
                    
                    
                    dyt0 = -5.5*np.sin(t3)*np.sin(t4)*np.sin(t0) \
                        +(6.5+(5.5*np.sin(t4)*np.cos(t2)*np.cos(t3) \
                               +(11+5.5*np.cos(t4))*np.sin(t2))*np.cos(t1) \
                          +(16.5-5.5*np.sin(t2)*np.sin(t4)*np.cos(t3) \
                            +(11+5.5*np.cos(t4))*np.cos(t2))*np.sin(t1))*np.cos(t0)

                    dyt1 = (-(5.5*np.sin(t4)*np.cos(t2)*np.cos(t3) \
                               +(11+5.5*np.cos(t4))*np.sin(t2))*np.sin(t1) \
                          +(16.5-5.5*np.sin(t2)*np.sin(t4)*np.cos(t3) \
                            +(11+5.5*np.cos(t4))*np.cos(t2))*np.cos(t1))*np.sin(t0)
                              
                    dyt2 = ((-5.5*np.sin(t4)*np.sin(t2)*np.cos(t3) \
                               +(11+5.5*np.cos(t4))*np.cos(t2))*np.cos(t1) \
                          +(-5.5*np.cos(t2)*np.sin(t4)*np.cos(t3) \
                            -(11+5.5*np.cos(t4))*np.sin(t2))*np.sin(t1))*np.sin(t0)

                    dyt3 = 5.5*np.cos(t3)*np.sin(t4)*np.cos(t0) \
                        +(-5.5*np.sin(t4)*np.cos(t2)*np.sin(t3)*np.cos(t1) \
                          +5.5*np.sin(t2)*np.sin(t4)*np.sin(t3)*np.sin(t1))*np.sin(t0)
                            
                    dyt4 = 5.5*np.sin(t3)*np.cos(t4)*np.cos(t0) \
                        +((5.5*np.cos(t4)*np.cos(t2)*np.cos(t3) \
                               -5.5*np.sin(t4)*np.sin(t2))*np.cos(t1) \
                          +(-5.5*np.sin(t2)*np.cos(t4)*np.cos(t3) \
                            -5.5*np.sin(t4)*np.cos(t2))*np.sin(t1))*np.sin(t0)
                    
                    dy = (0.5*dyt0 + dyt1 + dyt2 + dyt3 + dyt4) * dt
                    
                    
                    dzt0 = 0

                    dzt1 = -(5.5*np.sin(t4)*np.cos(t2)*np.cos(t3) \
                           +(11+5.5*np.cos(t4))*np.sin(t2))*np.cos(t1) \
                      -(16.5-5.5*np.sin(t2)*np.sin(t4)*np.cos(t3) \
                        +(11+5.5*np.cos(t4))*np.cos(t2))*np.sin(t1)
                              
                    dzt2 = -(-5.5*np.sin(t4)*np.sin(t2)*np.cos(t3) \
                           +(11+5.5*np.cos(t4))*np.cos(t2))*np.sin(t1) \
                      +(-5.5*np.cos(t2)*np.sin(t4)*np.cos(t3) \
                        -(11+5.5*np.cos(t4))*np.sin(t2))*np.cos(t1)

                    dzt3 = 5.5*np.sin(t4)*np.cos(t2)*np.sin(t3)*np.sin(t1) \
                      +5.5*np.sin(t2)*np.sin(t4)*np.sin(t3)*np.cos(t1)
                            
                    dzt4 = -(5.5*np.cos(t4)*np.cos(t2)*np.cos(t3) \
                           -5.5*np.sin(t4)*np.sin(t2))*np.sin(t1) \
                      +(-5.5*np.sin(t2)*np.cos(t4)*np.cos(t3) \
                        +-5.5*np.sin(t4)*np.cos(t2))*np.cos(t1)
                    
                    dz = (0.5*dzt0 + dzt1 + dzt2 + dzt3 + dzt4) * dt
                    
                    
                    dpos = np.sqrt(dx**2 + dy**2 + dz**2)
                    
                    if dpos > Mdpos: #recherche du maximum d'erreur possible sur la position
                        
                        Mdpos = dpos
                    
                    
                    res_x.append(x)
                    res_y.append(y)
                    res_z.append(z)
                    res_dpos.append(dpos)


print("Erreur maximale sur la position:",Mdpos,"cm")


# Tracé du résultat en 3D
fig = plt.figure()
ax = fig.gca(projection='3d')  # Affichage en 3D
ax.scatter(res_x, res_y, res_dpos, label='Courbe', marker='d')  # Tracé des points 3D
plt.title("Points 3D")
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.tight_layout()
plt.show()


