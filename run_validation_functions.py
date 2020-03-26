# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:08:47 2020

@author: svc_ccg
"""
import json



def main(argv):
    
    with open(argv[1]) as json_params:
        params = json.load(json_params)
    
    with open(argv[2]) as json_params:
        file_paths = json.load(json_params)['file_paths']
    
    validation_results = {}
    functions_to_run = params['functions_to_run']

    datastream_set = set()
    for func_dict in functions_to_run:
        datastream_set.add(func_dict['data_streams'])

    datastream_dict = {}
    for datastream_name in datastream_set:
        if not(datastream_name in file_paths):
            validation_results[get_datstream_func_name] = {'value': False, 'success': 0, 'result string': f"Path for {datastream_name} was not found in params json, {argv[2]}"}
        else:
            datastream_path = file_paths[datastream]
            if not(os.path.exists(datastream_path))
                validation_results[get_datstream_func_name] = {'value': False, 'success': 0, 'result string': f"File for {datastream_name} was not found at {datastream_path}"}
            else:
                try
                    get_datstream_func_name = 'get_'+datastream_name
                    getter_func = globals()[get_datstream_func_name]
                    datastream_dict[datastream] = getter_func(datastream_path)
                    validation_results[get_datstream_func_name] = {'value': True, 'success': 1, 'result string': f"Sucessfully retrieved data for {datastream_name}"}
                except Exception as E:
                    validation_results[get_datstream_func_name] = {'value': False, 'success': 0, 'result string': f"Failed to retrive data for {datastream_name} found at {datastream_path}"}

    #### Run validation functions ####

    
    for func_dict in functions_to_run:
        func_name = func_dict['function']
        output_name = func_dict['output_name']
        kwargs = func_dict['args']
        datastream_list = func_dict['data_streams']
        criterion_descriptor = func_dict['criterion_descriptor']
        if set(datastream_list).issubset(set(datastream_dict.keys)):
            if len(datastream_list)>1:
                datastreams = {}
                for datastream_string in datastream_list:
                    datastreams[datastream] = datastream_dict[datastream_string]
            else:
                datastreams = datastream_dict[datastream_string]
            #make set of necessary datastreams
            
            func = globals()[func_name]#getattr(pretest_validation_functions, func_name)
            val, outcome_bool = func(datastreams, **kwargs)

            result_string = get_result_string(datastream_list, val, outcome_bool, criterion_descriptor, kwargs)
            validation_results[output_name] = {'value': val, 'success': int(outcome_bool), 'result string': result_string}
    
    save_path= argv[3]
    with open(save_path, 'w') as out:
        json.dump(validation_results, out, indent=2)
    
def get_result_string(datastream_list, val, outcome_bool, criterion_descriptor, kwargs):

    criterion = str(kwargs['criterion'])
    if len(datastream_list) = 1:
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
    

#if __name__ == "__main__":
#    main(sys.argv)
    