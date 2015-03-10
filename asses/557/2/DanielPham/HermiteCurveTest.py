# -*- coding: utf-8 -*-
"""
Created on Sat Feb 07 15:14:01 2015

@author: Fahim
"""

import unittest
import numpy as np
import numpy.testing as nptest
from HermiteCurve import *

class HermiteCurveTest(unittest.TestCase):
    
    def test_add_point(self):
        curve = HermiteCurve()
        p0 = [1, 2, 3]
        m0 = [1, -1, 2]
        curve.add_point((p0, m0))
        ptl = curve.point_tangent_list
        self.assertEqual(len(ptl), 1)
        nptest.assert_array_equal(ptl[0][0], p0)
        nptest.assert_array_equal(ptl[0][1], m0)

    def test_add_point_2(self):
        curve = HermiteCurve()
        
        # add 1st point
        p0 = [1, 2, 3]
        m0 = [1, 1, 1]
        curve.add_point((p0, m0))
        ptl = curve.point_tangent_list
        self.assertEqual(len(ptl), 1)
        nptest.assert_array_equal(ptl[0][0], p0)
        nptest.assert_array_equal(ptl[0][1], m0)
        
        # add 2nd point
        p1 = [2, 3, 4]
        m1 = [-1, 2, -5]
        curve.add_point((p1, m1))
        ptl = curve.point_tangent_list
        self.assertEqual(len(ptl), 2)
        nptest.assert_array_equal(ptl[1][0], p1)
        nptest.assert_array_equal(ptl[1][1], m1)
        
    def test_curve_segment_endpoints(self):
        curve = HermiteCurve()
        
        # add 1st point
        p0 = [1, 2, 3]
        m0 = [1, 1, 1]
        curve.add_point((p0, m0))
        
        res0 = curve.evaluate_curve_segment(0, 0)
        self.assertEqual(res0, None, 'Test return type of evaluate for insufficient number of points.')
        
        # add 2nd point
        p1 = [2., 3., 4.]
        m1 = [-1, 2, -5]
        curve.add_point((p1, m1))
        
        res0 = curve.evaluate_curve_segment(0, 0)
        self.assertEqual(type(res0), tuple, 'Test return type of evaluate for first point.')
        nptest.assert_array_almost_equal(res0[0], p0, err_msg='Test t=0 point')
        nptest.assert_array_almost_equal(res0[1], m0, err_msg='Test t=0 tangent')
        
        res1 = curve.evaluate_curve_segment(0, 1)
        self.assertEqual(type(res1), tuple, '(redundant) Test return type of evaluate for second point.')
        nptest.assert_array_almost_equal(res1[0], p1, err_msg='Test t=1 point')
        nptest.assert_array_almost_equal(res1[1], m1, err_msg='Test t=1 tangent')
    
    def test_straight_curve_segment_basic(self):
        curve = HermiteCurve()
        
        # add 1st point
        p0 = [0, 0, 0]
        m0 = [1, 1, 1]
        curve.add_point((p0, m0))
        
        # add 2nd point
        p1 = [1, 1, 1]
        m1 = m0
        curve.add_point((p1, m1))
        
        for t in np.linspace(0, 1, 10):
            res = curve.evaluate_curve_segment(0, t)
            nptest.assert_array_almost_equal(res[0], [t, t, t], err_msg='Test var t=%f point' % (t))
            nptest.assert_array_almost_equal(res[1], m0, err_msg='Test var t tangent')
    
    def test_straight_curve_segment_basic2(self):
        curve = HermiteCurve()
        
        # add 1st point
        p0 = [-1, -1, -1]
        m0 = [1., 1., 1.]
        curve.add_point((p0, m0))
        
        # add 2nd point
        p1 = [0, 0, 0]
        m1 = m0
        curve.add_point((p1, m1))
        
        for t in np.linspace(0, 1, 10):
            res = curve.evaluate_curve_segment(0, t)
            nptest.assert_array_almost_equal(res[0], [t - 1, t - 1, t - 1], err_msg='Test var t=%f point' % (t))
            nptest.assert_array_almost_equal(res[1], m0, err_msg='Test var t=%f tangent' % (t))    
            
    def test_curve_segment_2D(self):
        curve = HermiteCurve()
        
        # add 1st point
        p0 = [1, 2, 0]
        m0 = [1., 1., 0]
        curve.add_point((p0, m0))
        
        # add 2nd point
        p1 = [3, 1, 0]
        m1 = [3, 2, 0]
        curve.add_point((p1, m1))
        
        res_expected = [[(1.000000, 2.000000, 0.000000), (1.000000, 1.000000, 0.000000)],
                        [(1.052500, 2.033125, 0.000000), (1.100000, 0.337500, 0.000000)],
                        [(1.110000, 2.035000, 0.000000), (1.200000, -0.250000, 0.000000)],
                        [(1.172500, 2.009375, 0.000000), (1.300000, -0.762500, 0.000000)],
                        [(1.240000, 1.960000, 0.000000), (1.400000, -1.200000, 0.000000)],
                        [(1.312500, 1.890625, 0.000000), (1.500000, -1.562500, 0.000000)],
                        [(1.390000, 1.805000, 0.000000), (1.600000, -1.850000, 0.000000)],
                        [(1.472500, 1.706875, 0.000000), (1.700000, -2.062500, 0.000000)],
                        [(1.560000, 1.600000, 0.000000), (1.800000, -2.200000, 0.000000)],
                        [(1.652500, 1.488125, 0.000000), (1.900000, -2.262500, 0.000000)],
                        [(1.750000, 1.375000, 0.000000), (2.000000, -2.250000, 0.000000)],
                        [(1.852500, 1.264375, 0.000000), (2.100000, -2.162500, 0.000000)],
                        [(1.960000, 1.160000, 0.000000), (2.200000, -2.000000, 0.000000)],
                        [(2.072500, 1.065625, 0.000000), (2.300000, -1.762500, 0.000000)],
                        [(2.190000, 0.985000, 0.000000), (2.400000, -1.450000, 0.000000)],
                        [(2.312500, 0.921875, 0.000000), (2.500000, -1.062500, 0.000000)],
                        [(2.440000, 0.880000, 0.000000), (2.600000, -0.600000, 0.000000)],
                        [(2.572500, 0.863125, 0.000000), (2.700000, -0.062500, 0.000000)],
                        [(2.710000, 0.875000, 0.000000), (2.800000, 0.550000, 0.000000)],
                        [(2.852500, 0.919375, 0.000000), (2.900000, 1.237500, 0.000000)],
                        [(3.000000, 1.000000, 0.000000), (3.000000, 2.000000, 0.000000)]]
        idx = 0
        for t in np.linspace(0, 1, 21):
            res = curve.evaluate_curve_segment(0, t)
            nptest.assert_array_almost_equal(res[0], res_expected[idx][0], err_msg='Test var t=%f point' % (t))
            nptest.assert_array_almost_equal(res[1], res_expected[idx][1], err_msg='Test var t=%f tangent' % (t))
            idx += 1

    def test_curve_segment_3D_basic(self):
        curve = HermiteCurve()
        
        # add 1st point
        p0 = [-1, -1, -1]
        m0 = [1, 1, 1]
        curve.add_point((p0, m0))
        
        # add 2nd point
        p1 = [1, 1, 1]
        m1 = m0
        curve.add_point((p1, m1))
        
        res_expected = [[(-1.000000, -1.000000, -1.000000), (1.000000, 1.000000, 1.000000)],
                        [(-0.942750, -0.942750, -0.942750), (1.285000, 1.285000, 1.285000)],
                        [(-0.872000, -0.872000, -0.872000), (1.540000, 1.540000, 1.540000)],
                        [(-0.789250, -0.789250, -0.789250), (1.765000, 1.765000, 1.765000)],
                        [(-0.696000, -0.696000, -0.696000), (1.960000, 1.960000, 1.960000)],
                        [(-0.593750, -0.593750, -0.593750), (2.125000, 2.125000, 2.125000)],
                        [(-0.484000, -0.484000, -0.484000), (2.260000, 2.260000, 2.260000)],
                        [(-0.368250, -0.368250, -0.368250), (2.365000, 2.365000, 2.365000)],
                        [(-0.248000, -0.248000, -0.248000), (2.440000, 2.440000, 2.440000)],
                        [(-0.124750, -0.124750, -0.124750), (2.485000, 2.485000, 2.485000)],
                        [(0.000000, 0.000000, 0.000000), (2.500000, 2.500000, 2.500000)],
                        [(0.124750, 0.124750, 0.124750), (2.485000, 2.485000, 2.485000)],
                        [(0.248000, 0.248000, 0.248000), (2.440000, 2.440000, 2.440000)],
                        [(0.368250, 0.368250, 0.368250), (2.365000, 2.365000, 2.365000)],
                        [(0.484000, 0.484000, 0.484000), (2.260000, 2.260000, 2.260000)],
                        [(0.593750, 0.593750, 0.593750), (2.125000, 2.125000, 2.125000)],
                        [(0.696000, 0.696000, 0.696000), (1.960000, 1.960000, 1.960000)],
                        [(0.789250, 0.789250, 0.789250), (1.765000, 1.765000, 1.765000)],
                        [(0.872000, 0.872000, 0.872000), (1.540000, 1.540000, 1.540000)],
                        [(0.942750, 0.942750, 0.942750), (1.285000, 1.285000, 1.285000)],
                        [(1.000000, 1.000000, 1.000000), (1.000000, 1.000000, 1.000000)]]
        idx = 0        
        for t in np.linspace(0, 1, 21):
            res = curve.evaluate_curve_segment(0, t)
            nptest.assert_array_almost_equal(res[0], res_expected[idx][0], err_msg='Test var t=%f point' % (t))
            nptest.assert_array_almost_equal(res[1], res_expected[idx][1], err_msg='Test var t=%f tangent' % (t))
            idx += 1
    
    def test_curve_segment_3D(self):
        curve = HermiteCurve()
        
        # add 1st point
        p0 = [1, 2, 3]
        m0 = [-1, 4, 0]
        curve.add_point((p0, m0))
        
        # add 2nd point
        p1 = [5, -3, -4]
        m1 = [1, -1, -1]
        curve.add_point((p1, m1))
        
        res_expected = [[(1.000000, 2.000000, 3.000000), (-1.000000, 4.000000, 0.000000)],
                        [(0.981500, 2.146625, 2.951625), (0.240000, 1.897500, -1.902500)],
                        [(1.022000, 2.193000, 2.813000), (1.360000, -0.010000, -3.610000)],
                        [(1.115500, 2.148875, 2.593875), (2.360000, -1.722500, -5.122500)],
                        [(1.256000, 2.024000, 2.304000), (3.240000, -3.240000, -6.440000)],
                        [(1.437500, 1.828125, 1.953125), (4.000000, -4.562500, -7.562500)],
                        [(1.654000, 1.571000, 1.551000), (4.640000, -5.690001, -8.490000)],
                        [(1.899500, 1.262375, 1.107375), (5.160000, -6.622500, -9.222500)],
                        [(2.168000, 0.912000, 0.632000), (5.560000, -7.360000, -9.760000)],
                        [(2.453500, 0.529625, 0.134625), (5.840000, -7.902500, -10.102501)],
                        [(2.750000, 0.125000, -0.375000), (6.000000, -8.250000, -10.250000)],
                        [(3.051500, -0.292125, -0.887125), (6.040000, -8.402500, -10.202500)],
                        [(3.352000, -0.712000, -1.392000), (5.960000, -8.360000, -9.960000)],
                        [(3.645500, -1.124875, -1.879875), (5.760000, -8.122500, -9.522500)],
                        [(3.925999, -1.521000, -2.341000), (5.440000, -7.690001, -8.889999)],
                        [(4.187500, -1.890625, -2.765625), (5.000000, -7.062500, -8.062500)],
                        [(4.424000, -2.224000, -3.144000), (4.440000, -6.240000, -7.040000)],
                        [(4.629500, -2.511375, -3.466375), (3.760000, -5.222500, -5.822500)],
                        [(4.798000, -2.743000, -3.723000), (2.960001, -4.010001, -4.410001)],
                        [(4.923500, -2.909125, -3.904125), (2.040000, -2.602500, -2.802500)],
                        [(5.000000, -3.000000, -4.000000), (1.000000, -1.000000, -1.000000)]]
        idx = 0        
        for t in np.linspace(0, 1, 21):
            res = curve.evaluate_curve_segment(0, t)
            nptest.assert_array_almost_equal(res[0], res_expected[idx][0], err_msg='Test var t=%f point' % (t))
            nptest.assert_array_almost_equal(res[1], res_expected[idx][1], err_msg='Test var t=%f tangent' % (t))
            idx += 1            

if __name__ == '__main__':
    unittest.main()