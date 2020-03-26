# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:59:16 2020

@author: svc_ccg
"""
import json
import os

params = {  
            'functions_to_run' : [
                    {
                        'function': 'validate_stim_vsyncs',
                        'args': {
                            'line_label': 'stim_vsync',
                            'tolerance': 1, 
                            'criterion':60
                        },
                        'data_stream': 'sync',
                        'output_name' : 'vsyncs',
                        'criterion_descriptor': 'stimulus framerate'
                    },
                    {
                        'function': 'validate_barcode_syncs',  
                        'args': {
                            'line_label': 'barcode',
                            'criterion': 5
                        }, 
                        'data_stream': 'sync',
                        'output_name' : 'barcodes',
                        'criterion_descriptor': 'minumum open ephys barcode edges'
                    },
                    {
                        'function': 'validate_cam_syncs',      
                        'args': {
                            'line_label': 'cam1_exposure', 
                            'framerate': 60, 
                            'criterion': 2
                        }, 
                        'data_stream': 'sync', 
                        'output_name' : 'cam1_syncs',
                        'criterion_descriptor': 'eye cam framerate'
                    },
                    {
                        'function': 'validate_cam_syncs',      
                        'args': {
                            'line_label': 'cam2_exposure', 
                            'criterion': 60, 
                            'tolerance': 2
                        }, 
                        'data_stream': 'sync', 
                        'output_name' : 'cam2_syncs',
                        'criterion_descriptor': 'body cam framerate'
                    },
                    {
                        'function': 'validate_cam_syncs',      
                        'args': {
                            'line_label': 'Face_Exposure', 
                            'criterion': 60, 
                            'tolerance': 2
                        }, 
                        'data_stream': 'sync', 
                        'output_name' : 'facecam_syncs',
                        'criterion_descriptor': 'face cam framerate'
                    },
                    {
                        'function': 'validate_pkl_licks',      
                        'args': {
                            'criterion': 5
                        }, 
                        'data_stream': 'pkl', 
                        'output_name': 'pkl_licks',
                        'criterion_descriptor': 'minimum lick number'
                    },
                    {
                        'function': 'validate_pkl_wheel_data',
                        'args': {
                            'criterion' : 2
                        }, 
                        'data_stream': 'pkl', 
                        'output_name' : 'wheel',
                        'criterion_descriptor': 'minimum wheel rotations'
                    }]
          }

ddir=r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130"
with open(os.path.join(ddir, 'pretest_params.json'), 'w') as out:
    json.dump(params, out, indent=2)
    
    

file_paths = {
                'file_paths': {
                    'synchronization_data': r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.sync",
                    'behavior_stimulus' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.stim.pkl",
                    'BODY_CAM_VID_PATH' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi",
                    'EYE_CAM_VID_PATH' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi",
                    'FACE_CAM_VID_PATH' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi"}
                }


with open(os.path.join(ddir, 'pretest_file_paths.json'), 'w') as out:
    json.dump(file_paths, out, indent=2)