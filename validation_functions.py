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
import pandas as pd
from data_files_config import sorted_data_filenames
from experiment_files import make_sorted_probe_filepaths_json
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

    def __init__(self, *args, datastreams, datastream_list, **kwargs):
        """Return a new Validator object."""
        #self.filepath
        try:
            self.lims_key = datastreams.lims_key
        except Exception as E:
            self.lims_key = datastreams[0].lims_key
        self.output_name = f'{self.lims_key}_{self.__class__.__name__}'
        self.datastream =datastreams
        self.override_matching_failures = False
        if 'override_matching_failures' in kwargs:
            self.override_matching_failures = kwargs['override_matching_failures']
        self.interactive = False
        if 'interacvie' in kwargs:
            self.attempt_to_ammend_failures = kwargs['interactive']
        self.attempt_to_ammend_missing = False
        if 'attempt_to_ammend_missing' in kwargs:
            self.attempt_to_ammend_missing = kwargs['attempt_to_ammend_missing']




    @validation_decorator
    @abstractmethod
    def run_validation(self, Datastream):
        """"Run the validator function on the input datastream"""
        pass


class validate_file_size(Validator):
    """Check that file is large enough"""
    def __init__(self, *args, min_file_size, tolerance=None, **kwargs):
        """Return a new Validator object."""
        self.criterion_descriptor = 'file_size'
        self.tolerance = tolerance
        self.min_file_size = min_file_size
        super().__init__(*args, **kwargs)
        self.output_name = self.criterion_descriptor + '_of_'+self.lims_key


    @validation_decorator
    def run_validation(self):
        """"Run the validator function on the input datastream"""
        actual_file_size_gb = self.datastream.file_size/(10**9)
        validation_bool, message = generic_validator(actual_file_size_gb, self.min_file_size, self.criterion_descriptor, self.lims_key, self.tolerance, preposition='in')
        return actual_file_size_gb, validation_bool, message


class validate_data_subtype(Validator):
    """Check the data subtype in a given datastream"""
    def __init__(self, *args, data_label, criterion=None, criterion_descriptor=None, tolerance=None, **kwargs):
        """Return a new Validator object."""
        super().__init__(*args, **kwargs)
        self.criterion_descriptor = criterion_descriptor
        self.data_label = data_label
        if self.criterion_descriptor is None:
            self.criterion_descriptor = self.data_label + bool(not(tolerance))*' count' + bool(tolerance)*' framerate'
        no_underscores = self.lims_key.replace('.', '_')
        self.output_name = self.data_label + 's_in '+no_underscores
        self.tolerance = tolerance
        self.criterion = criterion

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


class validate_data_subtype_values(Validator):
    """Check the data subtype in a given datastream"""
    def __init__(self, *args, data_label, valid_values, **kwargs): #I think this trick makes data_label and valid_values
        """Return a new Validator object."""
        super().__init__(*args, **kwargs)
        self.data_label = data_label
        self.valid_values = valid_values
        self.output_name = self.data_label + '_valid values'


    @validation_decorator
    def run_validation(self):
        data_values = self.datastream.get_data_subtype(self.data_label)
        invalid_set = set()
        actual_value = True
        validation_bool = True
        for value in data_values:
            if not(value in self.valid_values):
                invalid_set.add(value)
                actual_value = False
                validation_bool = False
        if invalid_set:
            message = f'Found invalid values in {self.lims_key} subtype {self.data_label}: {", ".join(invalid_set)}'
        else:
            message = f'All values were valid in {self.lims_key} subtype {self.data_label}'
        return actual_value, validation_bool, message

#we are also gonna need to pass in the whole experiment to the validators -
class validate_no_extra_files(Validator):
    def __init__(self, datastream, **kwargs):
        #what info does this need? directory location and import files_list from data_file config
        self.datastream = datastream
        self.lims_key = datastream.lims_key
        self.output_name = f'{datastream.lims_key}_clear of extra files'

    @validation_decorator
    def run_validation(self):
        extra_files_list = []
        actual_value = True
        validation_bool = True
        for root, dirs, files in os.walk(self.datastream.file_path):
            if not(files in data_filenames) or not(data_filenames[files].upload):
                actual_value = False
                validation_bool = False
                extra_files_list.append(files)
        if extra_files_list:
            message = f'Found extra files in {datastream.file_path}: {", ".join(extra_files_list)}'
        else:
            message = f'No extra files were found in {datastream.file_path}'
        return actual_value, validation_bool, message


