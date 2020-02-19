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
        
#    with open(r"Z:\pretest\params.json") as json_params:
#        params = json.load(json_params)
    
    syncDataset = Dataset(params['file_paths']['SYNC_FILE_PATH'])
    pklData = pd.read_pickle(params['file_paths']['PKL_FILE_PATH'])
    
    datastream_dict = {'sync' : syncDataset,
                       'pkl' : pklData}

    #### Run validation functions ####
    validation_results = {}
    functions_to_run = params['functions_to_run']
    for func_dict in functions_to_run:
        func_name = func_dict['function']
        output_name = func_dict['output_name']
        kwargs = func_dict['args']
        datastream = datastream_dict[func_dict['data_stream']]
        
        func = getattr(pretest_validation_functions, func_name)
        
        validation_results[output_name] = int(func(datastream, **kwargs))
    
    
    
    
    save_path= argv[2]
    with open(save_path, 'w') as out:
        json.dump(validation_results, out, indent=2)
    
    
    

if __name__ == "__main__":
    main(sys.argv)
    