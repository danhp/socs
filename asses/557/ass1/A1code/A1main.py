# -*- coding: utf-8 -*-
"""
A1Main.py

This file handles all the windowing functions and does not require you to add
any code for this assignment. All your implementations should be in A1.py

IMPORTANT NOTE: Make sure to change the import filename if you happen to
change the name of A1.py to something else make sure to update this file
"""
from __future__ import division
import sys

try:
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print '''
ERROR: PyOpenGL not installed properly.
        '''
  sys.exit()

# ---- IMPORTANT: Update the import filename if you change the name of your file
import A1

camera_gain = 0.1*300/A1.sizeViewport


FPS = 60            # maximum frame rate
Timer_ms = 1000/FPS

# --- Window callback handlers ---
"""
The rest of the code below are mostly for perfoming GUI operations and you do
not need to deal with them for this assignment.
"""
class Window:

    def __init__(self):
        self.prev_x = self.prev_y = 0
        self.mouse_button = -1
        A1.initGL()

    def drawOverlay(self):
        '''
          Draw 2 lines to separate the 4 viewports
        '''
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, 2 * int(A1.sizeViewport), 2 * int(A1.sizeViewport))
        gluOrtho2D(0, 2 * int(A1.sizeViewport), 0, 2 * int(A1.sizeViewport))
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)
        glPushMatrix()

        glBegin(GL_LINES)
        glVertex2i(0, int(A1.sizeViewport))
        glVertex2i(int(2 * A1.sizeViewport), int(A1.sizeViewport))
        glVertex2i(int(A1.sizeViewport), 0)
        glVertex2i(int(A1.sizeViewport), 2 * int(A1.sizeViewport))
        glEnd()

        glPopMatrix()
        glPopAttrib()
        glEnable(GL_DEPTH_TEST)

    def display(self):

        A1.drawMain() # draw the different scenes in the 4 viewports

        self.drawOverlay()
        glutSwapBuffers()
        glFlush()

    def reshape(self, width, height):
        self.width = width
        self.height = height

        A1.sizeViewport = int(min(width, height) / 2)


    def mouse(self, button, state, x, y):

        # Variables to keep track of the mouse events.
        self.mouse_button = button

        # If state is 0, it's a press event.
        if(state == 0):
            self.prev_x = x
            self.prev_y = y
        else:
            pass

    def motion(self, x, y):

        # Variables to keep track of the mouse events.
        displacement = [x - self.prev_x, y - self.prev_y ]
        self.prev_x = x
        self.prev_y = y
        # If left button is pressed, we pan or tilt the camera.
        if self.mouse_button == 0:
            A1.pan = A1.pan + camera_gain * displacement[0]
            A1.tilt = A1.tilt - camera_gain * displacement[1]
        # Else if right button is pressed, we translate.
        elif self.mouse_button == 2:
            A1.eyeX = A1.eyeX + camera_gain * displacement[0]
            A1.eyeZ = A1.eyeZ + camera_gain * displacement[1]

    def keyboard(self, key, x, y ):

        if key == '\033':
            sys.exit()
        elif key == 'p' or key == 'P':
            from scipy.misc import imsave
            from numpy import flipud
            filename = 'a1.png'
            print('saving screen shot to %s' %filename)
            glReadBuffer(GL_FRONT)
            im = glReadPixels(0, 0, self.width, self.height,
                                   GL_RGBA, GL_UNSIGNED_INT)
            imsave('a1.png', flipud(im))
            im_depth = glReadPixels(0, 0, self.width, self.height, GL_DEPTH_COMPONENT, GL_FLOAT)
            imsave('a1_depth.png', flipud(im_depth))
            print('done')

        elif key == 'w' or  key == 'W':    #  W moves eye forward, i.e. in the -z direction.
            A1.eyeZ = A1.eyeZ - camera_gain
        elif key == 's' or  key == 'S':    #  S moves eye backward, i.e. in the z direction.
            A1.eyeZ = A1.eyeZ + camera_gain
        elif key == 'a' or  key == 'A':
            A1.eyeX = A1.eyeX - camera_gain
        elif key == 'd' or  key == 'D':
            A1.eyeX = A1.eyeX + camera_gain
        elif key == 'i' or  key == 'I':
            A1.movingCameraHeight = A1.movingCameraHeight + camera_gain
        elif key == 'k' or  key == 'K':
            A1.movingCameraHeight = A1.movingCameraHeight - camera_gain
        elif key == 't' or key == 'T':
            A1.viewport4Sol1 = not A1.viewport4Sol1

    def specialKeyboard(self, key, x, y):

        if key == GLUT_KEY_LEFT:        # Left
            A1.pan  = A1.pan - 1
        elif key == GLUT_KEY_RIGHT:     # Right
            A1.pan = A1.pan + 1
        elif key == GLUT_KEY_UP:        # Up
            A1.tilt = A1.tilt + 1
        elif key == GLUT_KEY_DOWN:      # Down
            A1.tilt = A1.tilt - 1

    def timer_func(self, value):
        '''
        timer_func gets called by glut's glutTimerFunc. It simply updates all
        the variables that are updated during animation and tells glut to update
        the display by calling glutPostRedisplay function.
        '''

        A1.updateAnimationVariables()
        glutPostRedisplay()

        # The glutTimerFunc expires after each call. Therefore we need to
        # create a new timer callback
        glutTimerFunc(value, self.timer_func, value)

# -------------------   MAIN   ------------------------------
if __name__ =='__main__':
     #   -------------    Set up the window
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

    glutCreateWindow('COMP557 A1')
    glutReshapeWindow(A1.sizeViewport*2,A1.sizeViewport*2)

    window = Window()
    glutReshapeFunc(window.reshape)
    glutDisplayFunc(window.display)
    glutKeyboardFunc(window.keyboard)
    glutSpecialFunc(window.specialKeyboard)
    glutMouseFunc(window.mouse)
    glutMotionFunc(window.motion)
    glutTimerFunc(int(Timer_ms), window.timer_func, int(Timer_ms))
    glutMainLoop()
