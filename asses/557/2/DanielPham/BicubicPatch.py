# -*- coding: utf-8 -*-
"""
BicubicPatch.py
---------------
This file implements the BicubicPatch class. Code needs to be added in
evaluate(st_param): returns a list of point and tangent values for a given
                    parameter [s, t]

"""
from __future__ import division
import numpy as np
from ModelViewWindow import Model
from OpenGL.GL import *
from GLDrawHelper import *

class BicubicPatch(Model):
    '''
    Bicubic surface patch defined by 16 points. The 16 points on a 4x4 (s, t)
    grid is provided during instantiation.
    '''
    def __init__(self, data_points, num_samples_rendering = (90, 90)):
        '''
        data_points is in row major order, namely the 16 rows of the array
        correspond to (s,t) values (0,0), (0,1),(0,2), (0,3), (1, 0), (1,1),...
        and so on.
        num_samples_rendering refers to the number of samples that would be used
        by the draw_scene() function when rendering the patch
        '''
        Model.__init__(self)
        self.data_points = data_points
        self.num_samples_rendering = num_samples_rendering

        self.B = np.linalg.inv( [ [0, 1, 8, 27], [0, 1, 4, 9], [0, 1, 2, 3], [1, 1, 1, 1]])
        self.MatX = np.dot( np.transpose(self.B), np.dot( np.reshape(data_points[:,0], (4,4)), self.B ))
        self.MatY = np.dot( np.transpose(self.B), np.dot( np.reshape(data_points[:,1], (4,4)), self.B ))
        self.MatZ = np.dot( np.transpose(self.B), np.dot( np.reshape(data_points[:,2], (4,4)), self.B ))

    def evaluate(self, st_param):
        '''
        st_param = [s, t] where
        s in [0, 3] and t in [0, 3]
        For a given set of parameters return
        [x(s,t), y(s,t), z(s,t),
        dsx(s,t), dsy(s,t), dsz(s,t),
        dtx(s,t), dty(s,t), dtz(s,t)]
        '''
        s = st_param[0]
        t = st_param[1]
        assert(0. <= s <= 3. and 0. <= t <= 3.)
        x = y = z = dsx = dsy = dsz = dtx = dty = dtz = 0.
        #TODO --------- SOLUTION --------

        s_mat = [s*s*s, s*s, s, 1]
        sd_mat = [3*s*s, 2*s, 1, 0]

        t_mat = np.transpose([t*t*t, t*t, t, 1])
        td_mat = np.transpose([3*t*t, 2*t, 1, 0])

        x = np.dot(s_mat, np.dot(self.MatX, t_mat))
        y = np.dot(s_mat, np.dot(self.MatY, t_mat))
        z = np.dot(s_mat, np.dot(self.MatZ, t_mat))

        dsx = np.dot(sd_mat, np.dot(self.MatX, t_mat))
        dsy = np.dot(sd_mat, np.dot(self.MatY, t_mat))
        dsz = np.dot(sd_mat, np.dot(self.MatZ, t_mat))

        dtx = np.dot(s_mat, np.dot(self.MatX, td_mat))
        dty = np.dot(s_mat, np.dot(self.MatY, td_mat))
        dtz = np.dot(s_mat, np.dot(self.MatZ, td_mat))
        #-------------- SOLUTION --------
        return [x, y, z, dsx, dsy, dsz, dtx, dty, dtz]

    def get_samples(self, samples = (7, 7)):
        '''
        Returns an array of values. samples is a tuple that has to be at least (2, 2)
        '''
        assert(samples[0] >= 2 and samples[1] >= 2)
        X = np.zeros(samples)
        Y = np.zeros(samples)
        Z = np.zeros(samples)
        DsX = np.zeros(samples)
        DsY = np.zeros(samples)
        DsZ = np.zeros(samples)
        DtX = np.zeros(samples)
        DtY = np.zeros(samples)
        DtZ = np.zeros(samples)

        for i in range(samples[0]):
            for j in range(samples[1]):
                p = self.evaluate([3.*i/(samples[0] - 1.), 3.*j/(samples[1] - 1.)])
                X[i][j] = p[0]
                Y[i][j] = p[1]
                Z[i][j] = p[2]
                DsX[i][j] = p[3]
                DsY[i][j] = p[4]
                DsZ[i][j] = p[5]
                DtX[i][j] = p[6]
                DtY[i][j] = p[7]
                DtZ[i][j] = p[8]

        return (X, Y, Z, DsX, DsY, DsZ, DtX, DtY, DtZ)

    def set_color_from_XYZ(self, x, y, z):
        '''
        set_color_from_XYZ is the default color scheme for rendering
        bicubic patches. It takes  x, y, z values that are in [0, 1] and sets
        the color based on the normalized XYZ coordinate
        '''
        assert(0. <= x <= 1.)
        assert(0. <= y <= 1.)
        assert(0. <= z <= 1.)

        #TODO ------- BEGIN SOLUTION ----------

        glColor3f(0, y, 0)
        #---------- END SOLUTION --------------

    def draw_scene(self, bDrawCoordAxes = False):
        '''
        drawing meshes with normalized values is more generic because the caller
        can then approrpriately scale and translate the mesh.
        '''
        result = self.get_samples(self.num_samples_rendering)

        # The following draw3DCoordinateAxesQuadrics can be commented out
        if bDrawCoordAxes is True:
            glPushMatrix()
            glScalef(.25, .25, .25)
            draw3DCoordinateAxesQuadrics()
            glPopMatrix()

        #TODO ---------   BEGIN SOLUTION --------
        glPushMatrix()
        glScalef(.25, .25, .25)
        for i in range(self.num_samples_rendering[0] - 1):
            for j in range(self.num_samples_rendering[1] - 1):
                self.set_color_from_XYZ(abs((result[0][i][j])/3), abs((result[1][i][j])/3), abs((result[2][i][j])/3))
                glBegin(GL_TRIANGLES)
                glVertex3f(result[0][i][j], result[1][i][j], result[2][i][j])
                glVertex3f(result[0][i + 1][j], result[1][i + 1][j], result[2][i + 1][j])
                glVertex3f(result[0][i][j + 1], result[1][i][j + 1], result[2][i][j + 1])

                glVertex3f(result[0][i + 1][j], result[1][i + 1][j], result[2][i + 1][j])
                glVertex3f(result[0][i + 1][j + 1], result[1][i + 1][j + 1], result[2][i + 1][j + 1])
                glVertex3f(result[0][i][j + 1], result[1][i][j + 1], result[2][i][j + 1])
                glEnd()

        # Couldn't find the how to disable face culling so just repeat making them face the other way.........
        # For some reason I can't figure out why this has tranparency.
        for i in range(self.num_samples_rendering[0] - 1):
            for j in range(self.num_samples_rendering[1] - 1):
                self.set_color_from_XYZ(abs((result[0][i][j])/3), abs((result[1][i][j])/3), abs((result[2][i][j])/3))
                glBegin(GL_TRIANGLES)
                glVertex3f(result[0][i][j], result[1][i][j], result[2][i][j])
                glVertex3f(result[0][i][j + 1], result[1][i][j + 1], result[2][i][j + 1])
                glVertex3f(result[0][i + 1][j], result[1][i + 1][j], result[2][i + 1][j])

                glVertex3f(result[0][i + 1][j], result[1][i + 1][j], result[2][i + 1][j])
                glVertex3f(result[0][i][j + 1], result[1][i][j + 1], result[2][i][j + 1])
                glVertex3f(result[0][i + 1][j + 1], result[1][i + 1][j + 1], result[2][i + 1][j + 1])
                glEnd()

        glPopMatrix()
        #-------------- END SOLUTION -------------
        ''' return the result obtained from get_samples so it can be used for
        further processing by the caller if necessary'''
        return result

#### ----- Code for rendering a sample Bicubic Patch ------
def main():
    from OpenGL.GLUT import glutInit, glutInitDisplayMode,  \
                            glutMainLoop, GLUT_DOUBLE, GLUT_RGBA

    from ModelViewWindow import View, GLUTWindow

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)

    cam_spec = {'eye' : [2, 2, 2], 'center' : [0, 0, 0], 'up' : [0, 1, 0],
                 'fovy': 30, 'aspect': 1.0, 'near' : 0.01, 'far' : 200.0}
    data_points = np.zeros((16, 3))
    data_points[:,0] = np.transpose([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])
    data_points[:,1] = np.transpose([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3])
    data_points[:,2] = np.transpose([0, 2, 2, -3, 0, -2, 2, -3, 0, -2, 2, -3, 0, -2, 2, -3])

    BCPatch = BicubicPatch(data_points)
    cam = View(BCPatch, cam_spec)
    GLUTWindow('Bicubic Patch', cam, window_size = (512, 512), window_pos =(220, 0))

    glutMainLoop()

if __name__ == '__main__':
    main()
