# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 12:15:38 2020

@author: svc_ccg
"""
import numpy as np
import os
#from visual_behavior.ophys.sync import sync_dataset
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
import analysis
import probeSync_qc as probeSync
import data_getters
import logging
import sys
sys.path.append("..")
from sync_dataset import Dataset as sync_dataset

### SPECIFY EXPERIMENT TO PULL ####
#the local base directory
identifier = sys.argv[1]
print(identifier)

d = data_getters.local_data_getter(base_dir=identifier)
paths = d.data_dict

FIG_SAVE_DIR = os.path.join(r"\\allen\programs\braintv\workgroups\nc-ophys\corbettb\NP_behavior_pipeline\QC", 
                            paths['es_id']+'_'+paths['external_specimen_name']+'_'+paths['datestring'])

if not os.path.exists(FIG_SAVE_DIR):
    os.mkdir(FIG_SAVE_DIR)

### GET FILE PATHS TO SYNC AND PKL FILES ###
SYNC_FILE = paths['sync_file']
BEHAVIOR_PKL = paths['behavior_pkl']
REPLAY_PKL = paths['replay_pkl']
MAPPING_PKL = paths['mapping_pkl']
syncDataset = sync_dataset(SYNC_FILE)

print('Grabbing pkl data')
for f,s in zip([SYNC_FILE, BEHAVIOR_PKL, REPLAY_PKL, MAPPING_PKL], ['sync: ', 'behavior: ', 'replay: ', 'mapping: ']):
    print(s)
    print(f)

behavior_data = pd.read_pickle(BEHAVIOR_PKL)
mapping_data = pd.read_pickle(MAPPING_PKL)
replay_data = pd.read_pickle(REPLAY_PKL)


### PLOT FRAME INTERVALS ###
vr, vf = probeSync.get_sync_line_data(syncDataset, channel=2)

behavior_frame_count = behavior_data['items']['behavior']['intervalsms'].size + 1
mapping_frame_count = mapping_data['intervalsms'].size + 1
replay_frame_count = replay_data['intervalsms'].size + 1

MONITOR_LAG = 0.036
FRAME_APPEAR_TIMES = vf + MONITOR_LAG  

### CHECK THAT NO FRAMES WERE DROPPED FROM SYNC ###
total_pkl_frames = (behavior_frame_count +
                    mapping_frame_count +
                    replay_frame_count) 
print('frames in pkl files: {}'.format(total_pkl_frames))
print('frames in sync file: {}'.format(len(vf)))

assert(total_pkl_frames==len(vf))

#%%
### GET UNIT METRICS AND BUILD UNIT TABLE ###
probe_dirs = [[paths['probe'+pid], pid] for pid in paths['data_probes']]
probe_dict = {a[1]:{} for a in probe_dirs}

for p in probe_dirs:
    try:
        print(f'########## stage 1 for probe {p} ###########')
        probe = p[1]
        full_path = p[0]
        
        # Get unit metrics for this probe    
        metrics_file = os.path.join(full_path, 'continuous\\Neuropix-PXI-100.0\\metrics.csv')
        unit_metrics = pd.read_csv(metrics_file)
        unit_metrics = unit_metrics.set_index('cluster_id')
        
        # Get unit data
        units = probeSync.getUnitData(full_path, syncDataset)
        units = pd.DataFrame.from_dict(units, orient='index')
        units['cluster_id'] = units.index.astype(int)
        units = units.set_index('cluster_id')
        
        units = pd.merge(unit_metrics, units, left_index=True, right_index=True, how='outer')
        
        probe_dict[probe] = units
    except Exception as E:
        logging.error(f'################## {p} failed ###############')


### PLOT POPULATION RF FOR EACH PROBE ###
flatten = lambda l: [item[0] for sublist in l for item in sublist]
ctx_units_percentile = 66 #defines what fraction of units we should assume are cortical (taken from top of probe)
for p in probe_dict:
    try:
        print(f'########## stage 2 for probe {p} ###########')
        u_df = probe_dict[p]
        good_units = u_df[(u_df['quality']=='good')&(u_df['snr']>1)]
        #max_chan = good_units['peak_channel'].max()
        # take spikes from the top n channels as proxy for cortex
        #spikes = good_units.loc[good_units['peak_channel']>max_chan-num_channels_to_take_from_top]['times']
        #take spikes from top third of units
        ctx_bottom_chan = np.percentile(good_units['peak_channel'], ctx_units_percentile)
        spikes = good_units.loc[good_units['peak_channel']>ctx_bottom_chan]['times']
        rmats = []
        for s in spikes:
            rmat = analysis.plot_rf(mapping_data, s.flatten(), replay_frame_count, FRAME_APPEAR_TIMES)
            rmats.append(rmat/rmat.max())
            
    #    rmats_normed = np.array([r/r.max() for r in rmats])
        rmats_normed_mean = np.nanmean(rmats, axis=0)
     
        # plot population RF
#        fig, ax = plt.subplots()
#        title = p + ' population RF'
#        fig.suptitle(title)
#        ax.imshow(np.mean(rmats_normed_mean, axis=2), origin='lower')
        
        fig = plt.figure(constrained_layout=True, figsize=[6,6])
        title = p + ' population RF cb'
        fig.suptitle(title, color='w')
        
        nrows, ncols = 10,10
        gs = gridspec.GridSpec(ncols=ncols, nrows=nrows, figure=fig)
        
        ax1 = fig.add_subplot(gs[0:nrows-1, 0:ncols-1])
        ax2 = fig.add_subplot(gs[0:nrows-1, ncols-1])
        ax3 = fig.add_subplot(gs[nrows-1, 0:ncols-1])
        
        ax1.imshow(np.mean(rmats_normed_mean, axis=2), origin='lower')
        ax1.set_xticks([],[])
        ax1.set_yticks([],[])
        
        ax3.imshow(np.vstack((np.arange(-45, 46), np.arange(-45, 46))), cmap='jet', clim=[-60, 60])
        ax3.set_xticks([0, 45, 90])
        ax3.set_xticklabels([-45, 0, 45])
        ax3.set_yticks([],[])
        ax3.set_xlabel('Azimuth')
        
        ax2.imshow(np.hstack((np.arange(-45, 46)[:,None], np.arange(-45, 46)[:,None])), cmap='jet_r', clim=[-60, 60])
        ax2.yaxis.tick_right()
        ax2.set_yticks([0, 45, 90])
        ax2.set_yticklabels([-45, 0, 45])
        ax2.set_xticks([],[])
        ax2.yaxis.set_label_position("right")
        ax2.set_ylabel('Elevation', rotation=270)
        
        fig.savefig(os.path.join(FIG_SAVE_DIR, title + '.png'))
    
    except Exception as E:
        logging.error(f'################## {p} failed ###############')