class validate_lims_match(Validator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_name = f'{self.lims_key}_matching when comparing lims and local versions'

    @validation_decorator
    def run_validation(self):
        #retrieve associated file from lims - just use paths for now?
        #lims_datastream = get_file_from_lims(self.lims_key) #- how do we deal with probe files different - they need a probe identifier to find correct file
        #how can we preserve probe information iwthout being verbose
        return False, False, 'Not yet implemented'


class validate_platform_json_fields(Validator):
    def __init__(self, datastreams, *args, **kwargs):
        datastream = datastreams['platform_json']
        self.platform_json = datastream
        self.files_json = datastreams['file_paths_json']
        super().__init__(datastream, data_object, *args, **kwargs)
        self.output_name = f'{self.lims_key} files_complete'

    @validation_decorator
    def run_validation(self):
        def check_for_missing_files():
            platform_files = self.platform_json.get_data_subtype('files')
            experiment_files = self.files_json.get_data_subtype('file_paths')
            missing_dict = {}
            for lims_key, file_path in experiment_files.items():
                if os.path.exixts(file_path) and (file in platform_files):
                    name = os.path.split(file_path)[1]
                    if os.path.isdir(file_path):
                        filename = {'directory_name': name}
                    else:
                        filename = {'filename': name}
                    missing_dict[lims_key] = filename
            return missing_dict
        missing_dict = check_for_missing_files()
        if missing_dict and self.attempt_to_ammend_failures:
            platform_files.update(missing_dict)
            set_data_subtype('files', platform_files)
            missing_dict = check_for_missing_files()
        if missing_dict:
            message = f'Some files are missing from the {self.lims_key}: {", ".join(missing_dict)}'
        else:
            message = f'All files were found in the {self.lims_key}'
        return bool(missing_dict), bool(missing_dict), message



class sorted_probe_lims_ready(Validator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_name = f'{self.lims_key}_ready for lims upload'

    @validation_decorator
    def run_validation(self):
        probe = self.lims_key[-1]
        prefix = probe+'_'
        save_location = os.path.split(self.file_path)[0]
        ddir = self.file_path
        file_paths_path = make_sorted_probe_filepaths_json(ddir, probe, save_location=save_location, prefix=prefix)
        params = 'sorted_probe_lims_ready.json'
        output_path = os.path.join(ddir, prefix+self.__class__.__name__+'_output.json')
        comand_string = ['python', 'run_validation_functions.py', params, file_paths_path, output_path]
        subprocess.check_call(comand_string)
        failed_list = check_all_validation_json(validation_json_path)
        actual_value = not(bool(failed_list))
        validation_bool = bool(actual_value)
        if validation_bool:
            message = f'All params passed for {self.file_path}'
        else:
            message = f'Some params failed for {self.file_path}: {", ".join(failed_list)}'
        return actual_value, validation_bool, message

class experiment_lims_verify(Validator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_name = f'{self.lims_key} upload_found in lims'

    @validation_decorator
    def run_validation(self):
        #here we need to check if the session has been uploaded to lims
        return False



def check_all_validation_json(validation_json_path):
        with open(validation_json_path, 'r') as f:
            validation_output = json.load(f)
        failed_list = check_all_ouput(validation_output)
        return failed_list

def check_all_validation_output(validation_output):
    all_sucess = True
    failed_list = []
    for validation_result, ouput in validation_output:
        if not(ouput['sucess']):
            all_sucess = False
            failed_list.append(validation_result)
    return failed_list


def check_subtype_output(validation_output, subtype_strings:set):
    subtype_dict = {}
    for validation_result, ouput in validation_output:
        if all([(s in validation_result) for s in subtype_strings]):
            subtype_dict[validation_result] = ouput
    return check_all_ouput(subtype_dict)


#I think it would be better to split these up - validate_data_subtype_presence, validate_data_subtype_rate, validate_data_subtype_minimum...
#but they can each inherit largely everything from the parent
def generic_validator(actual_value, criterion, criterion_descriptor, lims_key, tolerance=None, preposition='in'):
    if criterion is None:
        validation_bool = bool(actual_value)
        result_string = f'{criterion_descriptor} of {actual_value} {preposition} {lims_key} {sucess_str} goal criterion {criterion}'
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

    def __init__(self, *args, file_path, lims_key, **kwargs):
        """Return a new Datastream object."""
        self.file_size = os.path.getsize(file_path)
        self.file_path = file_path
        self.kwargs_in = kwargs
        self.lims_key = lims_key
        self.data = self.load_datastream()
 

    @abstractmethod
    def load_datastream(self):
        """"Return the loaded data stream from the filepath """
        pass

    @abstractmethod
    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        pass

class session(Datastream):
    
    def load_datastream(self):
        assert('_'.split(self.datastream) ==3)
        self.session_id, self.mouse_number, self.date = ('_').split(self.datastream)

class synchronization_data(Datastream):
    """Neuropixels Sync file"""
    #lims_key = 'synchronization_data'

    def load_datastream(self):
        """"Return the loaded data stream from the filepath """
        return  Dataset(self.file_path)

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
    #lims_key = None

    def load_datastream(self):
        """"Return the loaded data stream from the filepath """
        with open(self.file_path, 'rb') as f:
            pklData = pickle.load(f, encoding='bytes')#pd.read_pickle(file_path, enocoding='bytes')
        return pklData

    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        return getattr(self, data_subtype_str)()



class behavior_stimulus(Stimulus_pkl):
    """Neuropixels behavior_stimulus file"""
    #lims_key = 'behavior_stimulus'

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
    #lims_key = None

    def load_datastream(self):
        """"Return the loaded data stream from the filepath """
        extension = os.path.splitext(file_path)[1]
        assert((extension == '.mp4') or (extension == '.avi')) 



class behavior_tracking(Video):
    """Neuropixels behavior_tracking file"""
    #lims_key = 'behavior_tracking'
    pass


class eye_tracking(Video):
    """Neuropixels eye_tracking file"""
    #lims_key = 'eye_tracking'
    pass

class face_tracking(Video):
    """Neuropixels behavior_tracking file"""
    #lims_key = 'behavior_tracking'
    pass


class GenericFile(Datastream):

    pass
    # would be kinda nice if we could get it to infer the right class (json, video, image, csv) and then load the generic version of that...
    #then we could get rid of the emptyish classes


class Json(Datastream):

    def load_datastream(self):
        """"Return the loaded data stream from the filepath """
        with open(self.file_path, 'r') as f:
            jsondata = json.load(f)#pd.read_pickle(file_path, enocoding='bytes')
        return jsondata

    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        return self.data[data_subtype_str]

    def set_data_subtype(self, data_subtype_str, value):
        self.data[data_subtype_str] = value
        with open(self.file_path, 'r') as f:
            jsondata = json.dump(self.data, f, indent=2)


class platform_json(Json):
    """Neuropixels experiment platform json"""

    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        if data_subtype_str == 'brain_surface_channel_newscale':
            try:
                data_subtype = self.data['brain_surface_channel_newscale']
            except KeyError as E:
                #run corbetts code on newscale csv here.... how does this class access newscale data. inspect?
                # this is where a calls woul dbe better than a dict. can call the "run newscale analysis" method of the class object
                data_subtype = False
        elif 'time' in data_subtype_str:
            try:
                data_subtype = self.data['brain_surface_channel_newscale']
            except Exception as E:
                #call class method to compare the times.... but this seems like it is doing a different thing. need a new validator class?
                data_subtype = False
        else:
            data_subtype = super().get_data_subtype
        return data_subtype


class Csv(Datastream):

    def load_datastream(self):
        """"Return the loaded data stream from the filepath """
        with open(self.file_path, 'r') as f:
            csv_data = pd.load(f)#pd.read_pickle(file_path, enocoding='bytes')
        return csv_data

    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        return self.data.loc[:, data_subtype_str]


class area_classifications(Csv):
    """Neuropixels experiment platform json"""

    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        if data_subtype_str == 'area_confirmed_user':
            try:
                data_subtype = self.data['area_confirmed_user']
            except KeyError as E:
                #pop up the images to allow the user to validate
                #this is where a calls woul dbe better than a dict. can call the "run newscale analysis" method of the class object
                data_subtype = False #for now
        else:
            data_subtype = super().get_data_subtype
        return data_subtype

class probe_info_json(Json):
    """Neuropixels experiment platform json"""

    def get_data_subtype(self, data_subtype_str):
        """"Return the loaded data stream from the filepath """
        if data_subtype_str == 'brain_surface_channel_manual':
            try:
                data_subtype = self.data['area_confirmed_user']
            except KeyError as E:
                #pop up the images to allow the user to validate
                #this is where a calls woul dbe better than a dict. can call the "run newscale analysis" method of the class object
                data_subtype = False #for now
        if data_subtype_str == 'brain_surface_channel_newscale':
            try:
                data_subtype = self.data['area_confirmed_user']
            except KeyError as E:
                #go grab the value from the platform json
                data_subtype = False #for now
        else:
            data_subtype = super().get_data_subtype
        return data_subtype



class Ddir(Datastream):

    def load_datastream(self):
        """"Return the loaded data stream from the filepath """
        assert(os.isdir(self.filepath))





#Depracated VVV
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

#Depracated VVV
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
    #print(file_path)
    with open(file_path, 'rb') as f:
        pklData = pickle.load(f, encoding='bytes')#pd.read_pickle(file_path, enocoding='bytes')
    return pklData

#for files that aren't really datastreams (should probably change nomenclature), mainly images that can't be loaded just check that the file extension is correct and return true



#if __name__ == "__main__":
#    main(sys.argv)




