# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 21:08:24 2015

@author: fmannan
"""
# To do: send special controls to view methods
from __future__ import division # use floating-point division by default
import sys, time
from threading import Timer, Event
#import sched
import numpy as np
import scipy.misc
try:
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print('ERROR: PyOpenGL not installed properly.')
  sys.exit()
from GLDrawHelper import *
from GeomTransform import *


def lookAt(eye, center, up):
    '''
    lookAt is a wrapper around gluLookAt. eye, center, and up are python lists.
    '''
    gluLookAt(eye[0], eye[1], eye[2], 
              center[0], center[1], center[2], 
              up[0], up[1], up[2])  
                  
"""
x > y means x contains y

GLUTWindow > View > Model

GLUTWindow: Handles most common type of user interactions. It interprets the keyboard
and mouse motions and generates view transformation commands such as translate or rotate.
It can send unhandled interactions to the view object for special processing.

View: This essentially handles the view transformation. 

Model: This can be considered as one large model in the models coordinate system.

The idea is to create an instance of the scene and view it in different ways.
A view can contain another view as its child. From the parent view's point of view
its child is a scene. This makes it possible to render a scene with a camera
in it from an external observer's point of view.
"""
class Model:
    '''
    Base class for all types of Model. The purpose of the Model class is to 
    transparently manage OpenGL's Display List. Display List allows OpenGL to
    evaluate and optimize rendering instructions and efficiently render the 
    contents of a Display List. This improves the rendering time and allows
    rendering complex scenes such as fractals and L-systems.
    '''
    def __init__(self):
        self.DLId = None
        
    def init(self):
        self.pQuadric = gluNewQuadric()
        if(self.DLId is None):
            self.DLId = glGenLists(1)
        glNewList(self.DLId, GL_COMPILE);
        self.draw_scene()
        glEndList()
    
    def display(self):
        if(self.DLId is not None):
            glCallList(self.DLId)
        else:
            print('Warning: Display List is not used for rendering')
            self.draw_scene()

class View:
    """
    Render scene from different views. Different views are specialization of this
    base view. This base class implements a default view with identity as modelview
    and projection matrix.
    
    A view can contain a scene or another view as its child.
    All reshape calls terminate at the view
    What if a subview does its projection in the reshape function?
    One options is to not have projection transformation in the reshape
    other option is for the view to check if the subview is also a view and then
    call it. The subview may set the viewport so the current view needs to reset the 
    viewport. 
    """
    def __init__(self, child, camera = dict()):
        assert(bool(child.display))
        assert(type(camera) is dict)

        self.child = child

        self.TRANSLATE_DELTA = 0.02
        self.ROTATE_DELTA = 0.8
        
        # camera can be represented in mulitple ways. The view matrix is 
        # the most general. However it is more convenient to define the
        # camera either as (fovy, aspect, near, far)
        # or frustum (left, right, bottom, top, near, far)
        # or ortho (left, right, bottom, top, near, far)

        # To avoid any initialization error the camera has to be specified in
        # one of the above form. Also if it's specified in the 2nd and 3rd form
        # then the type of the camera has to be explicitly specified.

        # if left, right, near, far are defined but not projection_type then
        # that should be an error
        assert(not (camera.has_key('left') and camera.has_key('right') and
            camera.has_key('near') and camera.has_key('far') and
            not camera.has_key('type')) )

        # if no camera specification is provided then we assume a default
        # orthographic camera at the following default coord
        self.eye = np.array(camera.get('eye', [0, 0, 1]))
        self.lookat = normalize(np.array(camera.get('center', np.zeros(3))) - self.eye)
        self.up = normalize(np.array(camera.get('up', [0, 1, 0])))
            
        # ensure that (normalized) lookat and up vectors are not parallel
        assert(1 - abs(np.dot(self.lookat, self.up)) > 1e-8)
        cam_right = normalize(np.cross(self.lookat, self.up))
        self.up = normalize(np.cross(cam_right, self.lookat))
        
        self.projection_type = camera.get('type', 'ortho')
        
        # if camera type was specified make sure that it is specificed in the 
        # correct form
        assert(self.projection_type == 'ortho' or 
                self.projection_type == 'perspective')
                
        # all camera specs need to have near and far defined
        self.near = camera.get('near', 0.1)
        self.far = camera.get('far', 100.0)        
        self.left = camera.get('left', -1)
        self.right = camera.get('right', 1)
        self.top = camera.get('top', 1)
        self.bottom = camera.get('bottom', -1)
        
        if(camera.has_key('fovy') and camera.has_key('aspect')):
            self.projection_type = 'perspective'
            self.fovy = camera['fovy']
            self.aspect = camera['aspect']
            self.top = self.near * np.tan(np.deg2rad(self.fovy/2.))
            self.bottom = -self.top
            self.right = self.aspect * self.top
            self.left = -self.right
        elif(self.projection_type == 'perspective'): # spec as glFrustum
            pass
        else: # has to be ortho
            pass
        
    def init(self):
        self.pQuadric = gluNewQuadric()
        if(hasattr(self.child, 'init')):
            self.child.init()
            
    def reshape(self, width, height):
        self.width = width
        self.height = height
        
        if(hasattr(self.child, 'reshape')):
            self.child.reshape(width, height)
            
        glViewport(0, 0, self.width, self.height)
        self.aspect = float(self.width) / self.height
        if(self.projection_type == 'perspective'):
            self.top = self.near * np.tan(np.deg2rad(self.fovy/2.))
            self.bottom = -self.top
            self.right = self.aspect * self.top
            self.left = -self.right
    
    def draw_camera_frame(self):
        '''
        Draw the current camera's frame and view volume
        '''
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        glPushMatrix()
        glLoadIdentity()
        lookAt(self.eye, self.eye + self.lookat, self.up)
        M = glGetDoublev(GL_MODELVIEW_MATRIX)
        glPopMatrix()
        InvM = np.linalg.inv(M)
        glMultMatrixd(InvM)
        glPushMatrix()
        glScalef(.25, .25, .25)
        draw3DCoordinateAxesQuadrics(self.pQuadric)
        glPopMatrix()
        #drawViewVolume(self.left, self.right, self.bottom, 
        #               self.top, self.near, self.far)
        # inverser of projection * 2x2x2 cube
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(self.fovy, self.aspect, self.near, self.far)
        Proj = glGetDoublev(GL_MODELVIEW_MATRIX)
        glPopMatrix()
        glMultMatrixd(np.linalg.inv(Proj))
        glutWireCube(2.0)
        glPopMatrix()
    
    def display(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if(self.projection_type == 'ortho'):
            glOrtho(self.left, self.right, self.bottom, self.top, self.near, self.far)
        else:
            gluPerspective(self.fovy, self.aspect, self.near, self.far)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        lookAt(self.eye, self.eye + self.lookat, self.up)
        if hasattr(self.child, 'draw_camera_frame'):
            self.child.draw_camera_frame()
            self.child.child.display()
        else:
            self.child.display()

    def save_screenshot(self, filename = 'screenshot'):
        print('saving screen shot to %s' %filename)
        glReadBuffer(GL_FRONT)
        im = glReadPixels(0, 0, self.width, self.height, 
                               GL_RGBA, GL_UNSIGNED_INT)
        scipy.misc.imsave(filename + '.png', np.flipud(im))
        
        im_depth = glReadPixels(0, 0, self.width, self.height, GL_DEPTH_COMPONENT, GL_FLOAT)
        scipy.misc.imsave( filename + '_depth.png', np.flipud(im_depth))
        print('done')
                           
    def pan(self, angle_deg):
        ''' rotate lookat about the up vector'''
        self.lookat = normalize(np.dot(np.array(rotate(angle_deg, self.up)[:3,:3]), self.lookat))
    
    def panLeft(self, angle_deg = None):
        if(angle_deg is None):
            angle_deg = self.ROTATE_DELTA
        self.pan(angle_deg)
    
    def panRight(self, angle_deg = None):
        if(angle_deg is None):
            angle_deg = -self.ROTATE_DELTA
        self.pan(angle_deg)

    def tilt(self, angle_deg):
        '''rotate lookat and up about (lookat x up) vector'''
        cam_right = np.cross(self.lookat, self.up)
        
        self.up = normalize(np.dot(np.array(rotate(angle_deg, cam_right)[:3,:3]), self.up))
        self.lookat = normalize(np.dot(np.array(rotate(angle_deg, cam_right)[:3,:3]), self.lookat))
        
    def tiltUp(self, angle_deg = None):
        if(angle_deg is None):
            angle_deg = self.ROTATE_DELTA
        self.tilt(abs(angle_deg))

    def tiltDown(self, angle_deg = None):
        if(angle_deg is None):
            angle_deg = -self.ROTATE_DELTA
        self.tilt(-abs(angle_deg))
        
    def roll(self, angle_deg):
        '''rotate up about the lookat vector '''
        self.up = normalize(np.dot(np.array(rotate(angle_deg, -self.lookat)[:3,:3]), self.up))
  
    def rollLeft(self, amount = None):
        if amount is None: amount = self.ROTATE_DELTA
        self.roll(abs(amount))
    
    def rollRight(self, amount = None):
        if amount is None: amount = -self.ROTATE_DELTA
        self.roll(-abs(amount))
        
    def translate(self, vec):
        self.eye += vec
        
    def translateLR(self, amount):
        cam_right = normalize(np.cross(self.lookat, self.up))
        
        self.eye = self.eye + cam_right * amount
    
    def translateUD(self, amount):
        self.up = normalize(self.up)
        self.eye = self.eye + self.up * amount

    def translateFB(self, amount):
        self.lookat = normalize(self.lookat)
        self.eye = self.eye + self.lookat * amount
    
    def translateForward(self, amount = None):
        if amount is None: amount = self.TRANSLATE_DELTA
        self.translateFB(abs(amount))
    
    def translateBackward(self, amount = None):
        if amount is None: amount = -self.TRANSLATE_DELTA
        self.translateFB(-abs(amount))
    
    def translateRight(self, amount = None):
        if amount is None: amount = self.TRANSLATE_DELTA
        self.translateLR(abs(amount))
        
    def translateLeft(self, amount = None):
        if amount is None: amount = -self.TRANSLATE_DELTA
        self.translateLR(-abs(amount))
        
    def translateUp(self, amount = None):
        if amount is None: amount = self.TRANSLATE_DELTA
        self.translateUD(abs(amount))
        
    def translateDown(self, amount = None):
        if amount is None: amount = -self.TRANSLATE_DELTA
        self.translateUD(-abs(amount))

    def __orthogonalize_up(self):
        cam_right = normalize(np.cross(self.lookat, self.up))
        self.up = normalize(np.cross(cam_right, self.lookat))       
    
    def translateArcBallFB(self, amount):
        u = normalize(-self.eye)
        self.eye = self.eye + u * amount
        
    def translateArcBallForward(self, amount = None):
        if amount is None: amount = self.TRANSLATE_DELTA
        self.translateFB(abs(amount))
    
    def translateArcBallBackward(self, amount = None):
        if amount is None: amount = -self.TRANSLATE_DELTA
        self.translateFB(-abs(amount))    

    def rotateArcBallLR(self, amount):
        # rotate eye position about the Y-axis
        # movements can seem unnatural since mouse picking is not used
        sgn = np.sign(np.dot(self.up, [0, 1, 0]))
        self.eye = np.dot(np.array(rotate(amount, [0, sgn, 0])[:3,:3]), self.eye)
        self.lookat = np.dot(np.array(rotate(amount, [0, sgn, 0])[:3,:3]), self.lookat)
        self.up = np.dot(np.array(rotate(amount, [0, sgn, 0])[:3,:3]), self.up)
    
    def rotateArcBallUD(self, amount):
        cam_right = normalize(np.cross(self.lookat, self.up))
        self.eye = np.dot(np.array(rotate(amount, cam_right)[:3,:3]), self.eye)
        self.lookat = np.dot(np.array(rotate(amount, cam_right)[:3,:3]), self.lookat)
        self.up = np.dot(np.array(rotate(amount, cam_right)[:3,:3]), self.up)
    
    def rotateArcBallLeft(self, amount = None):
        if amount is None: amount = self.ROTATE_DELTA
        self.rotateArcBallLR(abs(amount))
        
    def rotateArcBallRight(self, amount = None):
        if amount is None: amount = -self.ROTATE_DELTA
        self.rotateArcBallLR(-abs(amount))
    
    def rotateArcBallUp(self, amount = None):
        if amount is None: amount = self.ROTATE_DELTA
        self.rotateArcBallUD(abs(amount))
    
    def rotateArcBallDown(self, amount = None):
        if amount is None: amount = -self.ROTATE_DELTA
        self.rotateArcBallUD(-abs(amount))    
        
    def timer_func(self, value):
        '''
        Call the childs timer function unless it's a View itself
        '''
        if(hasattr(self.child, 'timer_func') and 
            not hasattr(self.child, 'draw_camera_frame')):
            self.child.timer_func(value)

#------ GLUTWindow -------------
EventQueue = []  # queue of events for stopping all threads when ESC is pressed

class GLUTWindow:
    """ Every glut window handles some user input and periodically draws to the
        display. User inputs such as mouse moves are first passed to the registered
        class and handled in a consistent way. 

        Types of events that are generated are:
        Rotate, Translate, Zoom
        
        View handler is the class that gets the inputs. The view handler can 
        monitor additional unhandled special motions.
    """
        
    def __init__(self, window_name, view, window_size, window_pos = [], timer_time_ms = 10):
        self.window_name = window_name;
        self.view = view
        
        if(len(window_pos) > 0):
            glutInitWindowPosition(int(window_pos[0]), int(window_pos[1]))
        if(len(window_size) > 0):
            glutInitWindowSize(int(window_size[0]), int(window_size[1]))
            
        self.id = glutCreateWindow(self.window_name)
        print(window_name, window_size, window_pos, self.id)
        
        # registers self to glut callback function
        # can ask scene_handler about which functions it wants to respond to
        glutReshapeWindow(int(window_size[0]), int(window_size[1]))
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutSpecialFunc(self.specialKeyboard)
        glutMouseFunc(self.mouse)
        glutMotionFunc(self.motion)
        self.timer_time_ms = int(timer_time_ms);
        if(self.timer_time_ms > 0):
            self.timer = Timer(self.timer_time_ms/1000., self.idle_func)
            self.timer.start()
            
        self.init()
        if(hasattr(view, 'init')): # if scene wants to be initialized
            self.view.init()
    
    def init(self): # default init if the scene handler doesn't have one
        glFrontFace(GL_CCW);           #  should be CCW for glQuadric,  but CW for my mesh surface (?)
        glEnable(GL_DEPTH_TEST)        # Enables Depth Testing
        glDepthFunc(GL_LEQUAL)         # The Type Of Depth Test To Do
        glEnable(GL_CULL_FACE)
        glClearColor(0.0, 0.0, 0.0, 1.0) #  defines background color when you run glClear(GL_COLOR_BUFFER_BIT)
        glClearDepth(1.0)
        
    def reshape(self, width, height):
        self.width = width
        self.height = height

        # this is the entry point of all reshape functions so do all the cleanup
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        if(bool(self.view.reshape)):
            self.view.reshape(width, height)
        
        # set viewport after all children has executed
        glViewport(0, 0, self.width, self.height)
    
    def display(self):
        # Note: glClear should be called only at the very beginning
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # do all the drawing
        self.view.display()
        glutSwapBuffers() # swap buffer only at the end
    
    def keyboard(self, key, x, y):
        if key == chr(27):   # Esc pressed
            for event in EventQueue:
                #print event
                event.set()
            sys.exit(0)
        elif key == 'w' or  key == 'W':    #  W moves eye forward, i.e. in the -z direction.
            self.view.translateForward()
        elif key == 's' or  key == 'S':    #  S moves eye backward, i.e. in the z direction.
            self.view.translateBackward()
        elif key == 'a' or  key == 'A':
            self.view.translateLeft()
        elif key == 'd' or  key == 'D':
            self.view.translateRight()
        elif key == 'r' or  key == 'R':
            self.view.translateUp()
        elif key == 'f' or  key == 'F':
            self.view.translateDown()
        elif key == 'z' or key == 'Z':
            self.view.rollLeft()
        elif key == 'x' or key == 'X':
            self.view.rollRight()
        elif((key == 'o' or key == 'O') and 
             (hasattr(self.view, 'save_screenshot'))):
            print('here')
            self.view.save_screenshot(self.window_name)
        elif(hasattr(self.view, 'keyboard')):
            self.view.keyboard(key, x, y)
    
    def mouse(self, button, state, x, y):
        # Variables to keep track of the mouse events.
        self.mouse_button = button
        
        # If state is 0, it's a press event.
        if(state == GLUT_DOWN):    
            self.prev_x = x
            self.prev_y = y
        else: 
            pass
        
        if button == 3:
            # scroll up
            self.view.translateArcBallBackward()
        elif button == 4:
            self.view.translateArcBallForward()
      
    def motion(self, x, y):
        # Variables to keep track of the mouse events.
        Delta = np.array([x - self.prev_x, y - self.prev_y ]) * 0.1
        self.prev_x = x
        self.prev_y = y
        modifier = glutGetModifiers()
        #print(modifier)
        # If left button is pressed, we pan or tilt the camera.
        if self.mouse_button == GLUT_LEFT_BUTTON:
            if(modifier == GLUT_ACTIVE_CTRL):
                self.view.rotateArcBallLR(-Delta[0])
                self.view.rotateArcBallUD(-Delta[1])
            else:
                self.view.pan(-Delta[0])
                self.view.tilt(-Delta[1])
        # Else if right button is pressed, we translate.
        elif self.mouse_button == GLUT_RIGHT_BUTTON:
            if(modifier == GLUT_ACTIVE_CTRL):
                self.view.translateArcBallFB(Delta[1])
            else:
                self.view.translateFB(-Delta[1])
                self.view.translateLR(Delta[0])
        elif self.mouse_button == GLUT_MIDDLE_BUTTON:
            self.view.rotateArcBallLR(-Delta[0])
            self.view.rotateArcBallUD(-Delta[1])
            
        
    def specialKeyboard(self, key, x, y):
        modifier = glutGetModifiers()        
        if key == GLUT_KEY_LEFT:        # Left
            if(modifier == GLUT_ACTIVE_CTRL):
                self.view.rotateArcBallLeft()
            else:
                self.view.panLeft()
        elif key == GLUT_KEY_RIGHT:     # Right
            if(modifier == GLUT_ACTIVE_CTRL):
                self.view.rotateArcBallRight()
            else:
                self.view.panRight()
        elif key == GLUT_KEY_UP:        # Up
            if(modifier == GLUT_ACTIVE_CTRL):
                self.view.rotateArcBallUp()
            else:
                self.view.tiltUp()
        elif key == GLUT_KEY_DOWN:      # Down
            if(modifier == GLUT_ACTIVE_CTRL):
                self.view.rotateArcBallDown()
            else:
                self.view.tiltDown()
    
    def idle_func(self):
        self.stop_event = Event()
        EventQueue.append(self.stop_event)
        while not self.stop_event.isSet():
            self.stop_event.wait(self.timer_time_ms / 1000.)
            self.view.timer_func(self.id)
            glutPostWindowRedisplay(self.id)
            

# ------------ Render a sample scene for testing --------------------    
class SampleScene(Model):
    """
    Scene class only deals with models in the scene. 
    """        
    def __init__(self):
        Model.__init__(self)
        
    def init(self):
        self.quadric = gluNewQuadric()
        Model.init(self)        

    def draw_scene(self):
        glPushMatrix()
        draw3DCoordinateAxesQuadrics(self.quadric)
        glPopMatrix()
        
        glPushMatrix()
        glRotate(-90, 1, 0, 0)
        drawCheckerBoard(scale = [8, 8], 
                         check_colors = [[0.8, 0.8, 0.8], [0.2, 0.2, 0.2]])
        glPopMatrix()

        glPushMatrix()
        glRotatef(-80, 1, 0 , 0)
        glTranslatef(-1, 1, 0)
        glRotatef(45, 0, 0, 1)
        glScalef(0.5, 0.5, 0.5)
        drawTriangle([[0, 1, 1], [1, 0, 1], [1, 1, 0]]);
        glPopMatrix()
        
        glPushMatrix()
        glPushAttrib(GL_ALL_ATTRIB_BITS )
        glColor3f(.8, 0.2, 0.2)
        glTranslatef(0, .5, 0)
        gluSphere(self.quadric, 0.5, 32, 32)
        glTranslatef(0, .7, 0)
        gluSphere(self.quadric, 0.25, 32, 32)
        glPopAttrib()
        glPopMatrix()
        
        glPushMatrix()
        glPushAttrib(GL_ALL_ATTRIB_BITS )
        glColor3f(0.8, 0.1, 0.2)
        glTranslatef(1, 1, -1)
        gluSphere(self.quadric, 0.5, 32, 32)
        glPopAttrib()
        glPopMatrix()
        
def main():
    # intialize glut
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)

    # instantiate a scene
    sc = SampleScene();

    # specify a camera
    cam_spec1 = {'eye' : [0, 1, 5], 'center' : [0, 1, 0], 'up' : [0, 1, 0], 
                 'fovy': 40, 'aspect': 1.33, 'near' : 1., 'far' : 100.0}
    
    # setup the view using the camera specification and provide the model/scene to be rendered
    c1 = View(sc, cam_spec1)
    
    # create the glut window by providing the View object and some initialization parameters 
    GLUTWindow("Main Camera View", c1, window_size = (640, 480), window_pos = (320, 0), timer_time_ms = 1000./60.)

    # set params for the second window    
    cam_spec2 = {'eye' : [5, 5, 5], 'center' : [0, 1, 0], 'up' : [0, 1, 0], 
                 'fovy': 60, 'aspect': 1.0, 'near' : 0.01, 'far' : 200.0}
    c2 = View(c1, cam_spec2)
    GLUTWindow("External Camera View", c2, window_size = (640, 480), window_pos = (320, 510))
    
    glutMainLoop()
  
if __name__ == '__main__':
    main()