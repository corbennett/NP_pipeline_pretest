# NP_pipeline_pretest
validation functions to run before NP data collection

dependencies: 
  numpy
  pandas
  json
  h5py  

Run on command line:
```
python run_validation_functions.py path_to_json_params path_to_results_save_directory
```

The params file should include paths to 
1. sync hdf5 file
2. foraging2 pkl file in the DOC format

Other params specify the sync line labels and QC criteria for each QC function. 
