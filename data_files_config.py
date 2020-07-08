from collections import namedtuple
import copy

#def create_file_extensions_dict():
    #TODO I'm thinking this whole dictionary should just live in the config, that would make things a lot clearner, and way easier to dupdate without messing with WSE
    #TODO everything should be re-written to rely on this. e.g. moving of avi files
    #maybe pkl file moving could rely on this dict too? right now I'm creating a dict with all falses...
extension_params = namedtuple('extension_params', ['session_types', 'size_min_rel', 'size_min_abs', 'lims_key'])

#weight = float(state_globals['external']['mouse_weight'])
#mouse_proxy = state_globals['component_proxies']['']


#kb to gb -> *(10**(-6))

def create_file_extension_dict(session_type):
    pass
    #we want to use this to spit it out with minimum size dependant on experiment length - or we could make it standard for 1 hr
    # and then adjust later. I kinda like this.

file_extension_dict = {
    ".behavior.avi": extension_params('old_vmon', 999, 999, "behavior_tracking"),
    ".eye.avi": extension_params('old_vmon', 999, 999, "eye_tracking"),
    ".behavior.mp4": extension_params('new_vmon', 999, 999, "behavior_tracking"),
    ".eye.mp4": extension_params('new_vmon', 999, 999, "eye_tracking"),
    ".face.mp4": extension_params('new_vmon', 999, 999, "face_tracking"),
    ".behavior.json": extension_params('new_vmon', None, None, "beh_cam_json"),
    ".eye.json": extension_params('new_vmon', None, None, "eye_cam_json"),
    ".face.json": extension_params('new_vmon', None, None, "face_cam_json"),
    ".stim.pkl": extension_params('stim', 999, 999, "visual_stimulus"),
    ".behavior.pkl": extension_params('behavior', 999, 999, "behavior_stimulus"),
    ".replay.pkl": extension_params('replay', 999, 999, "replay_stimulus"),
    #"_report.pdf": extension_params('all', 999, 999, "sync_report"),
    "_surgeryNotes.json": extension_params('all', None, None, "surgery_notes"),
    ".sync": extension_params('all', 999, 999, "synchronization_data"),
    "_platformD1.json": extension_params('all', None, None, 'platform_json'),
    ".motor-locs.csv": extension_params('probeLocator', None, None, "newstep_csv"),
    ".opto.pkl": extension_params('opto', None, None, "optogenetic_stimulus"),
    "_surface-image1-left.png": extension_params('exp', None, None, "pre_experiment_surface_image_left"),
    "_surface-image1-right.png": extension_params('exp', None, None, "pre_experiment_surface_image_left"),
    "_surface-image2-left.png": extension_params('all', None, None, "brain_surface_image_left"),
    "_surface-image2-right.png": extension_params('all', None, None, "brain_surface_image_right"),
    "_surface-image3-left.png": extension_params('exp', None, None, "pre_insertion_surface_image_left"),
    "_surface-image3-right.png": extension_params('exp', None, None, "pre_insertion_surface_image_right"),
    "_surface-image4-left.png": extension_params('exp', None, None, "post_insertion_surface_image_left"),
    "_surface-image4-right.png": extension_params('exp', None, None, "post_insertion_surface_image_right"),
    "_surface-image5-left.png": extension_params('exp', None, None, "post_stimulus_surface_image_left"),
    "_surface-image5-right.png": extension_params('exp', None, None, "post_stimulus_surface_image_right"),
    "_surface-image6-left.png": extension_params('exp', None, None, "post_experiment_surface_image_left"),
    "_surface-image6-right.png": extension_params('exp', None, None, "post_experiment_surface_image_right"),
    ".areaClassifications.csv": extension_params('probeLocator', None, None, "area_classifications"),
    ".overlay.png": extension_params('probeLocator', None, None, "overlay_image"),
    ".fiducial.png": extension_params('probeLocator', None, None, "fiducial_image"),
    ".insertionLocation.png": extension_params('probeLocator', None, None, "insertion_location_image"),
    ".ISIregistration.npz": extension_params('probeLocator', None, None, "isi_registration_coordinates"),
    ".surgeryImage1.png": extension_params('surgery', None, None, "post_removal_surgery_image"),
    ".surgeryImage2.png": extension_params('surgery', None, None, "final_surgery_image")
}


#what would we include here? number of pkls, experiment length,

session_type_params = namedtuple('session_type_params', ['session_subtypes', 'minimum_session_length', 'num_pkls'])
#num pkls could be computed...


all_options = {'exp', 'Hab', 'surgery', 'all', 'probeLocator', 'behavior', 'stim', 'replay'}

sesion_type_mapping = {}
sesion_type_mapping['behavior_habituation'] = {'behavior', 'all'}
sesion_type_mapping['behavior_habituation_last'] = {'behavior', 'probeLocator', 'all', }
sesion_type_mapping['behavior_pretest'] = {'behavior', 'stim', 'replay', 'opto', 'probeLocator', 'all', }
sesion_type_mapping['behavior_experiment_day2'] = {'exp', 'behavior', 'stim', 'replay', 'opto', 'probeLocator', 'all', }
sesion_type_mapping['behavior_experiment_day1'] = {'surgery', 'exp', 'behavior', 'stim', 'replay', 'opto', 'probeLocator', 'all', }

