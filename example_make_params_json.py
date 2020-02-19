# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:59:16 2020

@author: svc_ccg
"""
import json
import os

params = {  'file_paths': {
                    'SYNC_FILE_PATH': r"Z:\pretest\pretest200218124848.sync",
                    'PKL_FILE_PATH' : r"Z:\pretest\200218124916.pkl",
                    'BODY_CAM_VID_PATH' : r"Z:\pretest\Body_2020T124851.avi",
                    'EYE_CAM_VID_PATH' : r"Z:\pretest\Eye_2020T124851.avi",
                    'FACE_CAM_VID_PATH' : r"Z:\pretest\Face_2020T124851.avi"},
            'functions_to_run' : [
                    {'function': 'validate_stim_vsyncs',    'args': {'line_label': 'stim_vsync','tolerance': 1, 'vsync_framerate':60}, 'data_stream': 'sync', 'output_name' : 'vsyncs'},
                    {'function': 'validate_barcode_syncs',  'args': {'line_label': 'barcode', 'min_edges':10}, 'data_stream': 'sync', 'output_name' : 'barcodes'},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'cam1_exposure', 'framerate': 60, 'tolerance': 2}, 'data_stream': 'sync', 'output_name' : 'cam1_syncs'},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'cam2_exposure', 'framerate': 60, 'tolerance': 2}, 'data_stream': 'sync', 'output_name' : 'cam2_syncs'},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'Face_Exposure', 'framerate': 60, 'tolerance': 2}, 'data_stream': 'sync', 'output_name' : 'facecam_syncs'},
                    {'function': 'validate_pkl_licks',      'args': {'min_lick_num': 5}, 'data_stream': 'pkl', 'output_name' : 'pkl_licks'},
                    {'function': 'validate_pkl_wheel_data', 'args': {'min_wheel_rotations' : 2}, 'data_stream': 'pkl', 'output_name' : 'wheel'}]
          }

ddir=r"Z:\pretest"
with open(os.path.join(ddir, 'params.json'), 'w') as out:
    json.dump(params, out, indent=2)
    
    

