# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:59:16 2020

@author: svc_ccg
"""
import json
import os
from collections import defaultdict, OrderedDict
import data_files_config as dfc
import sys



##config
old_cam_framerate = 30
new_cam_framerate = 60
cam_framerate_tolerance = 2

experiment_length = 180

#'pretest', 'experiment_lims', 'experiment_local', 'experiment',  'sorted_data_preliminary', 'sorted_data_lims', 'sorted_data'
params = {'functions_to_run':[]}

def make_function_params(function_name, session_types, datastreams=[]):
    if type(datastreams)==str:
        datastreams = [datastreams]
    else:
        datastreams = list(datastreams)
    params = {
        'function': function_name,
        'session_types': session_types,
        'data_streams': datastreams,
    }
    return params


def update_session_types(criterion_name:str, session_criteria:dict, session_types=None):
    if session_types is None:
        session_types = defaultdict(dict)
    for session_type, criterion in session_criteria.items():
        session_types[session_type]
        if not(criterion is None):
            session_types[session_type][criterion_name] = criterion            
    return session_types

def func_params_from_lists(session_type, function_name, datastreams=[], criterion_names=None, args_lists=None):
    params = []
    if args_lists is None:
        session_types = {session_type:{}}
        function_params = make_function_params(function_name, session_types, datastreams)
        params.append(function_params)
    else:
        for arg_list in args_lists:
            if not(type(arg_list) == list):
                arg_list = [arg_list]
            if not(type(criterion_names) == list):
                criterion_names = [criterion_names]
            session_types = None
            for idx, arg in enumerate(arg_list):
                criterion_name = criterion_names[idx]
                session_criteria = {session_type: arg}
                session_types = update_session_types(criterion_name, session_criteria, session_types)
            function_params = make_function_params(function_name, session_types, datastreams)
            #else:
            #    criterion_name = criterion_names
            #    arg = arg_list
            #    session_criteria = {session_type: arg}
            #    session_types = update_session_types(criterion_name, session_criteria)
            #    function_params = make_function_params(function_name, session_types, datastreams)
            params.append(function_params)
    return params


def add_functions_to_params(params, session_type, function_name, datastreams=[], criterion_names={}, arg_lists=None):
    function_params = func_params_from_lists(session_type, function_name, datastreams, criterion_names, arg_lists)
    params['functions_to_run'].extend(function_params)

########################################################################
#Add filesize params for each session type - should break this out into functions
function_name = 'validate_file_size'
for extension, ext_params in dfc.file_extension_dict.items():
    criterion_name = 'min_file_size'
    absolute_minimum_filesize = .5*(10**(-6))# (.5kb) in units of gigabytes
    session_criteria = {}
    session_criteria['default'] = absolute_minimum_filesize
    #create a dict of criterions here
    #loop through all possible session
    for session_type, subtypes in dfc.sesion_type_mapping.items():
    #check if the file is required for that session type
        if 'pretest' in session_type:
            key = session_type
        else:
            key = session_type+'_lims_ready'

        if ext_params.session_types in subtypes:
            if ext_params.size_min_rel is None:
                if ext_params.size_min_abs is None:
                    session_criteria[key] = None
            else:
            #if so compute the size
                for session_type2, length in dfc.sesion_type_lengths.items():
                    #print(session_type2, session_type)
                    if (session_type2 == session_type) or (('pretest' in session_type) and ('pretest' in session_type2)):
                        #and add to dict
                        session_criteria[key] = ext_params.size_min_rel*length/60

    session_types = update_session_types(criterion_name, session_criteria)
    datastreams = [ext_params.lims_key]
    function_params = make_function_params(function_name, session_types, datastreams)
    params['functions_to_run'].append(function_params)



#######################################################################
#Check the files to ensure that they exist and seem to be the files that should be associated with this expeimrent
session_type = 'pretest'

#-----------------------------------------------------------------------
data_stream = 'behavior_stimulus'
function_name = 'validate_data_subtype'

criterion_names = ['data_label', 'criterion', 'tolerance', 'criterion_descriptor']
arg_list = [
    ['Face_Exposure', new_cam_framerate, cam_framerate_tolerance],
    ['cam2_exposure', new_cam_framerate, cam_framerate_tolerance, 'body cam framerate'],
    ['cam1_exposure', new_cam_framerate, cam_framerate_tolerance, 'eye cam framerate'],
    ['barcodes',        5 ],
    ['stim_vsync',      60,                 1 ],
]
add_functions_to_params(params, session_type, function_name, data_stream, criterion_names, arg_list)

data_stream = 'behavior_stimulus'
function_name = 'validate_data_subtype'
criterion_names = ['data_label', 'criterion']
data_labels = [
    ['wheel_rotations', 2 ],
    ['lick_events', 5 ],
]
add_functions_to_params(params, session_type, function_name, data_stream, criterion_names, data_labels)

#######################################################################
#Check the files to ensure that they exist and seem to be the files that should be associated with this expeimrent
session_type = 'experiment_lims_ready'

#-----------------------------------------------------------------------
data_stream = 'platform_json'
function_name = 'validate_data_subtype'

criterion_names = 'data_label'
data_labels = [
    'motor_probe_mapping',
    'brain_surface_channel_newscale',#If this fails popup plot and field to user? Do we need a popup to confirm this suceeded anyhow?
    #add all timestamps
]
add_functions_to_params(params, session_type, function_name, data_stream, criterion_names, data_labels)


data_stream = ['platform_json', 'file_paths_json']
function_name = 'validate_platform_json_fields'
add_functions_to_params(params, session_type, function_name, data_stream)


data_stream = 'area_classifications'
function_name = 'validate_data_subtype'
criterion_names = ['data_label', 'valid_values']
valid_area_names = ['VisP', 'VisAM', 'VisPM', 'VisLM', 'VisAL', 'VisRL', 'VisRLL', 'VisAL', 'VisLI', 'Vis LLA', 'VisMMA', 'VisMMA', 'VisRS', 'VisPo', 'nonVis']
data_labels = [
    ['area', valid_area_names],#validate that the column includes acceptable labels
    ['area_confirmed_user', valid_area_names],#popup window if not present
]
add_functions_to_params(params, session_type, function_name, data_stream, criterion_names, data_labels)


#######################################################################
#Also generate a seperate params for the individual probes
session_type = 'behavior_experiment_lims_ready'


#-----------------------------------------------------------------------
function_name = 'validate_data_subtype'
criterion_names = 'data_label'

data_streams = ['platform_json', 'behavior_stiulus', 'visual_stimulus', 'replay_stimulus']
data_labels = [
    'foraging_id',#this is actually more thorough, but maybe its not necesary to make a new validator because it is only used once?
        #we maybe don't need to pass the other streams if the data_object knows where they are...
        #I guess it is kinda nice that each retrieves its own and then we confirm tha they all match. This would be data_subtype_match
        #then we can have another one that verifies the behavior pkl matches the one in lims - similar to what we do later. load this based of of rig and time, not foraging ID
    'stimulus_name',
]
add_functions_to_params(params, session_type, function_name, data_streams, criterion_names, data_labels)


#######################################################################
#Add params for the entire experiment QC
session_type = 'experiment_qc'

function_name = 'experiment_lims_verify'
#datastream session_name??? Whats this supposed to do? just check if it is in lims at all?
add_functions_to_params(params, session_type, function_name, datastreams='session_name')

function_name = 'validate_lims_match'
for extension, ext_params in dfc.file_extension_dict.items():
    add_functions_to_params(params, session_type, function_name, datastreams=ext_params.lims_key)



#######################################################################
#Add params for sorted_data
session_type = 'sorted_data_lims_ready'

#-----------------------------------------------------------------------
function_name = 'sorted_probe_lims_ready'

for probe, lims_key in dfc.sorted_data_dict.items():
    add_functions_to_params(params, session_type, function_name, datastreams=lims_key)

#-----------------------------------------------------------------------
function_name = 'no_extra_files'

for probe, lims_key in dfc.sorted_data_dict.items():
    add_functions_to_params(params, session_type, function_name, datastreams=lims_key)


#######################################################################
#Also generate a seperate params for the individual probes
session_type = 'sorted_probe_lims_ready'

#-----------------------------------------------------------------------
function_name = 'validate_file_size'
criterion_names = 'min_file_size'
absolute_minimum_filesize = .5*(10**(-6))
data_labels = [absolute_minimum_filesize]
for extension, ext_params in dfc.sorted_data_filenames.items():
    if ext_params.upload:
        data_stream = extension
        add_functions_to_params(params, session_type, function_name, data_stream, criterion_names, data_labels)


#-----------------------------------------------------------------------
function_name = 'validate_data_subtype'
criterion_names = ['data_label', 'valid_values']


data_stream = 'metrics.csv'
data_labels = [
    ['quality', ['good', 'noise']]
]
add_functions_to_params(params, session_type, function_name, data_stream, criterion_names, data_labels)

data_stream = 'probe_info.json'
criterion_names = 'data_label'
data_labels = [
    'probe_serial_number',
    'brain_surface_channel',
    'brain_surface_channel_manual',
    'brain_surface_channel_newscale',
]
add_functions_to_params(params, session_type, function_name, data_stream, criterion_names, data_labels)




#######################################################################
#Add params for each probe for sorted_data
session_type = 'sorted_data_qc'

function_name = 'sorted_probe_lims_verify'
for probe, lims_key in dfc.sorted_data_dict.items():
    add_functions_to_params(params, session_type, function_name, datastreams=lims_key)


function_name = 'sorted_probe_lims_match'
for probe, lims_key in dfc.sorted_data_dict.items():
    add_functions_to_params(params, session_type, function_name, datastreams=lims_key)

function_name = 'sorted_probe_qc'
for probe, lims_key in dfc.sorted_data_dict.items():
    add_functions_to_params(params, session_type, function_name, datastreams=lims_key)


#######################################################################
#Also generate a seperate params for the individual probes
session_type = 'sorted_probe_lims_match'

#-----------------------------------------------------------------------
function_name = 'validate_lims_match'
for extension, ext_params in dfc.sorted_data_filenames.items():
    if ext_params.upload:
        add_functions_to_params(params, session_type, function_name, datastreams=extension)


#######################################################################
#Also generate a seperate params for the individual probes
session_type = 'sorted_probe_qc'

#-----------------------------------------------------------------------


save_dir = os.path.join(sys.path[0], 'params')
os.makedirs(save_dir,exist_ok=True)

#Save the params so we can view the different params for sessions side by side
with open(os.path.join(save_dir, 'combined_params.json'), 'w') as out:
    json.dump(params, out, indent=2)



#Our QC/validation process is multilayered, with those later being more thorought than the earler ones
#At each later stage of testing we want to include the tests run at earlier stages of testing
#To make sure tests are propogated forward
#Define a hierarchy that will allow us to inherit lower level tests
session_type_hierarchy = OrderedDict()
session_type_hierarchy['coding_experiment_lims_ready'] = ['experiment_lims_ready']
session_type_hierarchy['behavior_experiment_lims_ready'] = ['experiment_lims_ready']
session_type_hierarchy['behavior_experiment_day1_lims_ready'] = ['behavior_experiment_lims_ready']
session_type_hierarchy['behavior_experiment_day2_lims_ready'] = ['behavior_experiment_lims_ready']

session_type_hierarchy['experiment_local_qc'] = ['pretest', 'experiment_lims_ready']
session_type_hierarchy['coding_experiment_local_qc'] = ['experiment_local_qc']
session_type_hierarchy['behavior_experiment_local_qc'] = ['experiment_local_qc']
session_type_hierarchy['behavior_experiment_day1_local_qc'] = ['behavior_experiment_local_qc']
session_type_hierarchy['behavior_experiment_local_day2_qc'] = ['behavior_experiment_local_qc']

session_type_hierarchy['experiment_qc'] = ['experiment_local_qc']
session_type_hierarchy['coding_experiment_qc'] = ['coding_experiment_local_qc', 'experiment_qc']
session_type_hierarchy['behavior_experiment_qc'] = ['ehavior_experiment_local_qc', 'experiment_qc']
session_type_hierarchy['behavior_experiment_day1_qc'] = ['behavior_experiment_qc', 'behavior_experiment_day1_local_qc']
session_type_hierarchy['behavior_experiment_day2_qc'] = ['behavior_experiment_qc', 'behavior_experiment_day2_local_qc']

session_type_hierarchy['sorted_data_qc'] = ['sorted_data_preliminary_qc', 'sorted_data_lims_ready']
session_type_hierarchy['sorted_probe_qc'] = ['sorted_probe_preliminary_qc', 'sorted_probe_lims_ready']


#we need to flesh it out so all the subsessions are there otherwise its hard to know when to add a function
def get_sub_sub_sessions(sub_sessions, sub_sub_session_list=[]):
    for sub_session in sub_sessions:
        if sub_session in session_type_hierarchy:
            sub_sub_sessions = session_type_hierarchy[sub_session]
            sub_sub_session_list.extend(sub_sub_sessions)
            sub_sub_session_list = get_sub_sub_sessions(sub_sub_sessions, sub_sub_session_list)
    return sub_sub_session_list

for session_type, sub_sessions in session_type_hierarchy.items():
    sub_sessions.extend(get_sub_sub_sessions(sub_sessions))



#Now we compile the lists of function_params specific to each session and print them
def add_to_func_list(session_params, session_type, session_func_dict):
    if not(session_type in session_params):
        session_params[session_type] = {'functions_to_run': []}
    session_params[session_type]['functions_to_run'].append(session_func_dict)


session_params = {}
for func_dict in params['functions_to_run']:
    try:
        args = func_dict['session_types']['default']
    except (KeyError, TypeError) as E:
        args = {}
    for session_type, override_args in func_dict['session_types'].items():
        #if not(session_type == 'default'):
        session_args = args.copy()
        session_args.update(override_args)
        session_func_dict = {
            'function': func_dict['function'],
            'args': session_args,
            'data_streams': func_dict['data_streams'],
        }
        add_to_func_list(session_params, session_type, session_func_dict)
        if '_only' in session_type:
            session_type_key = session_type[:-5]
            add_to_func_list(session_params, session_type_key, session_func_dict)
    for higher_session_type, sub_sessions in session_type_hierarchy.items():
        already_added = higher_session_type in func_dict['session_types']
        inherit_from_lower = set(func_dict['session_types']).intersection(set(sub_sessions))

        if not(already_added) and inherit_from_lower:
             for sub_session in sub_sessions:#This loop is here so that we get the correct ordering based on the list. Set could give ambiguous
                if sub_session in func_dict['session_types']:
                    inherit_func_dict = session_params[sub_session]['functions_to_run'][-1]
                   #print(inherit_func_dict)
                    if sub_session == 'experiment_lims_ready':
                        print('adding lower')
                        #print(inherit_func_dict)
                        print('from session '+ sub_session)
                        print('to higher session:' +higher_session_type)
                        print(inherit_func_dict)
                   # print(higher_session_type, sub_sessions, func_dict['session_types'], inherit_from_lower)
#
                    add_to_func_list(session_params, higher_session_type, inherit_func_dict)
                    break
#before saving we could go through and add the unique output name, and make it a dict instead of a list?
#then it might be easier to map the input to the output? list isn't sufficuent because we chekc all the streams first. don't really want to put this in a different section


#Create the full dictionaries of params to be written for each session type
for session_type, session_func_dict in session_params.items():
    params_name = session_type+'_params.json'
    with open(os.path.join(save_dir, params_name), 'w') as out:
        json.dump(session_func_dict, out, indent=2)



old_params = {
            'functions_to_run' : [
                    {
                        'function': 'validate_data_subtype',
                        'session_types': {
                            'default': {
                                'data_label': 'stim_vsync',
                                'tolerance': 1,
                                'criterion': 60
                            },
                            'pretest': {}
                        },
                        'data_streams': ['synchronization_data'],
                    },
                    {
                        'function': 'validate_data_subtype',
                        'session_types': {
                            'default': {
                                'data_label': 'barcodes',
                                'criterion': 5
                            },
                            'pretest': {}
                        },
                        'data_streams': ['synchronization_data'],
                    },
                    {
                        'function': 'validate_data_subtype',
                        'session_types': {
                            'default': {
                                'data_label': 'cam1_exposure',
                                'criterion': new_cam_framerate,
                                'tolerance': cam_framerate_tolerance,
                                'criterion_descriptor': 'eye cam framerate'
                            },
                            'pretest': {}
                        },
                        'data_streams': ['synchronization_data'],
                    },
                    {
                        'function': 'validate_data_subtype',
                        'session_types': {
                            'default': {
                                'data_label': 'cam2_exposure',
                                'criterion': new_cam_framerate,
                                'criterion_descriptor': 'body cam framerate',
                                'tolerance': cam_framerate_tolerance
                            },
                            'pretest': {},
                            'experiment_local_pre_mvr': {
                                'data_label': 'cam2_exposure',
                                'criterion': old_cam_framerate,
                                'tolerance': cam_framerate_tolerance
                            },
                        },
                        'data_streams': ['synchronization_data'],
                    },
                    {
                        'function': 'validate_data_subtype',
                        'session_types': {
                            'default': {
                                'data_label': 'Face_Exposure',
                                'criterion': new_cam_framerate,
                                'tolerance': cam_framerate_tolerance,
                            },
                            'pretest': {}
                        },
                        'data_streams': ['synchronization_data'],
                    },
                    {
                        'function': 'validate_data_subtype',
                        'session_types': {
                            'default': {
                                'data_label': 'lick_events',
                                'criterion': 5,
                            },
                            'pretest': {}
                        },
                        'data_streams': ['behavior_stimulus'],
                    },
                    {
                        'function': 'validate_data_subtype',
                        'session_types': {
                            'default': {
                                'data_label': 'wheel_rotations',
                                'criterion' : 2,
                            },
                            'pretest': {}
                        },
                        'data_streams': ['behavior_stimulus'],
                    },
                ]
          }