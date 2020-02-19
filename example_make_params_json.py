# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:59:16 2020

@author: svc_ccg
"""
import json

params = {  'file_paths': {
                    'SYNC_FILE_PATH': r"Z:\pretest\pretest200218124848.sync",
                    'PKL_FILE_PATH' : r"Z:\pretest\200218124916.pkl",
                    'BODY_CAM_VID_PATH' : r"Z:\pretest\Body_2020T124851.avi",
                    'EYE_CAM_VID_PATH' : r"Z:\pretest\Eye_2020T124851.avi",
                    'FACE_CAM_VID_PATH' : r"Z:\pretest\Face_2020T124851.avi"},
            'functions_to_run' : [
                    {'function': 'validate_stim_vsyncs',    'args': {'line_label': 'stim_vsync','tolerance': 1, 'vsync_framerate':60}},
                    {'function': 'validate_barcode_syncs',  'args': {'line_label': 'barcode', 'min_edges':10}},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'cam1_exposure', 'framerate': 60, 'tolerance': 2}},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'cam2_exposure', 'framerate': 60, 'tolerance': 2}},
                    {'function': 'validate_cam_syncs',      'args': {'line_label': 'Face_Exposure', 'framerate': 60, 'tolerance': 2}},
                    {'function': 'validate_pkl_licks',      'args': {'min_lick_num': 5}},
                    {'function': 'validate_pkl_wheel_data', 'args': {'min_wheel_rotations' : 2}}]
          }

ddir=r"Z:\pretest"
with open(os.path.join(ddir, 'params.json'), 'w') as out:
    json.dump(params, out, indent=2)
    
    

