# -*- coding: utf-8 -*-
"""
Created on Wed Aug 08 13:08:37 2018

@author: svc_ccg
"""

from __future__ import division
from matplotlib import pyplot as plt
import ecephys
import pandas as pd
import numpy as np
import glob
import os
import logging


def getUnitData(probeBase,syncDataset):

    probeTTLDir = os.path.join(probeBase, r'events\\Neuropix-PXI-100.0\\TTL_1')
    probeSpikeDir = os.path.join(probeBase, r'continuous\\Neuropix-PXI-100.0')
        
    
    print(probeTTLDir)
    print(probeSpikeDir)
    
    #Get barcodes from sync file
#    if 'barcode' in syncDataset.line_labels:
#        bRising, bFalling = get_sync_line_data(syncDataset, 'barcode')
#    elif 'barcodes' in syncDataset.line_labels:
#        bRising, bFalling = get_sync_line_data(syncDataset, 'barcodes')
    bRising, bFalling = get_sync_line_data(syncDataset, channel=0)
    bs_t, bs = ecephys.extract_barcodes_from_times(bRising, bFalling)
    
    channel_states = np.load(os.path.join(probeTTLDir, 'channel_states.npy'))
    event_times = np.load(os.path.join(probeTTLDir, 'event_timestamps.npy'))
    
    beRising = event_times[channel_states>0]/30000.
    beFalling = event_times[channel_states<0]/30000.
    be_t, be = ecephys.extract_barcodes_from_times(beRising, beFalling)
    
    
    #Compute time shift between ephys and sync
    shift, p_sampleRate, m_endpoints = ecephys.get_probe_time_offset(bs_t, bs, be_t, be, 0, 30000)
    
    
    #Get unit spike times 
    units = load_spike_info(probeSpikeDir, p_sampleRate, shift)
    
    return units

def build_unit_table(probes_to_run, paths, syncDataset):
    ### GET UNIT METRICS AND BUILD UNIT TABLE ###
    probe_dirs = [[paths['probe'+pid], pid] for pid in probes_to_run]
    print(probe_dirs)
    probe_dict = {a[1]:{} for a in probe_dirs}
    
    for p in probe_dirs:
        print(p)
        try:
            print(f'########## Getting Units for probe {p} ###########')
            probe = p[1]
            full_path = p[0]
            
            # Get unit metrics for this probe    
            metrics_file = os.path.join(full_path, 'continuous\\Neuropix-PXI-100.0\\metrics.csv')
            unit_metrics = pd.read_csv(metrics_file)
            unit_metrics = unit_metrics.set_index('cluster_id')
            
            # Get unit data
            units = getUnitData(full_path, syncDataset)
            units = pd.DataFrame.from_dict(units, orient='index')
            units['cluster_id'] = units.index.astype(int)
            units = units.set_index('cluster_id')
            
            units = pd.merge(unit_metrics, units, left_index=True, right_index=True, how='outer')
            
            probe_dict[probe] = units
            
        except Exception as E:
            logging.error(E)
        
        
    return probe_dict
            

    
def get_sync_line_data(syncDataset, line_label=None, channel=None):
    ''' Get rising and falling edge times for a particular line from the sync h5 file
        
        Parameters
        ----------
        dataset: sync file dataset generated by sync.Dataset
        line_label: string specifying which line to read, if that line was labelled during acquisition
        channel: integer specifying which channel to read in line wasn't labelled
        
        Returns
        ----------
        rising: npy array with rising edge times for specified line
        falling: falling edge times
    '''
    if isinstance(line_label, str):
        try:
            channel = syncDataset.line_labels.index(line_label)
        except:
            print('Invalid line label')
            return
    elif channel is None:
        print('Must specify either line label or channel id')
        return
    
    sample_freq = syncDataset.meta_data['ni_daq']['counter_output_freq']
    rising = syncDataset.get_rising_edges(channel)/sample_freq
    falling = syncDataset.get_falling_edges(channel)/sample_freq
    
    return rising, falling


