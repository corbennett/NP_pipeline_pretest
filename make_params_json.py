# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:59:16 2020

@author: svc_ccg
"""
import json
import os

params = {  
            'functions_to_run' : [
                    {'function': 'validate_stim_vsyncs',    'args': {'line_label': 'stim_vsync','tolerance': 1, 'vsync_framerate':60}, 'data_stream': 'sync', 'output_name' : 'vsyncs'},
                    {'function': 'validate_barcode_syncs',  'args': {'line_label': 'barcode', 'min_edges': 5}, 'data_stream': 'sync', 'output_name' : 'barcodes'},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'cam1_exposure', 'framerate': 60, 'tolerance': 2}, 'data_stream': 'sync', 'output_name' : 'cam1_syncs'},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'cam2_exposure', 'framerate': 60, 'tolerance': 2}, 'data_stream': 'sync', 'output_name' : 'cam2_syncs'},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'Face_Exposure', 'framerate': 60, 'tolerance': 2}, 'data_stream': 'sync', 'output_name' : 'facecam_syncs'},
                    {'function': 'validate_pkl_licks',      'args': {'min_lick_num': 5}, 'data_stream': 'pkl', 'output_name' : 'pkl_licks'},
                    {'function': 'validate_pkl_wheel_data', 'args': {'min_wheel_rotations' : 2}, 'data_stream': 'pkl', 'output_name' : 'wheel'}]
          }

ddir=r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130"
with open(os.path.join(ddir, 'params.json'), 'w') as out:
    json.dump(params, out, indent=2)
    
    

file_paths = {
                'file_paths': {
                    'SYNC_FILE_PATH': r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.sync",
                    'PKL_FILE_PATH' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.stim.pkl",
                    'BODY_CAM_VID_PATH' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi",
                    'EYE_CAM_VID_PATH' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi",
                    'FACE_CAM_VID_PATH' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi"}
                }


with open(os.path.join(ddir, 'file_paths.json'), 'w') as out:
    json.dump(file_paths, out, indent=2)