# -*- coding: utf-8 -*-
"""
Volume Rendering

Note: It's necessary to use GL_CLAMP_TO_BORDER for 3D texture parameter.
Because otherwise negative texture coordinates or coordinates greater than 1 can be generated.
"""
from __future__ import division
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from ModelViewWindow import *
import GeomTransform as GT
import load_tif_seq_data_UNC as LD
import matplotlib.pyplot as plt

def display_histogram(data, nbins = 64):
    ''' data can be any n-d array '''
    plt.ion()  # make the plot interactive i.e. show() at the end would be non-blocking
    plt.figure()
    hist_data, bin_edges = np.histogram(data, bins=nbins) # returns the histogram with the bin edges
    hist_data = 100. * hist_data / float(np.sum(hist_data)) # percentage contribution of each bin

    #print(hist_data, bin_edges)
    center = (bin_edges[:-1] + bin_edges[1:]) / 2.
    bin_width = (bin_edges[1] - bin_edges[0])
    #print(center)

    plt.bar(bin_edges[:-1], hist_data, width=bin_width)
    plt.plot(center, hist_data, 'ro')

    plt.xlim(min(bin_edges), max(bin_edges))
    plt.title('Histogram\n#bins : ' + str(nbins) + ' , bin width : ' + str(bin_width))
    plt.xlabel('Intensity', fontsize=20)
    plt.ylabel('% of pixels', fontsize=20)
    plt.savefig('histogram.png')    # the figure will be stored in the same folder this file is
    plt.show(False) # setting the argument to False should make the figure non-blocking

