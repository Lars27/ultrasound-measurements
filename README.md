# Programs for Measurement Systems in the Ultrasound Lab
## University of South-Eastern Norway, Vestfold Campus

Collection of small applications to comunicate with and acquire data from the measurement systems in USN's ultrasound laboratory at the Vestfold Campus.
The programs were written over several years using different tools.

The LabVIEW programs are no longer maintained, the Matlab-code is still active, while new developments are done in Python.

Note that the LabVIEW and Matlab programs will need access to all files in their folders to function. The LabVIEW VIs and Matlab app_ are stand-alone programs with a graphical user interface.
The Matlab functions must be called from the Matlab console or from an other Matlab-function.

Details of the individual functions are found in the sub-folders.

1. **Acquire Ultrasound Pulses** `acquire_ultrasound`
All programs save results to a common in-house defined binary file format called '.wfm'.
These results can be loaded by into LabVIEW, Matlab, and Python using dedicated functions, independent of which program generated the file.
   1. Matlab - Active, but new developments will be in Python.
   1. Python.
   1. LabVIEW - No longer maintained

1. **Ultrasound Beam Profile Measurements** `hydrophone-scanning-onda-aims-iii` 
Acquire and plot pulses from the Onda AIMS III hydrophone system in Matlab

1. **Analyse Results from LynceeTec DHM 2100L Holographic Microscope** `lyncee_dhm_processing`

1. **Acquire Impedance Spectra** `acquire_impedance`. Aquire impedance data from a network analyser or impedance analyser, save to file, and plot results.
