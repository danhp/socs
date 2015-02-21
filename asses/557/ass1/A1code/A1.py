"""
STUDENT NAME: Daniel Pham
STUDENT ID: 260 526 252

COMP 557: Assignment 1
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

import numpy as np
from numpy import sqrt, arctan2, cos, sin, tan, pi, transpose, rad2deg, deg2rad

from A1DrawHelperFunctions import *

"""
Code layout:
--------------------
Here are some notes on how the code is organized so that you can find your way
around the code.

There are 3 source files provided with this starter code. They are:
A1.py, A1Main.py, A1DrawHelperFunctions.py

A1.py: You ONLY NEED to work with A1.py. Descriptions are given below

A1Main.py : This is the file that you'll execute to start the application. It
contains all the windowing functions and makes appropriate calls to functions
int A1.py or updates variables in A1.py. You DO NOT NEED to make any changes to it.

A1DrawHelperFunctions: This file contains some common drawing routines. Again
you DO NOT NEED to deal with this file.

Now back to A1.py ...
The parts where you'll be adding your code are marked by the
TODO markers along with "BEGIN SOLUTION" and "END SOLUTION" comments.
More specifically the following functions need to be filled in:

drawScene()
Viewport3()
Viewport4()
perspective(fovy, aspect, near, far)
drawMovingViewVolume()

(NOTE: Some IDEs let you navigate to the TODO section. For instance spyder
puts a check mark on the left and a blue bar near the scroll bar.
You can click on the blue bar    to navigate to the TODO section. If you're
using spyder you can also use the "Outline" pane from View-> Windows and Toolbars -> Outline
to find commented sections for adding code.)

Where to start?
----------------
To get an idea about how things are put together you can start from the main
function in A1Main.py (see if __name__ == '__main__'). We use
the GLUT library for windowing (i.e. window creation, update, mouse/keyboard, etc.)

We implemented a class called Window which handles all the necessary glut
callback function calls such as drawing on the display, mouse and keyboard handling, etc.
This assingment does not require you to modify anything in the Window class.
(However, if you want to see how the main camera variables such as pan, tilt and eye position are
updated you can look at the Window.keyboard, Window.mouse, and Window.motion functions)

How does rendering work?
-------------------------
Everytime glut needs to refresh the display it'll call Window.display function
which in turn calls drawMain() (there are a few other calls but they are not relevant
for this assignment). We've setup glut to do double-buffering so the rendering is first done
in the back buffer and finally moved to the front buffer after glutSwapBuffers is called.
This call is also made in Window.display function.

At every frame Window.display calls drawMain(). drawMain() in turn calls the
functions for Viewport 1 to 4. The viewports do not depend on each other, they make
use of the global variables that are defined at the beginning of this file. The
viewport functions also do not modify any of those global variables.

How does animation work?
------------------------
We use glut's glutTimerFunc function which calls Window.timer_func at a time
specified in the Timer_ms variable (all of this is in A1Main.py and just to
restate are not part of the code that you submit). This function in turn
updates all the animation variables (only the moving camera related variables)
and tells glut to update the display.

Numpy:
------
For many operations we use the numpy module. We imported some of the commonly
used functions by name. We also imported numpy as np. So if you want to use
some function from there you can use "np.".