class VolumeRendering(Model):
    # Scene class only deals with models in the scene.

    # the number of slices in the volume
    NUMSLICES = 300

    def __init__(self):
        Model.__init__(self)
        ''' add any class related initialization here '''

        self.texID = None
        # 3D textures are loaded from file
        # self.intensity_stack saves the intensity map of the slices
        self.intensity_stack = LD.load_tif_seq_data_UNC('./cthead-8bit/')

        # self.im_seq saves a copy of the RGBA-converted images
        # np.tile will repeat the stack of 2D images along the 4th dimension.
        # Since intensity_stack is 3D (N-2D images), np.newaxis will add a 4th dimension
        # and (1, 1, 1, 4) means the first three dimensions are repeated once and the 4th dimension 4 times.
        self.im_seq = np.tile(self.intensity_stack[:,:,:,np.newaxis], (1, 1, 1, 4))
        self.im_seq[:,:,:,3] = 255 # set the alpha channel to completely opaque

        # initialize texels
        self.texels = self.im_seq

        # draw histogram of data
        display_histogram(self.intensity_stack[:,:,:])

        # Variable for keeping track of all the windows that uses this model
        # The default value is None which gets set in build_texture after texture loading
        self.window_texture_flag = dict()

    def init(self):
        # Add any OpenGL related initialization here before Model.init

        Model.init(self)
        # initialize the texture
        #request texture id from OpenGL
        self.texID = glGenTextures(1)

        # apply default transfer function
        self.transfer_func(3)

    def build_texture(self):
        WIDTH = self.texels[0].shape[1]
        HEIGHT = self.texels[0].shape[0]
        DEPTH = self.texels.shape[0]

        # tell OpenGL we're going to be setting up the texture id it gave us
        glBindTexture(GL_TEXTURE_3D, self.texID)
        # when this texture needs to be shrunk to fit on small polygons, use linear interpolation of the texels to determine the color
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # when this texture needs to be magnified to fit on a big polygon, use linear interpolation of the texels to determine the color
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # Note: It's necessary to use GL_CLAMP_TO_BORDER for 3D texture parameter. Because negative texture coordinates or coordinates greater than 1 can be generated.
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        # same as above for T axis
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        # same as above for R axis
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_BORDER)
        # this is a 3d texture, level 0 (max detail), GL should store it in RGBA8 format, its WIDTHxHEIGHTxDEPTH in size,
        # it doesnt have a border, we're giving it to GL in RGBA format as a series of unsigned bytes, and texels is where the texel data is.
        glTexImage3D(GL_TEXTURE_3D, 0, GL_RGBA8, WIDTH, HEIGHT, DEPTH, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.texels.ravel().astype(np.uint8))

        # at this point the texture is loaded so reset the flag for this window
        window_id = glutGetWindow()   # get the current glut window id
        self.window_texture_flag[window_id] = None # default no update required

    def transfer_func(self, flag):
        # refresh copy of the RGBA image to create texels using a transfer function
         self.texels = np.copy(self.im_seq)

         # iterate over frames in self.texels to set transfer function
         for frameNo in range(self.texels.shape[0]):
             # The following can be used when designing transfer functions to check the image intensities:
             # intensities = self.intensity_stack[frameNo,:,:]
             # intensities contains the intensity values of each pixel of image frameNo.
             # See transfer function for flag == 1 below for an example on how to set RGBA values
             # using conditionals. This code runs faster than when using for loops.

             if flag == 0:
                 # default transfer function sets (r,g,b,a) = (255,255,255,255)
                 self.texels[frameNo, :, :, :] = [255, 255, 255, 255]

             elif flag == 1:
                 # ====== SKIN ======
                 intensities = self.intensity_stack[frameNo,:,:]
                 self.texels[frameNo, (intensities>=75), :] = [255, 223, 196, 255]
                 self.texels[frameNo, (intensities<75), :] = [0, 0, 0, 0]
                 # ====== END SOLUTION ======

             elif flag == 2:
                 # ====== SKELETAL ======
                 intensities = self.intensity_stack[frameNo,:,:]
                 self.texels[frameNo, (intensities>=100), :] = [255, 215, 0, 255]
                 self.texels[frameNo, (intensities<100), :] = [0, 0, 0, 0]
                 # ====== END SOLUTION ======

             elif flag == 3:
                 # ====== TEETH =====
                 # Attempted to isolate the brain but never managed to get rid of the skin
                 intensities = self.intensity_stack[frameNo,:,:]
                 self.texels[frameNo, (intensities>=218), :] = [255, 255, 255, 255]
                 self.texels[frameNo, (intensities<218), :] = [0, 0, 0, 0]
                 # ====== END SOLUTION ======

         # reload texture
         self.build_texture()

    def draw_scene(self):
        glPushMatrix()
        glScalef(.25, .25, .25)
        draw3DCoordinateAxesQuadrics(self.pQuadric)
        glPopMatrix()

        # draw bounding box as a white cube
        glPushMatrix()
        glutWireCube(1.0)
        glPopMatrix()

        self.draw_volume()

    def draw_volume(self):
        # NOT IMPLEMENTED.
        # TODO: have the quads (slices) face the viewer
        glEnable(GL_BLEND)
        # glBlendFunc can be set during init but it's set here just to have all relevant things in one place
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_3D)

        # Draw all the NUMSLICES quads with corresponding texture coordinates.

        # the z-coordinate represents the depth of each slice in the bounding box
        for z in np.linspace(-0.5, 0.5, self.NUMSLICES):
            # the 1st row corresponds to the x-coordinates and 2nd row y-coordinates of the slices.
            quad_coord = np.array([[0, 1, 1, 0], [0, 0, 1, 1]]) - 0.5

            glBegin(GL_QUADS)
            for i in range(4):
                # You may need to modify the z-coordinate depending on your implementation
                glTexCoord3f(quad_coord[0][i] + .5, quad_coord[1][i] + .5 , z + .5)
                glVertex3f(quad_coord[0][i], quad_coord[1][i], z)
            glEnd()

        glDisable(GL_TEXTURE_3D)
        glDisable(GL_BLEND)

    def keyboard(self, key, x, y):
        ''' keyboard input for transfer functions '''
        flag = None
        if key == '0':
            flag = 0
        elif key == '1':
            flag = 1
        elif key == '2':
            flag = 2
        elif key == '3':
            flag = 3
        if flag is not None:
            for win_id in self.window_texture_flag: # set all the windows for update
                self.window_texture_flag[win_id] = flag
            self.transfer_func(flag) # update the current window

    def display(self):
        '''NOTE: Display list cannot be implemented because the transformations are
        done on the CPU at every frame and if the GL commands are compiled, proxy-geom (slices through volume)
        will not get updated.'''
        # check if build_texture needs to be called i.e. if the updated texture needs to be loaded
        window_id = glutGetWindow() # get the current glut window id
        if self.window_texture_flag[window_id] is not None: # if the current windows 3D texture needs update
            self.transfer_func(self.window_texture_flag[window_id])
        self.draw_scene()

def main():
    # intialize glut
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_ALPHA | GLUT_MULTISAMPLE)

    # instantiate a scene
    sc = VolumeRendering()

    # specify a camera
    cam_spec1 = {'eye' : [0, 0, 2], 'center' : [0, 0, 0], 'up' : [0, 1, 0],
            'fovy': 40, 'aspect': 1.33, 'near' : 1., 'far' : 4.0}

    # setup the view using the camera specification and provide the model/scene to be rendered
    c1 = View(sc, cam_spec1)

    # create the glut window by providing the View object and some initialization parameters
    GLUTWindow("Volume Rendering", c1, window_size = (640, 480), window_pos = (320, 0))

    # set params for the second window
    cam_spec2 = {'eye' : [3, 3, 3], 'center' : [0, 1, 0], 'up' : [0, 1, 0],
            'fovy': 60, 'aspect': 1.0, 'near' : 0.01, 'far' : 200.0}
    c2 = View(c1, cam_spec2)
    GLUTWindow("External Camera View", c2, window_size = (640, 480), window_pos = (320, 510))

    glutMainLoop()

if __name__ == '__main__':
    main()