sesion_type_mapping['coding_habituation'] = {'stim', 'all',}
sesion_type_mapping['coding_habituation_last'] = {'stim', 'probeLocator', 'all',}
sesion_type_mapping['coding_pretest'] = {'stim', 'opto', 'probeLocator', 'all',}
sesion_type_mapping['coding_experiment'] = {'exp', 'stim', 'opto', 'probeLocator', 'all',}

copy_sesion_type_mapping = copy.deepcopy(sesion_type_mapping)
for session_type, session_subtypes in sesion_type_mapping.items():
    session_subtypes.add('new_vmon')
#for session_type, session_subtypes in copy_sesion_type_mapping.items():
#    session_subtypes.add('old_vmon')
#    new_key = session_type+'_pre_mvr'
#   sesion_type_mapping[new_key] = session_subtypes
##^^ instead of doing this I think I just want to add them to a json with sessions to ignor for 
#certain tests, and tests to ignor for certain sessions. That seems like it will be cleaner since
#we don't anticipate recording data in this format

sesion_type_lengths = {
    'behavior_experiment_day1': 75+25+60+10,
    'behavior_experiment_day2': 75+25+60+10,
    'behavior_habituation_last': 60+5,
    'behavior_habituation': 60+5,
    'coding_experiment': 175,
    'coding_habituation_last': 100,
    'coding_habituation': 80,
    'pretest': 3,
}



raw_data_dict = {
    'ABC': "ephys_raw_data_probe_A",
    'DEF': "ephys_raw_data_probe_D",
}



data_relpaths = {
                'lfp':r"continuous\Neuropix-*-100.1",
                'spikes':r"continuous\Neuropix-*-100.0",
                'events':r"events\Neuropix-*-100.0\TTL_1",
                'empty':""
                    }

sorted_data_dict = {
    'A': "ephys_sorted_data_probe_A",
    'B': "ephys_sorted_data_probe_B",
    'C': "ephys_sorted_data_probe_C",
    'D': "ephys_sorted_data_probe_D",
    'E': "ephys_sorted_data_probe_E",
    'F': "ephys_sorted_data_probe_F",
}

data_file_params = namedtuple('data_file_params',['relpath','upload','sorting_step'])
sorted_data_filenames = {
      "probe_info.json":data_file_params('empty',True,'depth_estimation'),
      "channel_states.npy":data_file_params('events',True,'extraction'),
      "event_timestamps.npy":data_file_params('events',True,'extraction'),
      #r"continuous\Neuropix-{}-100.1\continuous.dat".format(probe_type):data_file_params('empty',True,'extraction'),
      "continuous.dat":data_file_params('lfp',True,'extraction'),
      "lfp_timestamps.npy":data_file_params('lfp',True,'extraction'),
      "amplitudes.npy":data_file_params('spikes',True,'sorting'),
      "spike_times.npy":data_file_params('spikes',True,'sorting'),
          "mean_waveforms.npy":data_file_params('spikes',True,'mean waveforms'),
          "spike_clusters.npy":data_file_params('spikes',True,'sorting'),
          "spike_templates.npy":data_file_params('spikes',True,'sorting'),
          "templates.npy":data_file_params('spikes',True,'sorting'),
          "whitening_mat.npy":data_file_params('spikes',True,'sorting'),
          "whitening_mat_inv.npy":data_file_params('spikes',True,'sorting'),
          "templates_ind.npy":data_file_params('spikes',True,'sorting'),
          "similar_templates.npy":data_file_params('spikes',True,'sorting'),
          "metrics.csv":data_file_params('spikes',True,'metrics'),
          "waveform_metrics.csv":data_file_params('spikes',False,'metrics'),
          "channel_positions.npy":data_file_params('spikes',True,'sorting'),
          #"cluster_group.tsv":data_file_params('spikes',True,'sorting'),
          "cluster_Amplitude.tsv":data_file_params('spikes',False,'sorting'),
          "cluster_ContamPct.tsv":data_file_params('spikes',False,'sorting'),
          "cluster_KSLabel.tsv":data_file_params('spikes',False,'sorting'),
          "channel_map.npy":data_file_params('spikes',True,'sorting'),
          "params.py":data_file_params('spikes',True,'sorting'),
      "probe_depth.png":data_file_params("empty",False,'depth estimation'),
      r"continuous\Neuropix-*-100.0\continuous.dat":data_file_params('empty',False,'extraction'),
      "residuals.dat":data_file_params('spikes',False,'median subtraction'),
      "pc_features.npy":data_file_params('spikes',False,'sorting'),
      "template_features.npy":data_file_params('spikes',False,'sorting'),
      "rez2.mat":data_file_params('spikes',False,'sorting'),
      "rez.mat":data_file_params('spikes',False,'sorting'),
      "pc_feature_ind.npy":data_file_params('spikes',False,'sorting'),
      "template_feature_ind.npy":data_file_params('spikes',False,'sorting')
      }


