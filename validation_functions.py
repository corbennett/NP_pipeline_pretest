# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 12:37:51 2020

@author: svc_ccg
"""

import numpy as np
import logging
#import pandas as pd
from sync_dataset import Dataset
import sys
import json
import pickle
from abc import ABCMeta, abstractmethod
import os
#from run_validation_functions import main
logging.root.setLevel(logging.DEBUG)


def validation_decorator(validation_func):
    def wrapper(*args, **kwargs):
        try:
            out = validation_func(*args, **kwargs)
            assert(len(out)==3)
        except Exception as e:
            logging.debug(validation_func.__name__)
            logging.debug(e)
            template = "An exception of type {0} occurred. Arguments:{1!r}"
            message = template.format(type(e).__name__, e.args)
            out = None, False, message
        
        return out
    
    return wrapper


class Validator(object):
    """A Validator to vlidate a piece of neuropixels data

    Attributes:
        output name: a unique name based on the inputs to use as a key in the output json"""
    __metaclass__ = ABCMeta

    def __init__(self):
        """Return a new Validator object."""
        self.lims_key = None
        self.criterion_descriptor = None
        self.output_name = None

    @validation_decorator
    @abstractmethod
    def run_validation(self, Datastream):
        """"Run the validator function on the input datastream"""
        pass


class validate_file_size(Validator):
    """Check that file is large enough"""
    def __init__(self, datastream, min_file_size, tolerance=None):
        """Return a new Validator object."""
        self.lims_key = datastream.lims_key
        self.criterion_descriptor = 'file_size'
        self.output_name = self.criterion_descriptor + '_of_'+self.lims_key
        self.tolerance = tolerance
        self.min_file_size = min_file_size
        self.datastream = datastream

    @validation_decorator
    def run_validation(self):
        """"Run the validator function on the input datastream"""
        actual_file_size_gb = self.datastream.file_size/(10**9)
        validation_bool, message = generic_validator(actual_file_size_gb, self.min_file_size, self.criterion_descriptor, self.lims_key, self.tolerance, preposition='in')
        return actual_file_size_gb, validation_bool, message    


class validate_data_subtype(Validator):
    """Check the data subtype in a given datastream"""
    def __init__(self, datastream, data_label, criterion, criterion_descriptor=None, tolerance=None):
        """Return a new Validator object."""
        self.lims_key = datastream.lims_key
        self.criterion_descriptor = criterion_descriptor
        self.data_label = data_label
        if self.criterion_descriptor is None:
            self.criterion_descriptor = self.data_label + bool(not(tolerance))*' count' + bool(tolerance)*' framerate'
        self.output_name = self.data_label + 's_in_'+self.lims_key
        self.tolerance = tolerance
        self.criterion = criterion
        self.datastream = datastream

    @validation_decorator
    def run_validation(self):
        data_values = self.datastream.get_data_subtype(self.data_label)
        if self.tolerance is None:
            try:
                actual_value = len(data_values)
            except TypeError as E:
                actual_value = data_values
        else:
            actual_value = rate(data_values) 
        validation_bool, message = generic_validator(actual_value, self.criterion, self.criterion_descriptor, self.lims_key, self.tolerance)
        return actual_value, validation_bool, message 


def generic_validator(actual_value, criterion, criterion_descriptor, lims_key, tolerance=None, preposition='in'):
    if tolerance is None:
        validation_bool = above_minimum(actual_value, criterion)
        sucess_str = 'did not exceed'
        if validation_bool:
            sucess_str = 'exceeded'
        result_string = f'{criterion_descriptor} of {actual_value} {preposition} {lims_key} {sucess_str} goal criterion {criterion}'
    else:
        validation_bool = within_tolerance(actual_value, tolerance, criterion)
        sucess_str = 'was not'
        if validation_bool:
            sucess_str = 'was'
        result_string = f'{criterion_descriptor} of {actual_value} {preposition} {lims_key} {sucess_str} within {tolerance} of goal criterion {criterion}'
    return validation_bool, result_string    




