# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 12:37:51 2020

@author: svc_ccg
"""

import logging
import sys
import json
from run_validation_functions import main
logging.root.setLevel(logging.DEBUG)


def validation_decorator(validation_func):
    def wrapper(*args, **kwargs):
        try:
            out = validation_func(*args, **kwargs)

        except Exception as e:
            logging.debug(validation_func.__name__)
            logging.debug(e)
            out = None, False
        
        return out
    
    return wrapper


@validation_decorator
def validate_stim_vsyncs(syncDataset, tolerance, line_label, criterion):
    ''' Validate that the sync box is getting 60 Hz signal from stim computer
        Confirms that vsync_rate is within tolerance of 60 Hz'''
    
    vsyncs_rising, vsyncs_falling = get_sync_line_data(syncDataset, line_label)
    vsync_rate = 1/(np.median(np.diff(vsyncs_falling)))
    
    return vsync_rate, (vsync_framerate-tolerance)<vsync_rate<(vsync_framerate+tolerance)

@validation_decorator    
def validate_barcode_syncs(syncDataset, criterion, line_label):
    ''' Validate that sync box is getting barcodes. Looks for at least min_barcode_num '''
    
    r, f = get_sync_line_data(syncDataset, line_label)
    logging.warning('num barcodes: ' + str(len(f)))
    return len(f), len(f)>=min_edges

@validation_decorator
def validate_cam_syncs(syncDataset, criterion, tolerance, line_label):
    ''' Validate that camera is sending sync pulses within tolerance of designated framerate '''
    
    r, f = get_sync_line_data(syncDataset, line_label)
    cam_rate = 1/np.median(np.diff(f))
    logging.warning('cam rate: ' + str(cam_rate))
    return cam_rate, (framerate-tolerance)<cam_rate<(framerate+tolerance)

@validation_decorator
def validate_pkl_licks(pklData, criterion):
    ''' Validate that pickle file has registered at least min_licks '''    
    
    licks = pklData['items']['behavior']['lick_sensors'][0]['lick_events']
    logging.warning('num licks: ' + str(len(licks)))
    return len(licks), len(licks)>= min_lick_num

@validation_decorator
def validate_pkl_wheel_data(pklData, criterion):
    ''' Validate that there's wheel data in the pkl file:
        Check to see that wheel spun more than min_wheel_rotations '''
    
    dx = pklData['items']['behavior']['encoders'][0]['dx']
    num_rotations = np.sum(dx)/360.  # wheel rotations
    logging.warning('wheel rotations: ' + str(num_rotations))
    return num_rotations, num_rotations>=min_wheel_rotations




# The syntax here is picky - the function name needs to be get_+"lims_key"
def get_synchronization_data(file_path)
    syncDataset = Dataset(file_path)
    return syncDataset



def get_datastream_dict(file_paths):
    pklData = pd.read_pickle(file_paths['file_paths']["behavior_stimulus"])
    return pklData

#for files that aren't really datastreams (should probably change nomenclature), mainly images that can't be loaded just check that the file extension is correct and return true



if __name__ == "__main__":
    main(sys.argv)   
    
    
    
