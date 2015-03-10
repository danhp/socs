# -*- coding: utf-8 -*-
"""
Created on Fri Jan  9 16:32:41 2015

@author: fmannan
"""
from __future__ import division
import numpy as np
from numpy import deg2rad, cos, sin, sqrt

def normalize(vec):
    vec = np.array(vec)
    n = np.linalg.norm(vec)
    if abs(n) > 1e-12:
        vec = vec / n
    return vec

def translate(translate_vec):
    T = np.eye(4);
    T[:3,3] = translate_vec
    return np.matrix(T)

def rotX(c, s):
    R = [[1, 0, 0, 0], 
         [0, c, -s, 0], 
         [0, s, c, 0],
         [0, 0, 0, 1]]
    return np.matrix(R)

def rotY(c, s):
    R = [[c, 0, s, 0], 
         [0, 1, 0, 0],
         [-s, 0, c,  0], 
         [0, 0, 0, 1] ]
    return np.matrix(R)

def rotZ(c, s):
    R = [[c, -s, 0, 0], 
         [s,  c, 0, 0], 
         [0, 0, 1, 0],
         [0, 0, 0, 1] ]
    return np.matrix(R)
    
def rotateX(angle_deg):
    theta = deg2rad(angle_deg)
    return rotX(cos(theta), sin(theta))

def rotateY(angle_deg):
    theta = deg2rad(angle_deg)
    return rotY(cos(theta), sin(theta))

def rotateZ(angle_deg):
    theta = deg2rad(angle_deg)
    return rotZ(cos(theta), sin(theta))
    
def rotate(angle_deg, axis):
    axis = normalize(axis)
    u = sqrt(axis[0]*axis[0] + axis[2]*axis[2])
    if (abs(u) < 1e-8): 
	return rotateY(np.sign(axis[1]) * angle_deg)
	
    cosphi = u
    sinphi = axis[1]
    costh = axis[2] / u
    sinth = axis[0] / u
    #for simplicity just multiply the matrices explicitly
    return rotY(costh, sinth) * rotX(cosphi, -sinphi) * rotateZ(angle_deg) * rotX(cosphi, sinphi) * rotY(costh, -sinth);
    
def lookAtMatrix(eye, center, up):
    pass
    
def perspectiveMatrix(fovy, aspect, zNear, zFar):
    f = 1.0/np.tan(np.deg2rad(fovy)/2)
    # perspective transformation matrix
    P = np.zeros((4, 4))
    P[0][0] = f/aspect
    P[1][1] = f
    P[2][2] = (zNear + zFar) / (zNear - zFar) #-1.0/zNear;
    P[2][3] = 2.0 * zNear * zFar / (zNear - zFar) #zNear / (zNear - zFar);
    P[3][2] = -1.0
    
    return np.matrix(P)

def frustumMatrix(left, right, bottom, top, near, far):
    pass

def orthoMatrix(left, right, bottom, top, near, far):
    pass

def ModelViewMatrix(self):
    pass

def ProjectionMatrix(self):
    return np.eye(4);
