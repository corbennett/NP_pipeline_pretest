# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 14:18:35 2020

@author: svc_ccg
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numba import njit
 

def find_spikes_per_trial(spikes, trial_starts, trial_ends):
    tsinds = np.searchsorted(spikes, trial_starts)
    teinds = np.searchsorted(spikes, trial_ends)
    
    return teinds - tsinds

@njit     
def makePSTH_numba(spikes, startTimes, windowDur, binSize=0.001, convolution_kernel=0.05, avg=True):
    spikes = spikes.flatten()
    startTimes = startTimes - convolution_kernel/2
    windowDur = windowDur + convolution_kernel
    bins = np.arange(0,windowDur+binSize,binSize)
    convkernel = np.ones(int(convolution_kernel/binSize))
    counts = np.zeros(bins.size-1)
    for i,start in enumerate(startTimes):
        startInd = np.searchsorted(spikes, start)
        endInd = np.searchsorted(spikes, start+windowDur)
        counts = counts + np.histogram(spikes[startInd:endInd]-start, bins)[0]
    
    counts = counts/startTimes.size
    counts = np.convolve(counts, convkernel)/(binSize*convkernel.size)
    return counts[convkernel.size-1:-convkernel.size], bins[:-convkernel.size-1]

def makePSTH(spikes,startTimes,windowDur,binSize=0.01, avg=True):
    bins = np.arange(0,windowDur+binSize,binSize)
    counts = np.zeros((len(startTimes),bins.size-1))    
    for i,start in enumerate(startTimes):
        counts[i] = np.histogram(spikes[(spikes>=start) & (spikes<=start+windowDur)]-start,bins)[0]
    if avg:
        counts = counts.mean(axis=0)
    counts /= binSize
    return counts


def plot_rf(mapping_pkl_data, spikes, first_frame_offset, frameAppearTimes, resp_latency=0.025, plot=True, returnMat=False):

    
    rfFlashStimDict = mapping_pkl_data
    rfStimParams = rfFlashStimDict['stimuli'][0] 
    rf_pre_blank_frames = int(rfFlashStimDict['pre_blank_sec']*rfFlashStimDict['fps'])
    first_rf_frame = first_frame_offset + rf_pre_blank_frames
    rf_frameTimes = frameAppearTimes[first_rf_frame:]
    rf_trial_start_times = rf_frameTimes[np.array([f[0] for f in np.array(rfStimParams['sweep_frames'])]).astype(np.int)]

    #extract trial stim info (xpos, ypos, ori)
    sweep_table = np.array(rfStimParams['sweep_table'])   #table with rfstim parameters, indexed by sweep order to give stim for each trial
    sweep_order = np.array(rfStimParams['sweep_order'])   #index of stimuli for sweep_table for each trial
    
    trial_xpos = np.array([pos[0] for pos in sweep_table[sweep_order, 0]])
    trial_ypos = np.array([pos[1] for pos in sweep_table[sweep_order, 0]])
    trial_ori = sweep_table[sweep_order, 3]
    
    xpos = np.unique(trial_xpos)
    ypos = np.unique(trial_ypos)
    ori = np.unique(trial_ori)
    
    respInds = tuple([(np.where(ypos==y)[0][0], np.where(xpos==x)[0][0], np.where(ori==o)[0][0]) for (y,x,o) in zip(trial_ypos, trial_xpos, trial_ori)])
    trial_spikes = find_spikes_per_trial(spikes, rf_trial_start_times+resp_latency, rf_trial_start_times+resp_latency+0.2)
    respMat = np.zeros([ypos.size, xpos.size, ori.size])
    for (respInd, tspikes) in zip(respInds, trial_spikes):
        respMat[respInd] += tspikes
    
#    bestOri = np.unravel_index(np.argmax(respMat), respMat.shape)[-1]

    return respMat


def plot_psth_change_flashes(change_times, spikes, preTime = 0.05, postTime = 0.55, sdfSigma=0.005):
    
    sdf, t = makePSTH_numba(spikes,change_times-preTime,preTime+postTime, convolution_kernel=sdfSigma*2)
    
    return sdf, t

def lickTriggeredLFP(lick_times, lfp, lfp_time, agarChRange=None, num_licks=20, windowBefore=0.5, windowAfter=0.5, min_inter_lick_time = 0.5, behavior_duration=3600): 
    first_lick_times = lick_times[np.insert(np.diff(lick_times)>=min_inter_lick_time, 0, True)]
    first_lick_times = first_lick_times[first_lick_times>lfp_time[0]+windowBefore]
    first_lick_times = first_lick_times[:np.min([len(first_lick_times), num_licks])]
    
    probeSampleRate = 1./np.median(np.diff(lfp_time))
    samplesBefore = int(round(windowBefore * probeSampleRate))
    samplesAfter = int(round(windowAfter * probeSampleRate))
    
    last_lick_ind = np.where(lfp_time<=first_lick_times[-1])[0][-1]
    lfp = lfp[:last_lick_ind+samplesAfter+1]
    lfp = lfp - np.mean(lfp, axis=0)[None, :]    

    if agarChRange is not None:
        agar = np.median(lfp[:,agarChRange[0]:agarChRange[1]],axis=1)
        lfp = lfp-agar[:,None]
    
    lickTriggeredAv = np.full([first_lick_times.size, samplesBefore+samplesAfter, lfp.shape[1]], np.nan)
    lick_inds = np.searchsorted(lfp_time, first_lick_times)
    for il, li in enumerate(lick_inds):
       lickTriggeredAv[il, :, :] = lfp[li-samplesBefore:li+samplesAfter] 


    m = np.nanmean(lickTriggeredAv, axis=0)
    mtime = np.linspace(-windowBefore, windowAfter, m.size)  
    return m, mtime, first_lick_times


   
#        lickTriggeredRunning = []
#        rsamplesBefore = int(round(windowBefore * 60))
#        rsamplesAfter = int(round(windowAfter*60))
#        for il, l in enumerate(first_lick_times):
#            if l > runTime[0]:
#                run_lick_ind = np.where(runTime<=l)[0][-1]
#                lta = running[run_lick_ind-rsamplesBefore: run_lick_ind+rsamplesAfter]
#                lickTriggeredRunning.append(lta)
#                
#        r = np.mean(lickTriggeredRunning, axis=0)
#        
#        ax[1].plot(r, 'k')
#        ax[1].axvline(rsamplesBefore, c='k')
#        ax[1].set_xlim([0, r.shape[0]])
#        ax[1].set_ylabel('run speed')