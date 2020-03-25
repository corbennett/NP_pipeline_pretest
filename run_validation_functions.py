# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:08:47 2020

@author: svc_ccg
"""
import pretest_validation_functions
import json
import pandas as pd
from sync_dataset import Dataset
import sys


def main(argv):
    
    with open(argv[1]) as json_params:
        params = json.load(json_params)
    
    with open(argv[2]) as json_params:
        file_paths = json.load(json_params)
    
#    with open(r"Z:\pretest\params.json") as json_params:
#        params = json.load(json_params)
    
    syncDataset = Dataset(file_paths['file_paths']["synchronization_data"])
    pklData = pd.read_pickle(file_paths['file_paths']["behavior_stimulus"])
    
    datastream_dict = {'sync' : syncDataset,
                       'pkl' : pklData}

    #### Run validation functions ####
    validation_results = {}
    functions_to_run = params['functions_to_run']
    for func_dict in functions_to_run:
        func_name = func_dict['function']
        output_name = func_dict['output_name']
        kwargs = func_dict['args']
        datastream_string = func_dict['data_stream']
        criterion_descriptor = func_dict['criterion_descriptor']

        datastream = datastream_dict[datastream_string]
        
        func = getattr(pretest_validation_functions, func_name)
        val, outcome_bool = func(datastream, **kwargs)

        result_string = get_result_string(datastream_string, val, outcome_bool, criterion_descriptor, kwargs)
        validation_results[output_name] = {'value': val, 'success': int(outcome_bool)}
        
    
    
    
    
    save_path= argv[3]
    with open(save_path, 'w') as out:
        json.dump(validation_results, out, indent=2)
    
 def get_result_string(datastream, val, outcome_bool, criterion_descriptor, kwargs):

    criterion = str(kwargs['criterion'])

    if 'tolerance' in kwargs:
        tolerance = str(kwargs['tolerance'])
        sucess_str = 'was not'
        if outcome_bool:
            sucess_str = 'was'
        result_string = f'{criterion_descriptor} of {val} in {datastream} {sucess_str} within {tolerance} of goal criterion {criterion}'
    else:
        sucess_str = 'did not exceed'
        if outcome_bool:
            sucess_str = 'exceeded'
        result_string = f'{criterion_descriptor} of {val} in {datastream} {sucess_str} minimum goal criterion {criterion}'
    
    return result_string
    

if __name__ == "__main__":
    main(sys.argv)
    