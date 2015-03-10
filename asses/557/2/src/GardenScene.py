# -*- coding: utf-8 -*-
"""
Garden Scene
"""
from OpenGL.GL import *
import numpy as np
from GLDrawHelper import *

from ModelViewWindow import Model
from LSystem import LSystem
from BicubicPatch import BicubicPatch
from FlythroughCamera import FlythroughCamera
from HermiteCurve import HermiteCurve

class GardenScene(Model):
    '''
    Scene with multiple 3D L-System and a checkerboard as ground-plane
    subscene_list is a list of dictionaries that contains the (x, y) position
    on the ground plane and the L-system.
    '''
    def __init__(self, terrain_model, subscene_list = []):
        Model.__init__(self)
        self.terrain_model = terrain_model
        self.subscene_list = subscene_list

    def init(self):
        Model.init(self)
        if(hasattr(self.terrain_model, 'init')):
            self.terrain_model.init()
        for scene in self.subscene_list:
            if(hasattr(scene, 'init')):
                scene.init()

    def add_subscene(self, subscene):
        self.subscene_list.append(subscene)

    def draw_scene(self):
        '''
        Draw the garden scene here. A sample solution is provided. You can
        build on top of it or replace it with your own approach.
        '''
        #TODO ----------- BEGIN SOLUTION ---------------

        # draw 3D coordinate axes
        glPushMatrix()
        glScalef(.25, .25, .25)
        draw3DCoordinateAxesQuadrics(self.pQuadric)
        glPopMatrix()

        # Replace the following checkerboard ground with your terrain and draw
        # a tiled pathway
        glPushMatrix()
        glRotate(-90, 1, 0, 0)
        drawCheckerBoard(scale = [8, 8], check_colors = [[0.8, 0.8, 0.8], [0.2, 0.2, 0.2]])
        glPopMatrix()

        ''' An example of how the Bicubic patch can be drawn and then the resulting
        points and tangents being retrieved '''
        glPushMatrix()
        # The argument 'False' is because we don't want to draw the coordinate axes
        (X, Y, Z, DsX, DsY, DsZ, DtX, DtY, DtZ) = self.terrain_model.draw_scene(False)
        glPopMatrix()

        for scene in self.subscene_list:
            glPushMatrix()
            pos = scene['pos']
            glTranslate(pos[0], pos[1], pos[2])
            scene['model'].draw_scene()
            glPopMatrix()
        #------------- END SOLUTION ----------------


def main():
    from OpenGL.GLUT import glutInit, glutInitDisplayMode, GLUT_DOUBLE, GLUT_RGBA
    from ModelViewWindow import GLUTWindow, View

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    #TODO -------- COPY CODE FROM LSystem.py ----------
    ''' Replace the following L-system speicfication with the one you did
    in LSystem.py '''
    # L-system specification
    TorchPlant = {'init' : 'X',
               'rule' : 'X->F-[[X]+X]+F[+FXL]-XL;F->FF',
               'depth': 5, 'angle': 25, 'growth_factor': .5,
               'init_angle_axis':{'angle':90, 'axis': [0, 0, 1]},
              }
    '''
    ModelList is a convenient way to add all the models with their position
    in a python list of dictionaries which can be used by the GardenScene class.
    NOTE that using this is optional. If you want you can add all the transformation
    code in GardenScene.draw_scene()
    '''
    ModelList = [{'pos':[0, 0, 0], 'model': LSystem(TorchPlant)},
                ]
    #--------------------------------------------------

    #TODO ---------------- BEGIN SOLUTION -----------------

    '''
    Represent the terrain using a Bicubic patch. Replace the
    control points below with the control points for your terrain.
    '''
    control_points = np.zeros((16, 3))
    control_points[:,0] = np.transpose([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])
    control_points[:,1] = np.transpose([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3])
    control_points[:,2] = np.transpose([0, 2, 2, 3, 0, 2, 2, 3, 0, 2, 2, 3, 0, 2, 2, 3])
    BCPatch = BicubicPatch(control_points)
    # ------------ END SOLUTION ------------------------
    # main camera
    cam_spec = {'eye' : [0, 4.5, 4], 'center' : [0, 2, 0], 'up' : [0, 1, 0],
                 'fovy': 40, 'aspect': 1.0, 'near' : 0.1, 'far' : 100.0}

    cam = FlythroughCamera(GardenScene(BCPatch, ModelList),
                           cam_spec, HermiteCurve())
    GLUTWindow('Garden Scene', cam, window_size = (640 * 1.2, 480), window_pos = (320, 0))

    # external camera
    cam_spec2 = {'eye' : [5, 5, 5], 'center' : [0, 1, 0], 'up' : [0, 1, 0],
                 'fovy': 60, 'aspect': 1.0, 'near' : 0.1, 'far' : 200.0}
    external_cam = View(cam, cam_spec2)
    GLUTWindow("External Camera View", external_cam, window_size = (640 * 1.2, 480), window_pos = (320, 520))

    glutMainLoop()

if __name__ == '__main__':
    main()
