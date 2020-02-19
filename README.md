# NP_pipeline_pretest
Validation functions to run after the pretest on NP pipeline rigs. The pretest should output a sync file (hdf5) and a pkl file (DOC format). 

Dependencies: 
  * numpy
  * pandas
  * json
  * h5py  

The validation functions can be run from the command line:
```
python run_validation_functions.py path_to_json_params path_to_results_save_directory
```

The params file includes:
1. path to sync file
2. path to pkl file
3. line labels for sync
4. criteria for each QC function

Check out the example to see how this is formatted.

The output is a json file saved to the path specified by the second command line argument. The file will specify which validation functions were called and whether they passed (1) or failed (0).
