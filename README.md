# NP_pipeline_pretest
Validation functions to run after the pretest on NP pipeline rigs to verify that all data streams are being collected. 
Dependencies: 
  * numpy
  * pandas
  * json
  * h5py  

The validation functions can be run from the command line:
```
python run_validation_functions.py params.json results.json
```
**params.json** should contain the following fields:
* 'file_paths' : dictionary specifying paths to the data streams required for QC (sync file, pkl file, behavior videos etc)
* 'functions_to_run': list containing a dictionary for every QC function that should be run on pretest data. These dictionaries contain the following keys:
  * 'function': name of function to run (should be one of the functions in the pretest_validation_functions.py file)
  * 'args' : kwargs for the function specifying various parameters like the sync line labels and QC criteria
  * 'data_stream' : which data stream this function validates (sync file, pkl file, behavior video etc)
  * 'output_name' : the name under which the results from this function will appear in the final results.json
  
Check out the example_make_params_json.py to see how this is formatted more clearly.

**results.json** will contain the outputs from these validation functions. The file will specify which validation functions were called and whether they passed (1) or failed (0).

I've also included a short pretest camstim script (example_DOC_short) that outputs the right pkl file format and can be used for the pretest.