def load_spike_info(spike_data_dir, p_sampleRate, shift):
    ''' Make dictionary with spike times, templates, sorting label and peak channel for all units
    
        Parameters
        -----------
        spike_data_dir: path to directory with clustering output files
        p_sampleRate: probe sampling rate according to master clock
        shift: time shift between master and probe clock
        p_sampleRate and shift are outputs from 'get_probe_time_offset' function
        sortMode: if KS, read in automatically generated labels from Kilosort; if phy read in phy labels
        
        Returns
        ----------
        units: dictionary with spike info for all units
            each unit is integer key, so units[0] is a dictionary for spike cluster 0 with keys
            'label': sorting label for unit, eg 'good', 'mua', or 'noise'
            'times': spike times in seconds according to master clock
            'template': spike template, should be replaced by waveform extracted from raw data
                averaged over 1000 randomly chosen spikes
            'peakChan': channel where spike template has minimum, used to approximate unit location
    '''
    print(p_sampleRate)
    print(shift)
    spike_clusters = np.load(os.path.join(spike_data_dir, 'spike_clusters.npy'))
    spike_times = np.load(os.path.join(spike_data_dir, 'spike_times.npy'))
    templates = np.load(os.path.join(spike_data_dir, 'templates.npy'))
    spike_templates = np.load(os.path.join(spike_data_dir, 'spike_templates.npy'))
    channel_positions = np.load(os.path.join(spike_data_dir, 'channel_positions.npy'))
    amplitudes = np.load(os.path.join(spike_data_dir, 'amplitudes.npy'))
    unit_ids = np.unique(spike_clusters)
    
    units = {}
    for u in unit_ids:
        ukey = str(u)
        units[ukey] = {}
    
        unit_idx = np.where(spike_clusters==u)[0]
        unit_sp_times = spike_times[unit_idx]/p_sampleRate - shift
        
        units[ukey]['times'] = unit_sp_times
        
        #choose 1000 spikes with replacement, then average their templates together
        chosen_spikes = np.random.choice(unit_idx, 1000)
        chosen_templates = spike_templates[chosen_spikes].flatten()
        units[ukey]['template'] = np.mean(templates[chosen_templates], axis=0)
        units[ukey]['peakChan'] = np.unravel_index(np.argmin(units[ukey]['template']), units[ukey]['template'].shape)[1]
        units[ukey]['position'] = channel_positions[units[ukey]['peakChan']]
        units[ukey]['amplitudes'] = amplitudes[unit_idx]
        
#        #check if this unit is noise
#        peakChan = units[ukey]['peakChan']
#        temp = units[ukey]['template'][:, peakChan]
#        pt = findPeakToTrough(temp, plot=False)
#        units[ukey]['peakToTrough'] = pt

        
    return units
    
    
def getLFPData(probeBase, syncDataset, num_channels=384):
    
    probeTTLDir = os.path.join(probeBase, r'events\\Neuropix-PXI-100.0\\TTL_1')
    lfp_data_dir = os.path.join(probeBase, r'continuous\\Neuropix-PXI-100.1')
    lfp_data_file = os.path.join(lfp_data_dir, 'continuous.dat')
    
    
    if not os.path.exists(lfp_data_file):
        print('Could not find LFP data at ' + lfp_data_file)
        return None,None
    
    lfp_data = np.memmap(lfp_data_file, dtype='int16', mode='r')    
    lfp_data_reshape = np.reshape(lfp_data, [int(lfp_data.size/num_channels), -1])
    time_stamps = np.load(os.path.join(lfp_data_dir, 'lfp_timestamps.npy'))
        
    
    #Get barcodes from sync file
#    if 'barcode' in syncDataset.line_labels:
#        bRising, bFalling = get_sync_line_data(syncDataset, 'barcode')
#    elif 'barcodes' in syncDataset.line_labels:
#        bRising, bFalling = get_sync_line_data(syncDataset, 'barcodes')
    bRising, bFalling = get_sync_line_data(syncDataset, channel=0)
    bs_t, bs = ecephys.extract_barcodes_from_times(bRising, bFalling)
    
    channel_states = np.load(os.path.join(probeTTLDir, 'channel_states.npy'))
    event_times = np.load(os.path.join(probeTTLDir, 'event_timestamps.npy'))
    
    beRising = event_times[channel_states>0]/30000.
    beFalling = event_times[channel_states<0]/30000.
    be_t, be = ecephys.extract_barcodes_from_times(beRising, beFalling)
    
    
    #Compute time shift between ephys and sync
    shift, p_sampleRate, m_endpoints = ecephys.get_probe_time_offset(bs_t, bs, be_t, be, 0, 30000)
    
    
    time_stamps_shifted = (time_stamps/p_sampleRate) - shift
    
    return lfp_data_reshape, time_stamps_shifted


