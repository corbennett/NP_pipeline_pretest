###############################################################################
# DoC Example 15 Seconds.
# @author: derricw
# Jan 16 2017
###############################################################################

from camstim.change import DoCTask, DoCGratingStimulus, DoCTrialGenerator
from camstim import Window, Warp
import logging

# Configure logging level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set up display window
window = Window(fullscr=True, screen=1, monitor='Gamma1.Luminance50', warp=Warp.Spherical)

# Set up Task
params = {
    "stage": "-1_example_stage",
    "task_id": "DoC",
    # rewards (ml),
    "auto_reward_vol": 0.007, # in microliters,
    "volume_limit": 1.5,
    # auto rewards,
    "warm_up_trials": 5, #infinite,
    # trial timing,
    "periodic_flash": None,
    "initial_blank": 0,
    "pre_change_time": 2.25,
    "stimulus_window": 6.0,
    "response_window": [0.15,1.0],
    "max_task_duration_min": 0.25,
}

f = DoCTask(window=window,
            auto_update=True,
            params=params)

t = DoCTrialGenerator(cfg=f.params)  # This also subject to change
f.set_trial_generator(t)

f._early_response_default_handler = lambda *args: None

# Set up our DoC stimulus
obj = DoCGratingStimulus(window,
                         tex='sqr',
                         units='deg',
                         size=(300, 300),
                         sf=0.04,)
                         
obj.add_stimulus_group("group0", 'Ori', [0])
obj.add_stimulus_group("group1", 'Ori', [90])

# Add our DoC stimulus to the Task
f.set_stimulus(obj, "grating")

# Run it
f.start()
