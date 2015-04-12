# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 12:52:46 2015

@author: Fahim
"""
import os
import fnmatch
from PIL import Image
import numpy as np

def load_tif_seq_data_UNC(dataset_dir):
    # load tiff data sequences found in http://graphics.stanford.edu/data/voldata/
    # usage: self.im_seq = load_tif_seq_data_UNC('./cthead-8bit/')
    in_map = []
    filterStr = '*.tif'
    for root, subDirs, files in os.walk(dataset_dir):
        slice_files = fnmatch.filter(os.listdir(root), filterStr)
        for slice_file in slice_files:
            slice_file_path = os.path.join(root, slice_file)
            im_frame = Image.open(slice_file_path)
            im_frame_arr = np.array(im_frame.resize((128, 128))) # resize to 128x128
            in_map.append(im_frame_arr)
    # the scans are from top to bottom...so flip and rotate to make the slices face the viewer
    # return intensity map
    return np.rot90(np.flipud(np.array(in_map)))