def rate(timestamps):
    return 1/np.median(np.diff(timestamps))  

def above_minimum(value, criterion):
    validation_bool = value > criterion
    return validation_bool 


def within_tolerance(value, tolerance, criterion):
    validation_bool = (criterion-tolerance)<value<(criterion+tolerance)
    return validation_bool 




class Datastream(object):
    """A Datastream from a neuropixels session to be validated

    Attributes:
        lims_key: the loms key corresponding to the datastream
    """
    __metaclass__ = ABCMeta
    lims_key = None

    def __init__(self, file_path):
        """Return a new Datastream object."""
        self.data = self.load_datastream(file_path)
        self.file_size = os.path.getsize(file_path)

    @abstractmethod
    def load_datastream(self, file_path):
        """"Return the loaded data stream from the filepath """
        pass

    @abstractmethod
    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        pass



class synchronization_data(Datastream):
    """Neuropixels Sync file"""
    lims_key = 'synchronization_data'

    def load_datastream(self, file_path):
        """"Return the loaded data stream from the filepath """
        return  Dataset(file_path)

    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        rising, falling = self.get_sync_line_data(data_subtype_str)
        return falling


    def get_sync_line_data(self, line_label):
        ''' Get rising and falling edge times for a particular line from the sync h5 file
            
            Parameters
            ----------
            dataset: sync file dataset generated by sync.Dataset
            line_label: string specifying which line to read, if that line was labelled during acquisition
            channel: integer specifying which channel to read in line wasn't labelled
            
            Returns
            ----------
            rising: npy array with rising edge times for specified line
            falling: falling edge times
        '''
        syncDataset = self.data
        
        if line_label in syncDataset.line_labels:
            channel = syncDataset.line_labels.index(line_label)
        else:
            massage_str = 'Line label was not found in sync file: ' + line_label
            logging.warning(massage_str)
            raise(AssertionError(massage_str))
        
        sample_freq = syncDataset.meta_data['ni_daq']['counter_output_freq']
        rising = syncDataset.get_rising_edges(channel)/sample_freq
        falling = syncDataset.get_falling_edges(channel)/sample_freq
        
        return rising, falling



class Stimulus_pkl(Datastream):
    """Neuropixels behavior_stimulus file"""
    __metaclass__ = ABCMeta
    lims_key = None

    def load_datastream(self, file_path):
        """"Return the loaded data stream from the filepath """
        with open(file_path, 'rb') as f:
            pklData = pickle.load(f, encoding='bytes')#pd.read_pickle(file_path, enocoding='bytes')
        return pklData

    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        return getattr(self, data_subtype_str)()



class behavior_stimulus(Stimulus_pkl):
    """Neuropixels behavior_stimulus file"""
    lims_key = 'behavior_stimulus'

    def pkl_event(self, sensor_type_string, event_type_string):
        #pprint(self.data)
        return self.data[b'items'][b'behavior'][bytes(sensor_type_string, 'utf8')][0][bytes(event_type_string, 'utf8')]

    def lick_events(self):
        return self.pkl_event('lick_sensors', 'lick_events')

    def wheel_rotations(self):
        dx = self.pkl_event('encoders', 'dx')
        num_rotations = np.sum(dx)/360.
        return num_rotations



class Video(Datastream):
    """Neuropixels behavior_tracking file"""
    __metaclass__ = ABCMeta
    lims_key = None

    def load_datastream(self, file_path):
        """"Return the loaded data stream from the filepath """
        extension = os.path.splitext(file_path)[1]
        assert((extension == '.mp4') or (extension == '.avi')) 



class behavior_tracking(Video):
    """Neuropixels behavior_tracking file"""
    lims_key = 'behavior_tracking'


class eye_tracking(Video):
    """Neuropixels eye_tracking file"""
    lims_key = 'eye_tracking'



##################################################################


