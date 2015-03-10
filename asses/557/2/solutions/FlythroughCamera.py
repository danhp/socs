# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 00:18:39 2015

@author: Fahim
"""
import time
from ModelViewWindow import View
import numpy as np
from GeomTransform import *

class FlythroughCamera(View):
    '''
    Extends the View class and add flythrough control. In this version the 
    eye position is used as the control point of the Hermite curve and the lookat
    vector is used as the tangent at the control point. (Perhaps for animation
    the right vector should be used as the tangent?)
    '''
    def __init__(self, child, camera_spec, path_model, num_steps = 101, MAX_FPS = 40):
        View.__init__(self, child, camera_spec)
        self.path_model = path_model
        self.num_steps = num_steps
        self.MAX_FPS = MAX_FPS
        self.init_flythrough()
        
    def timer_func(self, value):
        if self.bAnimate:
            curr_time = time.clock()
            elapsed_time = (curr_time - self.prev_time) * 1000.
            if(elapsed_time >= self.animation_timer_ms):
                self.animate_view()
                self.prev_time = curr_time
                
        if(hasattr(View, 'timer_func')):
            View.timer_func(self, value)
    
    def keyboard(self, key, x, y):
        ''' 
        Since FlythroughCamera is a child of GLUTWindow, this function will get
        called whenever there's a keyboard event.
        '''
        if key == 'p' or key == 'P':
            self.add_keyframe()
        elif key == 'g' or key == 'G':
            if self.NSeg < 1:
                self.bAnimate = False
            else:
                self.bAnimate = not self.bAnimate
            self.reset_position()
        elif key == 'c' or key == 'C':
            self.init_flythrough()
        # if View class happens to implement any keyboard functionality then
        # call it as well.
        if(hasattr(View, 'keyboard')):
            View.keyboard(key, x, y)    
    
    def init_flythrough(self):
        ''' clear everything and start from scratch '''
        self.path_model.set_data([])
        self.bAnimate = False
        self.NSeg = -1 # number of segments = number of points - 1
        self.keyframe = []
        self.camera_path = [] # store all points in the animation
        self.animation_timer_ms = 1000./self.MAX_FPS
        self.reset_position()
        
    def reset_position(self):
        ''' reset the camera position without clearing anything '''
        self.path_idx = 0 # current point in the animation path
        self.prev_time = time.clock()
        
    def restart_flythrough(self):
        self.reset_position()
        self.bAnimate = True
    
    def add_keyframe(self):
        cam_right = normalize(np.cross(self.lookat, self.up))
        # store the orientation of the camera
        self.keyframe.append((self.eye, self.lookat, self.up, cam_right))

        self.path_model.add_point((self.eye, self.lookat))
        self.NSeg += 1
        if self.NSeg >= 1: # if one or more segments
            param_t = np.linspace(0., 1., self.num_steps)
            #if self.NSeg > 1: # current semgent is 2nd or greater
            #    param_t = param_t[1:] # skip t = 0
            for t in param_t:
                self.camera_path.append(self.path_model.evaluate_curve_segment(self.NSeg - 1, t))
            
    def animate_view(self):
        if self.NSeg < 1 or self.path_idx > len(self.camera_path): 
            self.bAnimate = False
            return
        
        if np.mod(self.path_idx, self.num_steps) == 0:
            (pos, lookat, up, cam_right) = self.keyframe[int(self.path_idx / self.num_steps)]
        else:
            # we set the eye position and lookat based on the output of the
            # Hermite curve. For the camera frame we also need to ensure that
            # lookat and up vectors are consistent. Therefore we need to rotate
            # the camera frame based on the axis and angle determined from the
            # current lookat and the new lookat.
            (pos, tangent) = self.camera_path[self.path_idx]
            
            new_lookat = normalize(tangent)
            axis_of_rotation = np.cross(self.lookat, new_lookat)
            dot_prod = np.dot(self.lookat, new_lookat)
            # dot_prod value may not be between [-1, 1] due to floating-point
            # errors. This will cause np.arccos to throw a warning!
            if -1. <= dot_prod <= 1.:
                theta = np.arccos(dot_prod)
            else: # here it's either -1-eps or 1 + eps
                theta = 0. if dot_prod > 0. else np.pi
            
            if abs(theta) > 0 and abs(np.pi - theta) > 0:
                R = rotate(np.rad2deg(theta), axis_of_rotation)[:3,:3]
                #print(R)
                up = normalize(np.dot(R, self.up).getA1())
                lookat = new_lookat
            else:
                up = self.up
                lookat = self.lookat
#            rot_lookat = np.dot(R, normalize(self.lookat)).getA1()
#            np.testing.assert_array_almost_equal(rot_lookat, new_lookat)
#            np.testing.assert_almost_equal(np.dot(up, new_lookat), 0)
            
        self.eye = pos
        self.up = up
        self.lookat = lookat
        self.path_idx += 1
     
    def draw_camera_frame(self):
        View.draw_camera_frame(self)
        if self.NSeg > 0:
            self.path_model.draw_scene(False)
        
        