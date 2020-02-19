# NP_pipeline_pretest
Validation functions to run after the pretest on NP pipeline rigs to verify that all data streams are being collected. The pretest should output a sync file (hdf5) and a pkl file (DOC format). 

Dependencies: 
  * numpy
  * pandas
  * json
  * h5py  

The validation functions can be run from the command line:
```
python run_validation_functions.py path_to_json_params path_to_results_save_file
```

The params file includes:
1. path to sync file
2. path to pkl file
3. list of QC functions to run along with their respective criteria
4. relevant line labels for sync


Check out the example to see how this is formatted.

The output is a json file saved to the path specified by the second command line argument. The file will specify which validation functions were called and whether they passed (1) or failed (0).

I've also included a short pretest camstim script (example_DOC_short) that outputs the right pkl file format.



