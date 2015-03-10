# -*- coding: utf-8 -*-
"""
HermiteCurve.py
---------------
This file implements the class HermiteCurve. This module is used by the
FlythroughCamera class which uses it for generating the flythrough curve.

Where to add code?
add_point(self, data_point): compute the coefficient matrix for the last curve
                             segment
evaluate_curve_segment(self, segNo, t): return a tuple of (point, tangent) for
    a given curve segment segNo and parameter t in [0, 1].

Once this module has been implemented run HermiteCurveTest.py for performing
some basic correctness tests. You can add more tests to that file (note this is
 NOT part of the assignment) for ensuring correctness of your implementation.
"""
import numpy as np
from numpy import transpose
from numpy.linalg import inv
from ModelViewWindow import Model

class HermiteCurve(Model):
    '''
    Implementation of Hermite curve. The class can be instantiated with a
    sequence of points representing curve segments. In addition to that new
    points can also be added by calling add_point() function with a data point.
    Whenever a Hermite curve segment needs to be evaluated for some parameter
    t in [0, 1], the function evaluate_curve_segment(segNo, t) is called with
    the curve segment number (0-based) and the parameter.

    Since the evaluate_curve_segment function will be called very often we need to build
    the coefficient matrix for each curve segment as they are created. Therefore
    the coefficient matrices are built in add_point and in the evaluate_curve_segment
    function it is used with the current parameter.

    This class is derived from the Model class defined in ModelViewWindow.py
    This allows Hermite curves to be rendered using Display List automatically.
    Display List allows OpenGL to evaluate all the draw instructions and store
    them in memory for later usage.
    The draw_scene() function does the actual rendering of the curve.
    '''
    def __init__(self, data_points = None, num_samples_rendering = 101):
        '''
        A set of data points can be optionally provided during instantiaion.
        The format is a list of tuples, where each tuple consists of a point
        and tangent at that point. Both point and tangents are represented by
        arrays.
        [(p0, m0), (p1, m1), (p2, m2)] where point p0 = [x0, y0, z0] and
        m0 = [mx0, my0, mz0] the tangent at p0, and so on.
        '''
        Model.__init__(self)
        self.num_samples_rendering = num_samples_rendering
        self.B_Hermite = inv([[0, 1, 0, 3], [0, 1, 0, 2], [0, 1, 1, 1], [1, 1, 0, 0]])

        self.coeff_matrix = [] # list of basis vector matrices for each segment
        self.point_tangent_list = []

        if data_points is not None:
            set_data(data_points)

    def set_data(self, point_tangent_list):
        self.point_tangent_list = []
        self.coeff_matrix = [] # list of basis vector matrices for each segment
        for data_point in point_tangent_list:
            self.add_point(data_point)

    def add_point(self, data_point):
        '''
        The basis vector for every curve segment is computed here and stored in
        coeff_matrix.
        '''
        self.point_tangent_list.append(data_point)
        if(len(self.point_tangent_list) >= 2):
            '''
            Compute the coefficient matrix for the last segment. Recall that
            the last element of a list can be retrieved using the index -1
            and the element before that -2. Note that self.B_Hermite is provided
            in the __init__ function.
            '''
            # TODO -------- SOLUTION --------
            p0 = self.point_tangent_list[-2][0]
            p1 = self.point_tangent_list[-1][0]
            pd0 = self.point_tangent_list[-2][1]
            pd1 = self.point_tangent_list[-1][1]

            g_mat = transpose([p0, p1, pd0, pd1])
            coeff = np.dot(g_mat, self.B_Hermite)
            self.coeff_matrix.append(coeff)
            # --------------------------------


    def evaluate_curve_segment(self, segNo, t):
        '''
        Returns a tuple of (point, tangent) where point and tangent are
        1D arrays for parameter t in [0, 1]
        '''
        if(len(self.coeff_matrix) < 1): # There has to be at least one segment
            return None

        '''Compute the point p and its tangent m for the given parameter t.'''
        #TODO --------- SOLUTION --------
        coeff_m = self.coeff_matrix[segNo]

        t_matrix = transpose([t*t*t, t*t, t, 1])
        td_matrix = transpose([3*t*t, 2*t, 1, 0])

        p = np.dot(coeff_m, t_matrix)
        m = np.dot(coeff_m, td_matrix)
        # -------------------------------
        return (p, m)

    def draw_scene(self, bDrawCoord = True):
        '''
        Draw the sequence of Hermite curve segments and tangents at the endpoints.
        '''
        NSeg = len(self.point_tangent_list) - 1

        if(NSeg < 1 or len(self.coeff_matrix) < 1): return

        if bDrawCoord is True:
            glPushMatrix()
            glScalef(.2, .2, .2)
            draw3DCoordinateAxesQuadrics()
            glPopMatrix()

        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glColor3f(.8, .8, .8)
        glBegin(GL_LINE_STRIP)

        for segNo in range(NSeg):
            for t in np.linspace(0, 1, self.num_samples_rendering):
                (pt, tangent) = self.evaluate_curve_segment(segNo, t)
                glVertex3f(pt[0], pt[1], pt[2])

        glEnd()
        glPopAttrib()

        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glColor3f(1.0, .2, .2)
        for segNo in range(NSeg):
            (pt, tangent) = self.evaluate_curve_segment(segNo, 0)
            glBegin(GL_LINES)
            glVertex3f(pt[0], pt[1], pt[2])
            n = tangent / np.linalg.norm(tangent)
            pt2 = pt + n * 0.5
            glVertex3f(pt2[0], pt2[1], pt2[2])
            glEnd()
        # render the tangent at the endpoint of the last curve segment
        (pt, tangent) = self.evaluate_curve_segment(NSeg - 1, 1)
        glBegin(GL_LINES)
        glVertex3f(pt[0], pt[1], pt[2])
        n = tangent / np.linalg.norm(tangent)
        pt2 = pt + n * 0.5
        glVertex3f(pt2[0], pt2[1], pt2[2])
        glEnd()
        glPopAttrib()


#### ----- The following is for rendering a basic curve for testing -----
from OpenGL.GL import *
from GLDrawHelper import *
from ModelViewWindow import View, GLUTWindow
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)

    hcurve = HermiteCurve()
    # ----- Add your own initialization here for visualization (NOTE: NOT graded for the assignment)
    # np.random.seed(1234)
    # for idx in range(10):
    #    data_point = ( ( np.random.rand(1, 3).flatten() - .5) * 1.2, np.random.rand(1, 3).flatten() - .5)
    #    hcurve.add_point(data_point)
    hcurve.add_point(([1, 0, 0], [0, 1, 0]))
    hcurve.add_point(([np.cos(np.pi/4), np.sin(np.pi/4), 0], [-np.cos(np.pi/4), np.sin(np.pi/4), 0]))
    hcurve.add_point(([0, 1, 0], [-1, 0, 0]))
    hcurve.add_point(([0, 0, 0], [-1, 0, 0]))
    hcurve.add_point(([0, 0, 1], [1, 0, 0]))
    hcurve.add_point(([0, 1, 1], [1, 1, 1]))
    # ------------
    cam_spec = {'eye' : [0, 0, 4], 'center' : [0, 0, 0], 'up' : [0, 1, 0],
                 'fovy': 30, 'aspect': 1.0, 'near' : 0.01, 'far' : 200.0}
    c1 = View(hcurve, cam_spec)

    GLUTWindow('Hermite Curve', c1, window_size = (512, 512))


    glutMainLoop()

if __name__ == '__main__':
    main()
