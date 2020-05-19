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
                        'function': 'validate_data_subtype',
                        'args': {
                            'data_label': 'stim_vsync',
                            'tolerance': 1, 
                            'criterion':60
                        },
                        'data_streams': ['synchronization_data'],
                    },
                    {
                        'function': 'validate_data_subtype',  
                        'args': {
                            'data_label': 'barcodes',
                            'criterion': 5
                        }, 
                        'data_streams': ['synchronization_data'],
                    },
                    {
                        'function': 'validate_data_subtype',      
                        'args': {
                            'data_label': 'cam1_exposure', 
                            'criterion': 60, 
                            'tolerance': 2,
                            'criterion_descriptor': 'eye cam framerate'
                        }, 
                        'data_streams': ['synchronization_data'], 
                    },
                    {
                        'function': 'validate_data_subtype',      
                        'args': {
                            'data_label': 'cam2_exposure', 
                            'criterion': 60, 
                            'criterion_descriptor': 'body cam framerate',
                            'tolerance': 2
                        }, 
                        'data_streams': ['synchronization_data'], 
                    },
                    {
                        'function': 'validate_data_subtype',      
                        'args': {
                            'data_label': 'Face_Exposure', 
                            'criterion': 60, 
                            'tolerance': 2,
                        }, 
                        'data_streams': ['synchronization_data'], 
                    },
                    {
                        'function': 'validate_data_subtype',      
                        'args': {
                            'data_label': 'lick_events', 
                            'criterion': 5,
                        }, 
                        'data_streams': ['behavior_stimulus'], 
                    },
                    {
                        'function': 'validate_data_subtype',
                        'args': {
                            'data_label': 'wheel_rotations', 
                            'criterion' : 2,
                        }, 
                        'data_streams': ['behavior_stimulus'], 
                    },
                    {
                        'function': 'validate_file_size',
                        'args': {
                            'min_file_size' : 1,
                        }, 
                        'data_streams': ['behavior_tracking'], 
                    },
                    {
                        'function': 'validate_file_size',
                        'args': {
                            'min_file_size' : 1,
                        }, 
                        'data_streams': ['eye_tracking'], 
                    }
                ]
          }
 

ddir=r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130"
with open(os.path.join(ddir, 'pretest_params.json'), 'w') as out:
    json.dump(params, out, indent=2)
    
    

file_paths = {
                'file_paths': {
                    'synchronization_data': r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.sync",
                    'behavior_stimulus' : r"\\w10DTSM18306\neuropixels_data\1013811660_496639_20200312\1013811660_496639_20200312.behavior.pkl",
                    'behavior_tracking' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi",
                    'eye_tracking' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi",
                    'FACE_CAM_VID_PATH' : r"\\w10DTSM18306\neuropixels_data\815201437_425599_20190130\815201437_425599_20190130.behavior.avi"}
                }


with open(os.path.join(ddir, 'pretest_file_paths.json'), 'w') as out:
    json.dump(file_paths, out, indent=2)