NOTE: In serveral places we used np.eye(N). The eye here refers to the Identity
matrix that is implemented by NumPy which we imported as np. It does NOT have
anything to do with the eye coordinate. np.eye(N) will create an Identity
matrix of size N x N.
(http://docs.scipy.org/doc/numpy/reference/generated/numpy.eye.html)

Drawing using GLU:
------------------
GLU functions usually require a handle to a Quadric. In the starter code we
created a handle called myQuadric (initialized in Window.__init__) which you can reuse.

"""
# ------------    Setup and define global variables  -----------------------

near  =     1.0
far   =     7.0
left  =    -0.5
right =     0.5
bottom =   -0.5
top    =    0.5

# This binary variable handles toggling (Q4)
viewport4Sol1 = True # True: use solution 1, False: use solution 2

# Variables related to the moving camera
movingCameraRadius = 5
movingCameraHeight = 3
movingCameraPos = [0, 0, 0]
movingCameraAngle = 0 # This is the angular position of the moving camera.
                     # It is updated at every frame.

# Size of a single viewport i.e. (sizeViewport x sizeViewport)
sizeViewport = int(350)

# Initial eye position. These are updated by keyboard and mouse
# You only need to use them in appropriate locations.
eyeX  = 0
eyeY  = 0
eyeZ  = 0

# main camera pan and tilt
pan =  0
tilt = 0

myQuadric = 0   # Initialized in initGL after ogl context creation

'''
OpenGL stores 4x4 matrices in column major order and so the
list of list representation that is returned is
transpose of what we want.  For example, in the GL_PROJECTION
matrix, we want a -1 in the 4th row, 3rd column but the getDoublev function
returns a -1 in the 3rd row, 4th column.
This function is not used anywhere in the starter code but it can be used for
debugging.
'''
def getGL_MODELVIEW_PROJ():
    glModelViewMatrix  = transpose(glGetDoublev(GL_MODELVIEW_MATRIX))
    print('GL_MODELVIEW ' , glModelViewMatrix)
    glProjectionMatrix = transpose(glGetDoublev(GL_PROJECTION_MATRIX))
    print('GL_PROJECTION ' , glProjectionMatrix)
    return (glModelViewMatrix , glProjectionMatrix)

# ---- Initializations ----
def initGL():
    '''
    This function gets called at the very beginning and before any of the other
    functions in this file by Window.__init__ All OpenGL related initialization
    is done here.
    '''
    global myQuadric

    glFrontFace(GL_CCW);            #  should be CCW for glQuadric,  but CW for my mesh surface (?)
    glEnable(GL_DEPTH_TEST)         # Enables Depth Testing
    glDepthFunc(GL_LEQUAL)          # The Type Of Depth Test To Do
    glDisable(GL_CULL_FACE)         # Disabled for now
    glClearColor(0.0, 0.0, 0.0, 1.0)   #  defines background color when you run glClear(GL_COLOR_BUFFER_BIT)
    glClearDepth(1)                    #  defines background depth when you run glClear(GL_DEPTH_BUFFER_BIT)

    myQuadric = gluNewQuadric()

# ------------------    Methods for drawing parts of the scene
def drawScene():
    '''
    In this sample scene we have a rotating cube rotating with the moving camera
    '''

    draw3DCoordinateAxes()  #  world coordinates

    #  ---------------   BEGIN SOLUTION  -----------------------
    global myQuadric, movingCameraAngle

    deg = movingCameraAngle

    # Adds a Cube
    glPushMatrix()
    glRotatef(38, 0, 1, 0)
    glTranslatef(1,-0.5, -2)
    drawColoredCube(1)
    glPopMatrix()

    # Adds a Cone
    glPushMatrix()
    glTranslatef(-0.5,0,-2.4)
    glRotatef(90, -2, 0, 0)
    gluCylinder(myQuadric, 0.5, 0, 1.5, 32, 32)
    glPopMatrix()

    # Add a Teapot
    glPushMatrix()
    glColor3f(0,1,1)
    glRotatef(90, 0, -1, 0)
    glTranslatef(0.5,-0.5,1)
    glutSolidTeapot(0.5)
    glPopMatrix()

    # Adds the floor in orange
    glColor3f(1,0.5,0)
    glPushMatrix()
    glBegin(GL_QUADS)
    glVertex3f(-5,-1,-5)
    glVertex3f(-5,-1,5)
    glVertex3f(5,-1,5)
    glVertex3f(5,-1,-5)
    glEnd()
    glPopMatrix()
    #  ---------------   END SOLUTION  -----------------------

# ------ ADD CODE IN drawMovingViewVolume() ------
def drawMovingViewVolume():
    '''
    This function draws the view volume of the camera in viewport 1. This gets
    called by all the viewports that render the view volume of the 1st camera
    (i.e. viewport 2 and 4). There is a function called drawViewVolume in
    A1DrawHelperFunctions.py file that draws a static view volume. You can
    call that functions after applying the appropriate transformations. Note that
    the 'moving' part here refers to the fact that when you pan/tilt or translate
    the first camera, its corresponding view volume will move in viewport 2 and 4.
    '''
    global eyeX, eyeY, eyeZ, pan, tilt, left, right, bottom, top, near, far

    #  ---------------   BEGIN SOLUTION  -----------------------
    glPushMatrix()
    glTranslate(eyeX, eyeY, eyeZ)
    glRotate(-tilt, 1, 0, 0)
    glRotate(pan, 0, -1, 0)
    drawViewVolume(left, right, bottom, top, near, far)
    glPopMatrix()
    #  ---------------   END SOLUTION  -----------------------

def drawMovingCamera():
    '''
    This function draws the 4th viewport camera as seen by the other viewports.
    Since the camera is being animated we need to think about the correct transformations
    to apply for it to be rendered correctly in all the viewports.
    There is a functions called drawCamera which will draw a static camera.
    We just reuse that function from here with the appropriate transformation.
    '''
    global movingCameraPos, myQuadric, movingCameraRadius, movingCameraAngle

    #  Keep track of where the moving camera is with global variables.
    #  radius is the radius of circle of the path of moving camera.
    #  The center of the circle is (0, 0, -(near+far)/2)
    movingCameraTilt = -rad2deg(arctan2(movingCameraPos[1], movingCameraRadius))
    deg = movingCameraAngle
    glPushMatrix()
    #  position and move this camera
    glTranslatef( movingCameraPos[0],  movingCameraPos[1], movingCameraPos[2])
    glRotatef( deg, 0, 1, 0  )
    glRotatef(movingCameraTilt, 1, 0, 0)
    drawCamera()
    glPopMatrix()

def drawCamera():
    '''
    This function draws a static camera. This should get called called by drawMovingCamera()
    after appropriate transformation
    '''
    glPushMatrix()
    #  define moving camera in object coordinates
    glRotatef(180, 0, 1, 0)   #  initially pointed in -z direction
    glScalef(0.5, 0.5, 1.0)
    drawGrayCube(.5)
    glTranslatef(0,0,.5)
    gluCylinder(myQuadric, .2, .3,  .3, 10, 10)   # cone to indicate direction
    glPopMatrix()



def Viewport1():
    global eyeX,  eyeY,  eyeZ, left, right, bottom, top, near, far
    global pan, tilt
    global sizeViewport

    ''' ----------------- VIEWPORT 1   -----------------------'''

    glViewport(0, 0, int(sizeViewport), int(sizeViewport))

    eye =    [eyeX, eyeY,  eyeZ]
    lookat = [0.0, 0.0, -1.0]
    updir =  [0.0, 1.0,  0.0]

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(left, right, bottom, top, near, far)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt( eye[0], eye[1], eye[2],
               eye[0] + tan(pan/180.0*pi), eye[1] + tan(tilt/180.0*pi), eye[2] - 1,
               updir[0], updir[1], updir[2])
    drawScene()
    drawMovingCamera()
# ---- To see the scene correctly in Viewport2() implement drawMovingViewVolume()
def Viewport2():
    global eyeX,  eyeY,  eyeZ, left, right, bottom, top, near, far
    global pan, tilt
    global sizeViewport

    '''
     ----------------- VIEWPORT 2   -----------------------

    This is from the viewpoint of a second camera, which is viewing the scene from a distance.
    Note the camera uses orthographic projection, not perspective.

    In this viewport (2), the viewvolume (white lines) should rotate and translate
    in response to the keyboard and mouse input.
    This view volume motion should be consistent with what is seen in viewport 1.
    '''

    glViewport(int(sizeViewport),0,int(sizeViewport),int(sizeViewport))

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glOrtho(-5, 5, -5, 5, -1, 50)

    eye2    =  [2.0, 1, 4.0]
    lookat2 =  [0.0, 0.0, -(near + far)/2]
    updir   =  [0.0, 1.0, 0.0]

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluLookAt( eye2[0], eye2[1], eye2[2], lookat2[0], lookat2[1], lookat2[2], updir[0], updir[1], updir[2])

    drawScene()
    drawMovingCamera()
    drawMovingViewVolume()


# ---- ADD CODE IN Viewport3()----
def Viewport3():
    global eyeX,  eyeY,  eyeZ, left, right, bottom, top, near, far
    global pan, tilt
    global sizeViewport

    ''' ----------------- VIEWPORT 3   ----------------------- '''
    #  Orthographic projection onto x + y + z = 1 plane  (isometric projection)

    glViewport(0,int(sizeViewport),int(sizeViewport),int(sizeViewport))

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-3, 3, -3, 3, -3, 50)

    updir   =  [0.0, 1.0, 0.0]

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt( 7, 4, 5, 0, 0, 0, updir[0], updir[1], updir[2])

    #  Set the M_projective matrix.
    M = projective(near,far)

    glPushMatrix()
    glScalef(1.0, 1.0, -1.0)   #  flip the z axis to make xyz left handed
    draw3DCoordinateAxes()
    glPopMatrix()

    #  ---------------   BEGIN SOLUTION  -----------------------
    glPushMatrix()

    glTranslatef(-1, -1, 1)
    glScalef(2/(right-left), 2/(top-bottom), 2/(far-near))
    glTranslatef(-left, -bottom, near)

    glMultMatrixd(np.transpose(M))

    drawViewVolume(left, right, bottom, top, near, far)

    glTranslate(eyeX, eyeY, -eyeZ)
    glRotate(tilt, -1, 0, 0)
    glRotate(pan, 0, 1, 0)
    drawScene()
    drawMovingCamera()

    glPopMatrix()

    #  ---------------   END SOLUTION  -----------------------
# ----- Viewport 4 related functions
'''
 The following few functions are relevant to Viewport4 which is why they are placed
 close to Viewport4 function
'''
'''
Implementation of canonical rotations are given below. These functions return
numpy.matrix which makes matrix multiplication easier. For instance if A and B
are numpy.matrix then their product can be expressed as A * B in python.

Caution: If A and B are NOT numpy.matrix then A * B implies element-wise product.
'''
def rotateX(angle_deg):
    theta = deg2rad(angle_deg)
    R = [ [1, 0, 0, 0],
         [0, cos(theta ), sin(theta), 0],
         [0, -sin(theta), cos(theta ),  0],
          [0, 0, 0, 1]]
    return np.matrix(R)

def rotateY(angle_deg):
    theta = deg2rad(angle_deg)
    R = [[cos(theta ), 0, -sin(theta), 0],
         [0, 1, 0, 0],
         [sin(theta), 0, cos(theta ),  0],
         [0, 0, 0, 1] ]
    return np.matrix(R)

def translate(translate_vec):
    '''
    translate is a (1, 3) vector
    The function is called as: translate([x, y, z])
    '''
    # NOTE: Here np.eye refers to the Identity matrix implemented by NumPy (imported as np)
    # It does NOT have anything to do with the eye coordinates.
    # np.eye(N) will create an N x N Identity matrix.
    T = np.eye(4);
    T[:3,3] = translate_vec
    return np.matrix(T)

def scale(s):
    '''
    s is a (1, 3) vector
    The function is called as: scale([sx, sy, sz])
    '''
    S = np.eye(4);
    S[0][0] = s[0]
    S[1][1]= s[1]
    S[2][2] = s[2]
    return np.matrix(S)

def projective(near,far):
    M = np.zeros((4, 4)) # This creates a 4 x 4 matrix filled with zeros
    M[0][0] = near
    M[1][1] = near
    M[2][2] = near + far
    M[3][2] = -1
    M[2][3] = near*far
    return M

# ---- ADD CODE IN perspective(fovy, aspect, near, far) ----
def perspective(fovy, aspect, near, far):
    '''
    Implement the perspective matrix here for Q4.
    This function needs to be implemented using projective(near, far)
    and normalization technique given in class. You cannot just look up
    gluPerspective on the web. You are free to use any of the transformation
    functions defined above e.g. scale, translate, and rotate.
    '''
    # NOTE: Here np.eye refers to the Identity matrix implemented by NumPy (imported as np)
    # It does NOT have anything to do with the eye coordinates.
    # np.eye(N) will create an N x N Identity matrix.
    P = np.eye(4)
    #  ---------------   BEGIN SOLUTION  -----------------------
    P = P * translate([0, 0, 1])
    P = P * scale([2/(near * aspect * tan(deg2rad(fovy)/2)),
                   2/(near * tan(deg2rad(fovy)/2)),
                   -2/(near - far)])
    P = P * translate([0, 0, near])
    P = P * projective(near, far)
    #  ---------------   END SOLUTION  -----------------------
    return np.matrix(P)

# ---- ADD CODE IN Viewport4() ----
def Viewport4():
    global eyeX,  eyeY,  eyeZ, left, right, bottom, top, near, far
    global pan, tilt
    global sizeViewport
    global movingCameraPos, movingCameraRadius, movingCameraAngle


    ''' -----------------  VIEWPORT 4   -----------------------

    Here we draw the image seen by a camera that is travelling in a circle.
    and looking toward the center of the circle.  See drawMovingCamera().
    The camera position is defined by a variable called "movingCameraPos" which
    is updated at every frame in the updateAnimationVariables() function.
    '''

    glViewport(int(sizeViewport),int(sizeViewport),int(sizeViewport),int(sizeViewport))
    if(not viewport4Sol1):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, # 57/2,    #fov in degrees
                       1,     #aspect
                       .01,  #near
                       20)  #far
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        lookat = [0.0, 0.0, -(near + far)/2]
        updir =  [0.0, 1.0, 0.0]

        #  ---------------   BEGIN SOLUTION  -----------------------
        gluLookAt(movingCameraPos[0], movingCameraPos[1], movingCameraPos[2],
                  lookat[0], lookat[1], lookat[2],
                  updir[0], updir[1], updir[2])
        drawScene()
        drawMovingViewVolume()
        #  ---------------   END SOLUTION  -----------------------
    else: # perform projection and lookat without using gl functions

        #  ---------------   BEGIN SOLUTION  -----------------------
        glMultMatrixd(np.transpose(perspective(60, 1, near, far)))

        T = np.eye(4)
        T = T * translate([-movingCameraPos[0], -movingCameraPos[1], -movingCameraPos[2]])

        R = rotateY(movingCameraAngle)

        M = R * T
        glMultMatrixd(np.transpose(M))

        drawScene()
        drawMovingViewVolume()
        #  ---------------   END SOLUTION  -----------------------

    # ----------------- DONE RENDERING VIEWPORTS  -----------------------

def drawMain():
    '''
    This is the main drawing function. All drawing code should be called by this
    function. This function gets called from Scene.display which is the callback
    function for glutDisplayFunc
    '''

    #  These commands apply to the window,  not to the individual viewports.

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    Viewport1()

    Viewport2() # Add your solution to viewport 2 in the Viewport2() function

    Viewport3() # Add your solution to viewport 3 in the Viewport3() function

    Viewport4() # Add your solution to viewport 4 in the Viewport4() function



def updateAnimationVariables():
    '''
    All variables that are updated during animation are updated here. This function
    gets called from Window.timer_func() that is implemented in A1Main.py
    The only animated part required for the assignment is the moving camera.
    '''
    # The height of the camera is modified by the user by pressing 'i'/'k' (i.e. not animated)
    # All mouse/keyboard interactions are handled in the Window class (A1Main.py)
    # Only thing changing per frame is the angular position which is what is updated
    # in this function.
    global movingCameraAngle, movingCameraPos, movingCameraRadius, near, far
    theta = deg2rad(movingCameraAngle);
    movingCameraAngle = movingCameraAngle + 1
    movingCameraPos =    [ movingCameraRadius*sin( theta ),  movingCameraHeight, -(near+far)/2 + movingCameraRadius*cos( theta )]
