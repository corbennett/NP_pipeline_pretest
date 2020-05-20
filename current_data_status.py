import os
import pandas as pd
import json
from experiment_files import make_experiment_file_paths_json
import sys
import data_files_config as dfc
import subprocess


#import limstk


directory_list = [r'\\10.128.50.43\sd6.2']

columns = ['session_name', 'experiment_files', 'sorted_data_files', 'experiment_lims', 'sorted_data_lims']

validation_list = ['lims_ready', 'qc']#, 'sorted_data_lims_ready', 'sorted_data_qc']
columns = [
    'session_name',
    'session_type',
    'experiment_all_files_present',
    'experiment_lims_validation_passed',
    'experiment_lims_uploaded',
    'experiment_lims_match_local',
    'experiment_qc_passed',
    'sorted_data_all_files_present',
    'sorted_data_lims_validation_passed',
    'sorted_data_lims_uploaded',
    'sorted_data_lims_match_local',
    'sorted_data_qc_passed',
]



            #construct the dataframe

def check_all_ouput(validation_output):
    all_sucess = True
    for validation_result, ouput in validation_output:
        if not(ouput['sucess']):
            all_sucess = False
            break
    return all_sucess


def check_subtype_output(validation_output, subtype_strings:set):
    subtype_dict = {}
    for validation_result, ouput in validation_output:
        if all([(s in validation_result) for s in subtype_strings]):
            subtype_dict[validation_result] = ouput
    return check_all_ouput(subtype_dict)



def determine_session_type(session_dir, directory_list):
    session_id, mouse_number, date = session_dir.split('_')

    #best way to do this - use limstk to query mouse project code
    #return 'visual_behavior' or 'visual_coding'
    #then if behvior see if its the earlier or later experiment
    #result = limstk.donor_info(mouse_number)
    #project_code = result[0]["specimens"][0]["project"].get("code", "No Project Code")
    project_code = 'visual_behavior'
    if 'visual_coding' in project_code:
        project_type = 'coding_experiment'
    elif 'visual_behavior' in project_code:
        project_type = 'behavior_experiment'

    suffix = ''
    date_list = []
    for directory in directory_list:
        for subdir in os.listdir(directory):
            if len(subdir.split('_'))== 3:
                sub_session_id, sub_mouse_number, sub_date = session_dir.split('_')
                if sub_mouse_number == mouse_number:
                    date_list.append(sub_date)
    if date_list:
        suffix = '_day'+str(date_list.index(date)+1)
    return project_type+suffix


def determine_mvr(session_dir):
    #return('' or '_pre_mvr')
    mvr = True
    for filename in os.listdir(session_dir):
        if 'eye.avi' in filename:
            mvr = False
    return mvr

if __name__=='__main__':

    validation_ignore = {}
    validation_ignore_path = os.path.join(sys.path[0], 'params', 'validation_ignore.json')
    if os.path.exists(validation_ignore_path):
        with open(validation_ignore_path, 'r') as f:
            validation_ignore = json.load(f)

    df = pd.DataFrame(columns=columns)
    for directory in directory_list:
        for sub_dir in os.listdir(directory):
            fake_loop = True
            if fake_loop:
                directory = r"\\10.128.50.43\sd6.2"
                sub_dir = r"1013651431_496639_20200311"
            session = sub_dir
            if len(sub_dir.split('_'))== 3:
                #run validation for directory -
                session_results_dict = {}
                session_results_dict['session_name'] = sub_dir
                session_type = determine_session_type(sub_dir, directory_list)
                session_results_dict['session_type'] = session_type
                dirpath = os.path.join(directory, sub_dir)
                mvr = determine_mvr(dirpath)
                if not(mvr):
                    if not(session) in validation_ignore:
                        validation_ignore[session] = set()
                    validation_ignore[session] = list(set(validation_ignore[session]).union({'face_tracking', 'beh_cam_json', 'eye_cam_json', 'face_cam_json'}))
                    #TODO update the ignore json with these sessions.
                    with open(validation_ignore_path, 'w') as f:
                        json.dump(validation_ignore, f, indent=2)

                for validation_type in validation_list:
                    full_validation_type = session_type+'_'+validation_type
                    if 'sorted' in validation_type:
                        full_validation_type = validation_type
                    params_path = os.path.join(sys.path[0], 'params', full_validation_type+'_params.json') #may need fullpath here?


                    dirpath = os.path.join(directory, sub_dir)
                    file_paths_path = make_experiment_file_paths_json(dirpath, session_name=sub_dir)
                    output_path = os.path.join(dirpath, full_validation_type+'_output.json')
                    engine_path = os.path.join(sys.path[0], 'run_validation_functions.py')
                    command_string = ['python', engine_path, params_path, file_paths_path, output_path]

                    P = subprocess.Popen(command_string)
                    out, err = P.communicate()
                    print(out)
                    print(err)
                    with open(output_path, 'r') as f:
                        validation_output = json.load(f)

                    if validation_type == 'experiment_lims':
                        session_results_dict['experiment_lims_validation_passed'] = 'waiting - validation functions incomplete'#check_all_ouput(validation_output)
                        subtype_strings = {'min file size'}# may need to use file size here? or could rely on the faiure to use key "* file_found"
                        session_results_dict['experiment_all_files_present'] = check_subtype_output(validation_output, subtype_strings)

                    elif validation_type =='experiment_qc':
                        session_results_dict['experiment_lims_uploaded'] = validation_output['experiment_found in lims']['sucess']
                        subtype_strings = {'match'}
                        session_results_dict['experiment_lims_match_local'] = check_subtype_output(validation_output, subtype_strings)

                        session_results_dict['experiment_qc_passed'] = 'waiting - validation functions incomplete'#check_all_ouput(validation_output)

                    elif validation_type == 'sorted_data_lims':
                        session_results_dict['sorted_data_lims_validation_passed'] = check_all_ouput(validation_output)
                        subtype_strings = {'min file size'}# may need to use file size here? or could rely on the faiure to use key "* file_found"
                        session_results_dict['sorted_data_all_files_present'] = check_subtype_output(validation_output, subtype_strings)


                    elif validation_type == 'sorted_data_qc':
                        subtype_strings = {'found in lims'}
                        session_results_dict['sorted_data_lims_uploaded'] = check_subtype_output(validation_output, subtype_strings)
                        subtype_strings = {'identical to local'}
                        session_results_dict['sorted_data_lims_match_local'] = check_subtype_output(validation_output, subtype_strings)
                        session_results_dict['sorted_data_qc_passed'] = 'waiting - validation functions incomplete'#check_all_ouput(validation_output)
                df.append(session_results_dict, ignore_index=True)
            if fake_loop:
                break


    df.to_csv(os.path.join(sys.path[0], 'current_data_status.csv'))


