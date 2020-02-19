# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:08:47 2020

@author: svc_ccg
"""
import pretest_validation_functions
import json
import pandas as pd
from sync_dataset import Dataset
import os, sys


def main(argv):
    
    with open(argv[1]) as json_params:
        params = json.load(json_params)
        
#    with open(r"Z:\pretest\params.json") as json_params:
#        params = json.load(json_params)
    
    
    syncDataset = Dataset(params['file_paths']['SYNC_FILE_PATH'])
    pklData = pd.read_pickle(params['file_paths']['PKL_FILE_PATH'])

    #### Run validation functions ####
    validation_results = {}
    functions_to_run = params['functions_to_run']
    for func_dict in functions_to_run:
        func_name = func_dict['function']
        kwargs = func_dict['args']
        func = getattr(pretest_validation_functions, func_name)
        
        if 'cam' in func_name:
            func_key = func_name + '_' + kwargs['line_label']
        else:
            func_key = func_name
        
        if 'sync' in func_name:
            validation_results[func_key] = int(func(syncDataset, **kwargs))
        else: 
            validation_results[func_key] = int(func(pklData, **kwargs))
    
    
    
    
    save_dir= argv[2]
    with open(os.path.join(save_dir, 'validation_results.json'), 'w') as out:
        json.dump(validation_results, out, indent=2)
    
    
    

if __name__ == "__main__":
    main(sys.argv)
    