def get_sync_line_data(syncDataset, line_label):
    ''' Get rising and falling edge times for a particular line from the sync h5 file
        
        Parameters
        ----------
        dataset: sync file dataset generated by sync.Dataset
        line_label: string specifying which line to read, if that line was labelled during acquisition
        channel: integer specifying which channel to read in line wasn't labelled
        
        Returns
        ----------
        rising: npy array with rising edge times for specified line
        falling: falling edge times
    '''
    
    if line_label in syncDataset.line_labels:
        channel = syncDataset.line_labels.index(line_label)
    else:
        massage_str = 'Line label was not found in sync file: ' + line_label
        logging.warning(massage_str)
        raise(AssertionError(massage_str))
    
    sample_freq = syncDataset.meta_data['ni_daq']['counter_output_freq']
    rising = syncDataset.get_rising_edges(channel)/sample_freq
    falling = syncDataset.get_falling_edges(channel)/sample_freq
    
    return rising, falling

@validation_decorator
def validate_stim_vsyncs(syncDataset, tolerance, line_label, criterion, criterion_descriptor):
    ''' Validate that the sync box is getting 60 Hz signal from stim computer
        Confirms that vsync_rate is within tolerance of 60 Hz'''
    vsync_framerate = criterion
    vsyncs_rising, vsyncs_falling = get_sync_line_data(syncDataset, line_label)
    vsync_rate = 1/(np.median(np.diff(vsyncs_falling)))
    
    return vsync_rate, (vsync_framerate-tolerance)<vsync_rate<(vsync_framerate+tolerance)

@validation_decorator    
def validate_barcode_syncs(syncDataset, criterion, line_label, criterion_descriptor):
    ''' Validate that sync box is getting barcodes. Looks for at least min_barcode_num '''
    min_edges = criterion
    r, f = get_sync_line_data(syncDataset, line_label)
    logging.warning('num barcodes: ' + str(len(f)))
    return len(f), len(f)>=min_edges

@validation_decorator
def validate_cam_syncs(syncDataset, criterion, tolerance, line_label, criterion_descriptor):
    ''' Validate that camera is sending sync pulses within tolerance of designated framerate '''
    framerate = criterion
    r, f = get_sync_line_data(syncDataset, line_label)
    cam_rate = 1/np.median(np.diff(f))
    logging.warning('cam rate: ' + str(cam_rate))
    return cam_rate, (framerate-tolerance)<cam_rate<(framerate+tolerance)

@validation_decorator
def validate_pkl_licks(pklData, criterion, criterion_descriptor):
    ''' Validate that pickle file has registered at least min_licks '''    
    min_lick_num = criterion
    licks = pklData['items']['behavior']['lick_sensors'][0]['lick_events']
    logging.warning('num licks: ' + str(len(licks)))
    return len(licks), len(licks)>= min_lick_num

@validation_decorator
def validate_pkl_wheel_data(pklData, criterion, criterion_descriptor):
    ''' Validate that there's wheel data in the pkl file:
        Check to see that wheel spun more than min_wheel_rotations '''
    min_wheel_rotations = criterion
    dx = pklData['items']['behavior']['encoders'][0]['dx']
    num_rotations = np.sum(dx)/360.  # wheel rotations
    logging.warning('wheel rotations: ' + str(num_rotations))
    return num_rotations, num_rotations>=min_wheel_rotations

# The syntax here is picky - the function name needs to be get_+"lims_key"
def get_synchronization_data(file_path):
    syncDataset = Dataset(file_path)
    return syncDataset



def get_behavior_stimulus(file_path):
    print(file_path)
    with open(file_path, 'rb') as f:
        pklData = pickle.load(f, encoding='bytes')#pd.read_pickle(file_path, enocoding='bytes')
    return pklData

#for files that aren't really datastreams (should probably change nomenclature), mainly images that can't be loaded just check that the file extension is correct and return true



#if __name__ == "__main__":
#    main(sys.argv)   
    
    
    
    
