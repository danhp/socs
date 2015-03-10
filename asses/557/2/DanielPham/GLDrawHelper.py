# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 15:09:41 2015

@author: fmannan
"""
import sys
import numpy as np
try:
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print('ERROR: PyOpenGL not installed properly.')
  sys.exit()

g_pQuadric = None  
# ------------------    Methods for drawing parts of the scene
    
def setColor(color):
    glColor3f(color[0], color[1], color[2])
    
def drawTriangle(per_vertex_color = []):
    pvc_specified = np.array(per_vertex_color).shape == (3, 3)
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glBegin(GL_TRIANGLES)
    setColor(per_vertex_color[0]) if pvc_specified else []
    glVertex3f(-1, -1, 0.)
    setColor(per_vertex_color[1]) if pvc_specified else []
    glVertex3f(1., -1., 0.)
    setColor(per_vertex_color[2]) if pvc_specified else []
    glVertex3f(0, 1, 0.)
    glEnd()
    glPopAttrib()
    
def drawSquare(size = 1, per_vertex_color = []):
    pvc_specified = np.array(per_vertex_color).shape == (4, 3)
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glBegin(GL_QUADS)
    setColor(per_vertex_color[0]) if pvc_specified else []
    glVertex3f(-0.5*size, -0.5*size, 0.0)
    setColor(per_vertex_color[1]) if pvc_specified else []
    glVertex3f( 0.5*size, -0.5*size, 0.0)
    setColor(per_vertex_color[2]) if pvc_specified else []
    glVertex3f( 0.5*size, 0.5*size, 0.0)
    setColor(per_vertex_color[3]) if pvc_specified else []
    glVertex3f(-0.5*size, 0.5*size, 0.0)
    glEnd()
    glPopAttrib()

def drawCheckerBoard(scale = [1, 1], dim = [8, 8], check_colors = [[0, 0, 0], [1, 1, 1]]):
    assert(len(scale) == 2 and scale[0] > 0 and scale[1] > 0) # scale must be 2D
    assert(len(dim) == 2 and dim[0] >= 2 and dim[1] >= 2)
    assert(len(check_colors) is 2 and len(check_colors[0]) is 3 and len(check_colors[1]) is 3)
    
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glPushMatrix()
    glScalef(scale[0], scale[1], 1)
    glTranslate(-.5, -.5, 0)
    # draw a checkerboard assuming 1x1 scale
    DX = 1./dim[0]
    DY = 1./dim[1]
    for y in np.arange(dim[0]):
        for x in np.arange(dim[1]):
            setColor(check_colors[(x + y) & 1])
            glBegin(GL_QUADS)        # Draw A Quad
            glVertex2f(x * DX, y * DY)         # Top Left
            glVertex2f((x + 1) * DX, y * DX)    # Top Right
            glVertex2f((x + 1) * DX, (y + 1) * DY)    # Bottom Right
            glVertex2f(x * DX, (y + 1) * DY)    #  Bottom Left
            glEnd()

    glPopMatrix()
    glPopAttrib()

def draw3DCoordinateAxes():
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glBegin (GL_LINES)
    glColor4f(1.0,  0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(1.0, 0.0, 0.0)

    glColor4f(0.0,  1.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 1.0, 0.0)

    glColor4f(0.0,  0.0, 1.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 1.0)
    glEnd ()
    glPopAttrib()

def draw3DCoordinateAxesQuadrics(pQuadric = None):
    #print pQuadric
    if pQuadric is None:
        global g_pQuadric
        if g_pQuadric is None:
            g_pQuadric = gluNewQuadric()
        pQuadric = g_pQuadric
    glPushMatrix()
    glScalef(.5, .5, .5)
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glColor4f(0.8,  0.0, 0.0, 1.0)    
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    gluCylinder(pQuadric, .1, .1, .75, 32, 32)
    glTranslatef(0, 0, 0.75)
    gluCylinder(pQuadric, .2, 0, .5, 32, 32)
    glPopMatrix()

    glColor4f(0.0,  0.8, 0.0, 1.0)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(pQuadric, .1, .1, .75, 32, 32)
    glTranslatef(0, 0, 0.75)
    gluCylinder(pQuadric, .2, 0, .5, 32, 32)
    glPopMatrix()

    glColor4f(0.0,  0.0, .8, 1.0)
    glPushMatrix()
    gluCylinder(pQuadric, .1, .1, .75, 32, 32)
    glTranslatef(0, 0, 0.75)
    gluCylinder(pQuadric, .2, 0, .5, 32, 32)
    glPopMatrix()
    glPopAttrib()
    
    glPopMatrix()
    

def drawViewVolume(left, right, bottom, top, near, far):
    
    #  assumes camera is at origin
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glColor4f(1.0,  1.0, 1.0, 1.0)
    
    glBegin(GL_LINES)
    
    glVertex3d ( right, top, -near)
    glVertex3d ( left, top, -near)
    
    glVertex3d ( right, bottom, -near)
    glVertex3d ( left, bottom, -near)
    
    glVertex3d ( right, bottom, -near)
    glVertex3d ( right, top, -near)
    
    glVertex3d ( left, bottom, -near)
    glVertex3d ( left, top, -near)
    
    #  on far plane
    
    glVertex4d ( right, top, -near, near/far) 
    glVertex4d ( left, top, -near, near/far)
    
    glVertex4d ( right, bottom, -near, near/far)
    glVertex4d ( left, bottom, -near,  near/far)
    
    glVertex4d ( right, bottom, -near, near/far)
    glVertex4d ( right, top,    -near, near/far)
    
    glVertex4d ( left, bottom, -near,  near/far)
    glVertex4d ( left, top,    -near,  near/far)
    
    #  joining near and far plane
    
    glVertex3d( left, top, -near)
    glVertex3d( far/near*left, far/near*top, -far)
    
    glVertex3d ( right, top, -near)
    glVertex3d ( far/near*right, far/near*top, -far)
    
    glVertex3d( left, bottom, -near) 
    glVertex3d( far/near*left, far/near*bottom, -far)
    
    glVertex3d ( right, bottom, -near)
    glVertex3d ( far/near*right, far/near*bottom, -far)
    glEnd()
    glPopAttrib()
    
def drawGrayCube( size ):        #  give it a size parameter rather than bothering to do a glScale

    glPushMatrix()
    glScalef(size, size, size)
    
    #front face
    glColor4f(0.3,0.3,0.3,1.0)
    glPushMatrix()
    glTranslatef(0, 0, 0.5)
    drawSquare(1)
    glPopMatrix()
    #back face
    glColor4f(0.4,0.4,0.4,1.0)
    glPushMatrix()
    glTranslatef(0, 0, -0.5)
    drawSquare(1)
    glPopMatrix()
    #left face
    glColor4f(0.5,0.5,0.5,1.0)
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    glTranslatef(0, 0, -0.5)
    drawSquare(1)
    glPopMatrix()
    #right face
    glColor4f(0.6,0.6,0.6,1.0)
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    glTranslatef(0, 0, 0.5)
    drawSquare(1)
    glPopMatrix()
    
    #top face
    glColor4f(0.7,0.7,0.7,1.0)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glTranslatef(0, 0, -0.5)
    drawSquare(1)
    glPopMatrix()
    #bottom face
    glColor4f(0.8,0.8,0.8,1.0)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0, 0, -0.5)
    drawSquare(1)
    glPopMatrix()
    glPopMatrix()


    
def drawColoredCube( size ):        #  give it a size parameter rather than bothering to do a glScale

    glPushMatrix()
    glScalef(size, size, size)
    
    #front face
    glColor4f(1.0,0.0,0.0,1.0)
    glPushMatrix()
    glTranslatef(0, 0, 0.5)
    drawSquare(1)
    glPopMatrix()
    #back face
    glColor4f(0.5,0.5,0.0,1.0)
    glPushMatrix()
    glTranslatef(0, 0, -0.5)
    drawSquare(1)
    glPopMatrix()
    #left face
    glColor4f(0.5,0.5,0.5,1.0)
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    glTranslatef(0, 0, -0.5)
    drawSquare(1)
    glPopMatrix()
    #right face
    glColor4f(0.0,0.5,0.5,1.0)
    glPushMatrix()
    glRotatef(90, 0, 1, 0)
    glTranslatef(0, 0, 0.5)
    drawSquare(1)
    glPopMatrix()
    
    #top face
    glColor4f(0.5,0.0,0.5,1.0)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glTranslatef(0, 0, -0.5)
    drawSquare(1)
    glPopMatrix()
    #bottom face
    glColor4f(0.5,0.0,0.0,1.0)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0, 0, -0.5)
    drawSquare(1)
    glPopMatrix()

    glPopMatrix()