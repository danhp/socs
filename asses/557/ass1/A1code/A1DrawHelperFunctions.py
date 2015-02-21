# -*- coding: utf-8 -*-
"""
A1DrawHelperFunctions.py

This file contains some helper functions for drawing using OpenGL. These are
not critical for the assignment and were placed here to reduce clutter.

IMPORTANT NOTE:
---------------
Make sure that this file is in the same directory as the A1 starter code.

If you choose to add your own drawing helper functions please mark them clearly
using comments and also mention them in a README file.
"""

try:
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print '''
ERROR: PyOpenGL not installed properly.
        '''
  sys.exit()
  
def draw3DCoordinateAxes():

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


def drawViewVolume(left, right, bottom, top, near, far):
    '''
    Draws a view volume defined by (left, right, bottom, top, near, far)
    '''
    #  assumes camera is at origin
    
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

def drawSquare(size):        #  give it a size parameter rather than bothering to do a glScale
    glBegin(GL_QUADS)
    glVertex3f(-0.5*size, -0.5*size, 0)
    glVertex3f(0.5*size, -0.5*size,  0)
    glVertex3f(0.5*size, 0.5*size,   0)
    glVertex3f(-0.5*size, 0.5*size,  0)
    glEnd()

def drawGrayCube( size ):        #  give it a size parameter rather than bothering to do a glScale

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


    
def drawColoredCube( size ):        #  give it a size parameter rather than bothering to do a glScale

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