# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 12:15:38 2020

@author: svc_ccg
"""
from psycopg2 import connect, extras
import numpy as np
import os, glob, shutil
from visual_behavior.visualization.extended_trials.daily import make_daily_figure
from visual_behavior.translator.core import create_extended_dataframe
from visual_behavior.translator.foraging2 import data_to_change_detection_core
from visual_behavior.ophys.sync import sync_dataset
import visual_behavior
import pandas as pd
from matplotlib import pyplot as plt
import analysis
import probeSync_qc as probeSync
import scipy.signal
import cv2
import data_getters

### SPECIFY EXPERIMENT TO PULL ####
#this should be either the ten digit lims id:
#identifier = '1013651431' #lims id
#or the local base directory
identifier = r'\\10.128.50.43\sd6.3\1030489628_498756_20200617' 


if identifier.find('_')>=0:
    d = data_getters.local_data_getter(base_dir=identifier)
else:
    d = data_getters.lims_data_getter(exp_id=identifier)

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

syncDataset = sync_dataset.Dataset(SYNC_FILE)

for f,s in zip([SYNC_FILE, BEHAVIOR_PKL, REPLAY_PKL, MAPPING_PKL], ['sync: ', 'behavior: ', 'replay: ', 'mapping: ']):
    print(s + f)


### MAKE DAILY BEHAVIOR PLOT ###
behavior_data = pd.read_pickle(BEHAVIOR_PKL)
core_data = data_to_change_detection_core(behavior_data)
trials = create_extended_dataframe(
    trials=core_data['trials'],
    metadata=core_data['metadata'],
    licks=core_data['licks'],
    time=core_data['time'])

mapping_data = pd.read_pickle(MAPPING_PKL)
replay_data = pd.read_pickle(REPLAY_PKL)

daily_behavior_fig = make_daily_figure(trials)
daily_behavior_fig.savefig(os.path.join(FIG_SAVE_DIR, 'behavior_summary.png'))


### PLOT FRAME INTERVALS ###
vr, vf = probeSync.get_sync_line_data(syncDataset, channel=2)

fig, ax = plt.subplots()
ax.plot(np.diff(vf))
ax.set_ylim([0, 0.2])

behavior_frame_count = len(core_data['time'])
mapping_frame_count = mapping_data['intervalsms'].size + 1
replay_frame_count = replay_data['intervalsms'].size + 1
ax.plot(behavior_frame_count, 0.15, 'ko')

expected_break_2 = behavior_frame_count + mapping_data['intervalsms'].size
ax.plot(expected_break_2, 0.15, 'ko')
ax.set_xlabel('frames')
ax.set_ylabel('interval, s (capped at 0.2)')

# TODO add count of frames over some threshold

fig.savefig(os.path.join(FIG_SAVE_DIR, 'vsync_intervals.png'))

MONITOR_LAG = 0.036
FRAME_APPEAR_TIMES = vf + MONITOR_LAG  

### CHECK THAT NO FRAMES WERE DROPPED FROM SYNC ###
total_pkl_frames = (behavior_frame_count +
                    mapping_frame_count +
                    replay_frame_count) 

assert(total_pkl_frames == len(vf))

# TODO get images from LIMS
### GET PROBE INSERTION IMAGE ###
#insertion_image = glob.glob(os.path.join(sync_pkl_dir, '*insertionLocation.png'))[0]
#shutil.copyfile(insertion_image, os.path.join(FIG_SAVE_DIR, os.path.basename(insertion_image)))

### GET UNIT METRICS AND BUILD UNIT TABLE ###
probe_dirs = [[paths['probe'+pid], pid] for pid in paths['data_probes']]
probe_dict = {a[1]:{} for a in probe_dirs}

for p in probe_dirs:
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


### PLOT POPULATION RF FOR EACH PROBE ###
flatten = lambda l: [item[0] for sublist in l for item in sublist]
ctx_units_percentile = 66 #defines what fraction of units we should assume are cortical (taken from top of probe)
for p in probe_dict:
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
        rmat = analysis.plot_rf(mapping_data, s.flatten(), behavior_frame_count, FRAME_APPEAR_TIMES)
        rmats.append(rmat/rmat.max())
        
#    rmats_normed = np.array([r/r.max() for r in rmats])
    rmats_normed_mean = np.nanmean(rmats, axis=0)
 
    # plot population RF
    fig, ax = plt.subplots()
    title = p + ' population RF'
    fig.suptitle(title)
    ax.imshow(np.mean(rmats_normed_mean, axis=2), origin='lower')
    
    fig.savefig(os.path.join(FIG_SAVE_DIR, title + '.png'))
    


### PLOT IMAGE RESPONSE FOR EACH PROBE ###
probe_color_dict = {'A': 'orange',
                    'B': 'r',
                    'C': 'k',
                    'D': 'g',
                    'E': 'b',
                    'F': 'm'}
change_frames = np.array(trials['change_frame'].dropna()).astype(int)+1
active_change_times = FRAME_APPEAR_TIMES[change_frames]
first_passive_frame = behavior_data['items']['behavior']['intervalsms'].size + mapping_data['intervalsms'].size + 2
passive_change_times = FRAME_APPEAR_TIMES[first_passive_frame:][change_frames]

lfig, lax = plt.subplots()
preTime = 0.05
postTime = 0.55
for p in probe_dict:
    u_df = probe_dict[p]
    good_units = u_df[(u_df['quality']=='good')&(u_df['snr']>1)]
#    max_chan = good_units['peak_channel'].max()
#    # take spikes from the top n channels as proxy for cortex
#    spikes = good_units.loc[good_units['peak_channel']>max_chan-num_channels_to_take_from_top]['times']
    ctx_bottom_chan = np.percentile(good_units['peak_channel'], ctx_units_percentile)
    spikes = good_units.loc[good_units['peak_channel']>ctx_bottom_chan]['times']
    sdfs = [[],[]]
    for s in spikes:
        s = s.flatten()
        if s.size>3600:
            for icts, cts in enumerate([active_change_times, passive_change_times]): 
                sdf,t = analysis.plot_psth_change_flashes(cts, s, preTime=preTime, postTime=postTime)
                sdfs[icts].append(sdf)
 
    # plot population change response
    fig, ax = plt.subplots()
    title = p + ' population change response'
    fig.suptitle(title)
    ax.plot(t, np.mean(sdfs[0], axis=0), 'k')
    ax.plot(t, np.mean(sdfs[1], axis=0), 'g')
    ax.legend(['active', 'passive'])
    ax.axvline(preTime, c='k')
    ax.axvline(preTime+0.25, c='k')
    ax.set_xticks(np.arange(0, preTime+postTime, 0.05))
    ax.set_xticklabels(np.round(np.arange(-preTime, postTime, 0.05), decimals=2))
    ax.set_xlabel('Time from change (s)')
    ax.set_ylabel('Mean population response')
    fig.savefig(os.path.join(FIG_SAVE_DIR, title + '.png'))
    
    mean_active = np.mean(sdfs[0], axis=0)
    mean_active_baseline = mean_active[:int(preTime*1000)].mean()
    baseline_subtracted = mean_active - mean_active_baseline
    lax.plot(t, baseline_subtracted/baseline_subtracted.max(), c=probe_color_dict[p])
    
lax.legend(probe_dict.keys())
lax.set_xlim([preTime, preTime+0.1])
lax.set_xticks(np.arange(preTime, preTime+0.1, 0.02))
lax.set_xticklabels(np.arange(0, 0.1, 0.02))
lax.set_xlabel('Time from change (s)')
lax.set_ylabel('Normalized response')
lfig.savefig(os.path.join(FIG_SAVE_DIR, 'pop_change_response_latency_comparison.png'))


### Plot Running Wheel Data ###
active_wheel = scipy.signal.medfilt(behavior_data['items']['behavior']['encoders'][0]['dx'], 5)

rfig, rax = plt.subplots()
rfig.set_size_inches(12, 4)
rfig.suptitle('Running')
time_offset = 0
colors = ['k', 'g', 'r']
for ri, rpkl in enumerate([behavior_data, mapping_data, replay_data]):
    key = 'behavior' if 'behavior' in rpkl['items'] else 'foraging'
    intervals = rpkl['items']['behavior']['intervalsms'] if 'behavior' in rpkl['items'] else rpkl['intervalsms']
    time = np.insert(np.cumsum(intervals), 0, 0)/1000.
    
    dx,vsig,vin = [rpkl['items'][key]['encoders'][0][rkey] for rkey in ('dx','vsig','vin')]
    
    run_speed = visual_behavior.analyze.compute_running_speed(dx[:len(time)],time,vsig[:len(time)],vin[:len(time)])
    rax.plot(time+time_offset, run_speed, colors[ri])
    time_offset = time_offset + time[-1]
    
rax.set_xlabel('Time (s)')
rax.set_ylabel('Run Speed (cm/s)')
rax.legend(['active', 'mapping', 'passive'])
rfig.savefig(os.path.join(FIG_SAVE_DIR, 'run_speed.png'))

### Lick triggered LFP ###
lick_times = probeSync.get_sync_line_data(syncDataset, channel=31)[0]

lfp_dict = {}
for p in probe_dirs:
    base = p[0]
    print(p)
    #ld = os.path.join(p, 'continuous\\Neuropix-PXI-100.1')
    lfp, time = probeSync.getLFPData(base, syncDataset)
    lfp_dict[p[1]] = {'time': time, 'lfp': lfp}
    
for p in lfp_dict:
    winBefore = 0.5
    winAfter = 1.5
    plfp = lfp_dict[p]['lfp']
    lta, ltime, first_lick_times = analysis.lickTriggeredLFP(lick_times, plfp, lfp_dict[p]['time'], 
                                           agarChRange=[325, 350], num_licks=20, windowBefore=winBefore,
                                           windowAfter=winAfter, min_inter_lick_time=0.5)
    
    fig, axes = plt.subplots(2,1)
    fig.suptitle(p + ' Lick-triggered LFP, ' + str(len(first_lick_times)) + ' lick bouts')
    axes[0].imshow(lta.T, aspect='auto')
    axes[1].plot(np.mean(lta, axis=1), 'k')
    for a in axes:
        a.set_xticks(np.arange(0, winBefore+winAfter, winBefore)*2500)
        a.set_xticklabels(np.round(np.arange(-winBefore, winAfter, winBefore), decimals=2))
        
    axes[1].set_xlim(axes[0].get_xlim())
    axes[0].tick_params(bottom=False, labelbottom=False)
    axes[1].set_xlabel('Time from lick bout (s)')
    axes[0].set_ylabel('channel')
    axes[1].set_ylabel('Mean across channels')
    fig.savefig(os.path.join(FIG_SAVE_DIR, 'Probe' + p + ' lick-triggered LFP'))

### histogram of spikes over entire session ###
for p in probe_dict:
    u_df = probe_dict[p]
    good_units = u_df[(u_df['quality']=='good')&(u_df['snr']>1)]
    
    spikes = flatten(good_units['times'].to_list())
    binwidth = 1
    bins = np.arange(0, np.max(spikes), binwidth)
    hist, bin_e = np.histogram(spikes, bins)
    
    fig, ax = plt.subplots()
    fig.suptitle('spike histogram (good units), Probe ' + p)
    ax.plot(bin_e[:-1], hist)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Spike Count per ' + str(binwidth) + ' second bin')
    fig.savefig(os.path.join(FIG_SAVE_DIR, 'Probe' + p + ' spike histogram'))
    
### frames from videos ###
def get_video_file(glob_string, directory):
    paths = glob.glob(os.path.join(directory, glob_string))
    if len(paths)>0:
        return paths[-1]
    else:
        return None
    
BODY_VID_FILE = get_video_file('*behavior*.avi', sync_pkl_dir)
EYE_VID_FILE = get_video_file('*eye*.avi', sync_pkl_dir)
FACE_VID_FILE = get_video_file('*face*.avi', sync_pkl_dir)

vids = [v for v in [BODY_VID_FILE, EYE_VID_FILE, FACE_VID_FILE] if v is not None]
fig, axes = plt.subplots(len(vids), 3)
for iv, vid in enumerate(vids):
    v = cv2.VideoCapture(vid)
    total_frames = v.get(cv2.CAP_PROP_FRAME_COUNT)
    
    for 
        
        
        
        
        
        
        
### unit quantification ###

###
    
    
    
