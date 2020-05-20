#from collections import named_tuple
import data_files_config as dfc

import glob
import os
import json

def get_experiment_filepaths(ddir, session_name=None):
    exp_files = {}
    for suffix, params in dfc.file_extension_dict.items():
        name = params.lims_key
        for filename in os.listdir(ddir):
            session_match = ((session_name is None) or (session_name in filename))
            filepath = os.path.join(ddir, filename)
            exists = os.path.exists(filepath)
            if (suffix in filename) and session_match and exists:
                exp_files[name]  = filepath
    return exp_files


def get_raw_data_dirpaths(ddir, session_name=None):
    exp_raw = {}
    for suffix, name in dfc.raw_data_dict.items():
        for filename in os.listdir(ddir):
            session_match = ((session_name is None) or (session_name in filename))
            filename_match = (suffix in filename) and ('probe' in filename) and not('sorted' in filename)
            dirpath = os.path.join(ddir, filename)
            if filename_match and session_match and os.path.isdir(dirpath):
                exp_raw[name]  = dirpath
    return exp_raw



def get_sorted_data_dirpaths(ddir, session_name=None):
    exp_sorted = {}
    for suffix, name in dfc.sorted_data_dict.items():
        for filename in os.listdir(ddir):
            session_match = ((session_name is None) or (session_name in filename))
            filename_match = (suffix in filename) and ('probe' in filename) and ('sorted' in filename)
            dirpath = os.path.join(ddir, filename)
            if filename_match and session_match and os.path.isdir(dirpath):
                exp_sorted[name]  = dirpath
    return exp_sorted



def make_experiment_file_paths_json(ddir, session_name=None):
    file_paths = {
                    'file_paths': {}
    }
    if session_name is None:
        session_name = os.path.split(ddir)
    file_paths['file_paths'].update(get_experiment_filepaths(ddir, session_name))
    file_paths['file_paths'].update(get_raw_data_dirpaths(ddir, session_name))
    file_paths['file_paths'].update(get_sorted_data_dirpaths(ddir, session_name))
    file_paths['file_paths']['session_name'] = session_name

    file_paths_path = os.path.join(ddir, 'experiment_file_paths.json')
    with open(file_paths_path, 'w') as out:
        json.dump(file_paths, out, indent=2)

    return file_paths_path

def get_sorted_probe_filepaths(ddir):
    data_sorted = {}
    for filename, params in dfc.sorted_data_filenames.items():
        fullpaths = glob.glob(os.path.join(ddir, data_relpaths[params.relpath], filename))
        if len(fullpaths==1) and params.upload:
            path = fullpaths[0]
            if os.path.exists(path):
                unique_key = filename.replace('.', '_')
                data_sorted[unique_key] = path
    return data_sorted


def make_sorted_probe_filepaths_json(ddir, probe, session_name=None, save_location=None, prefix=''):
    file_paths = {
                    'file_paths': {}
    }
    file_paths['file_paths'].update(get_sorted_probe_filespaths(ddir))
    #we need the session and probe to be able to retrieve matching data from lims
    if session_name is None:
        probe_dir = os.path.split(ddir)[1]
        session_name = '_'.join(probe_dir.split('_')[:3])
        ###TODO this is bad and hacky - and won't work for lims loaded sessions. We need to grab it from a experiment object
    file_paths['file_paths']['session_name'] = session_name
    file_paths['file_paths']['probe'] = probe
    if save_location is None:
        save_location = ddir
    file_paths_path = os.path.join(save_location, prefix+'sorted_file_paths.json')
    with open(file_paths_path, 'w') as out:
        json.dump(file_paths, out, indent=2)
    return fil_paths_path
