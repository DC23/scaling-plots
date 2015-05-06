# scaling-plots
Automated strong and weak scaling plots from tabular timing results.
This is not the best or only way to do this, but it suits my needs.
Many aspects of the plots can be controlled through the commmand line arguments.

## Features

* Automatically produce speedup, efficiency (strong and weak), and walltime plots from timing data.
* Multiple rows for the same group and number of compute elements are averaged.
* Rows with missing data are excluded, however missing data handling is poor:
    * no support for mismatched numbers of compute elements.
    * groups missing a baseline 1 compute element entry are not handled gracefully.

## Tabular data requirements

* The tabular data must have a header row.
* Only three columns are required:
    * **group** *(string)*: Indicates a single set of timing results. Also used as the plot labels.
    * **compute_elements** *(int)*: Indicates the number of compute elements used for a particular timing run. 
    * **walltime** *(float)*: Walltime. The units do not matter so long as they
      are consistent. There is a command line argument for supplying the units
      name for use on the plots.
* Other columns can be present, but are ignored.

## To Do

* Scripts that generate the results spreadsheet by parsing the batch system (eg:
  SLURM, PBS) outputs.
