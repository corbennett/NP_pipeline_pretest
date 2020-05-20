# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:08:47 2020

@author: svc_ccg
"""
import json
import os
import sys

import logging
from pprint import pprint
import validation_functions


#class data_object(object):
    #we just need to be able to add the loaded data streams to a dictionary in here

    # need to learn how to load  stuff from lims
    #is this really necessary? we already put them in a dictionary, the class is pointles sunless we are gona have class methods


def data_stream_error(E, validation_results, datastream_name_out, datastream_name, datastream_path):
    logging.exception(E)
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(E).__name__, E.args)
    print(message)
    validation_results[datastream_name_out] = {'value': False, 'success': 0, 'result string': f"Failed to retrive data for {datastream_name} found at {datastream_path}: {message}"}


def main(argv):

    with open(argv[1]) as json_params:
        params = json.load(json_params)

    with open(argv[2]) as json_params:
        file_paths = json.load(json_params)['file_paths']

    validation_results = {}
    functions_to_run = params['functions_to_run']

    datastream_set = set()
    for func_dict in functions_to_run:
        datastreams_needed = set(func_dict['data_streams'])
        #logging.info(func_dict['data_streams'], datastreams_needed)
        datastream_set = datastream_set.union(datastreams_needed)

    datastream_dict = {}
    for datastream_name in datastream_set:
        print(f'Validating existance of datastream: {datastream_name}')
        datastream_name_out = datastream_name+'_found'
        if not(datastream_name in file_paths):
            validation_results[datastream_name_out] = {'value': False, 'success': 0, 'result string': f"Path for {datastream_name} was not found in params json, {argv[2]}"}
        else:
            datastream_path = file_paths[datastream_name]
            if not(os.path.exists(datastream_path)):
                validation_results[datastream_name_out] = {'value': False, 'success': 0, 'result string': f"File for {datastream_name} was not found at {datastream_path}"}
            else:
                if 'ephys_sorted_data_probe' in datastream_name:
                    try:
                        getter_func =  getattr(validation_functions, 'Ddir')
                        datastream_dict[datastream_name] = getter_func(file_path=datastream_path, lims_key=datastream_name)
                        validation_results[datastream_name_out] = {'value': True, 'success': 1, 'result string': f"Sucessfully retrieved data for {datastream_name}"}
                    except Exception as E:
                        data_stream_error(E, validation_results, datastream_name_out, datastream_name, datastream_path)
                try:
                    getter_func =  getattr(validation_functions, datastream_name)
                    datastream_dict[datastream_name] = getter_func(file_path=datastream_path, lims_key=datastream_name)
                    validation_results[datastream_name_out] = {'value': True, 'success': 1, 'result string': f"Sucessfully retrieved data for {datastream_name}"}
                except AttributeError as E:
                    try:
                        getter_func =  getattr(validation_functions, 'GenericFile')
                        datastream_dict[datastream_name] = getter_func(file_path=datastream_path, lims_key=datastream_name)
                        validation_results[datastream_name_out] = {'value': True, 'success': 1, 'result string': f"Sucessfully retrieved data for {datastream_name}"}
                    except Exception as E:
                        data_stream_error(E, validation_results, datastream_name_out, datastream_name, datastream_path)
                except Exception as E:
                    data_stream_error(E, validation_results, datastream_name_out, datastream_name, datastream_path)
    #### Run validation functions ####


    for func_dict in functions_to_run:
        func_name = func_dict['function']
        logging.info(f'Attempting to run validation function {func_name}')
        kwargs = func_dict['args']
        datastream_list = func_dict['data_streams']
        found_datastreams = set(datastream_dict)
        #print(found_datastreams)
        datastreams_present = set(datastream_list).issubset(found_datastreams)
        print(datastreams_present)
        if datastreams_present:
            if len(datastream_list)>1:
                datastreams = {}
                for datastream_name in datastream_list:
                    datastreams[datastream_name] = datastream_dict[datastream_name]
            else:
                try:
                    datastreams = datastream_dict[datastream_list[0]]
                except IndexError as E:
                    datastreams=None
            #make set of necessary datastreams
            try:
                validator = getattr(validation_functions, func_name)(datastreams=datastreams,datastream_list=datastream_list, **kwargs)
                output_name = validator.output_name
                print(output_name)
                out_list = validator.run_validation()
            except AttributeError as E:
                #this is for backwards compatibility with the old functions that are not classes
                output_name = func_dict['output_name']
                out_list = getattr(validation_functions, func_name)(datastreams, **kwargs)
            val = out_list[0]
            outcome_bool = out_list[1]
            print(outcome_bool)
            result_string = out_list[2]

            validation_results[output_name] = {'value': val, 'success': int(outcome_bool), 'result string': result_string}

    save_path= argv[3]
    with open(save_path, 'w') as out:
        json.dump(validation_results, out, indent=2)





#Depracated VVV
def get_result_string(datastream_list, val, outcome_bool, criterion_descriptor, kwargs):

    criterion = str(kwargs['criterion'])
    if len(datastream_list) == 1:
        datastream = datastream_list[0]
        if 'tolerance' in kwargs:
            tolerance = str(kwargs['tolerance'])
            sucess_str = 'was not'
            if outcome_bool:
                sucess_str = 'was'
            result_string = f'{criterion_descriptor} of {val} in {datastream} {sucess_str} within {tolerance} of goal criterion {criterion}'
        else:
            sucess_str = 'did not exceed or match'
            if outcome_bool:
                sucess_str = 'exceeded or matched'
            result_string = f'{criterion_descriptor} of {val} in {datastream} {sucess_str} goal criterion {criterion}'
    else:
        sucess_str = 'did not match'
        if outcome_bool:
            sucess_str = 'matched'
        result_string = f'{criterion_descriptor} of {val[0]} in {datastream[0]} {sucess_str} {criterion_descriptor} of {val[1]} in {datastream[1]}'
    return result_string


if __name__ == "__main__":
    main(sys.argv)
