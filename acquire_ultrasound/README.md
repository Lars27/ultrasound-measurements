# Programs for Measurement Systems in the Ultrasound Lab
## University of South-Eastern Norway, Vestfold Campus

Collection of small applications to comunicate with and acquire data from the measurement systems in USN's ultrasound laboratory at the Vestfold Campus.
The programs were written over several years using different tools. 

Note that the LabVIEW and Matlab programs will need access to all files in their folders to function.The LabVIEW VIs and Matlab-apps are stand-alone programs with a graphical user interface.
The Matlab functions are to be called from the Matlab console or from antoher Matlab-function.


## Acquire Ultrasound Pulses. `acquire_ultrasound`

All programs save results to a common in-house defined binary file format called '.wfm'.
These results can be loaded by any of the toos, LabVIEW, Matlab, and Python, using dedicated functions.

### Matlab - Active, but new developments will be in Python.
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire and display ultrasound pulses. Save result to Matlab .mat-file   | PicoScope 5000  | Matlab-app       | `AcquirePulses_Picoscope5000a.mlapp` |
| Acquire and display ultrasound pulses. Save result to binary file (wfm)  | PicoScope 5000  | Matlab-app       | `AcquirePulses_Picoscope5000a_wfm.mlapp` |
| Load measured ultrasound pulses from binary file (wfm)                   |                 | Matlab-function  | `readwfm.m`|

### Python.
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire and display ultrasound pulses. Save result to binary file (wfm) | PicoScope 5000 |  Python with GUI  | `acquire_ultrasound.py` |
| Acquire and display ultrasound pulses. Save result to binary file (wfm) | PicoScope 5000 |  Python script    | `acquire_ultrasound_raw_ps5000a.py` |
| Acquire and display ultrasound pulses. Save result to binary file (wfm) | PicoScope 2000 |  Python script    | `acquire_ultrasound_raw_ps2000a.py` |
| Wrappers for c-type functions to interact with instrument from  from Python | PicoScope 5000 |  Python class | `ps5000a_ultrasound_wrappers.py` |
| Wrappers for c-type functions to interact with instrument from  from Python | PicoScope 2000 |  Python class | `ps2000a_ultrasound_wrappers.py` |
| Collection of functions to alalyse and plot the ultrasound results.         |                | Python class  | `ultrasound_utilities.py` |  

## LabVIEW - No longer maintained
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire and display ultrasound pulses | National Instruments high-speed data acquisition boards (NI Scope)  | LabVIEW project | `Aquire Ultrasound.lvproj` |
| Load, analyse, and display aquired ultrasound pulses | Any                                                  | Matlab function, example | `ExamplePlotWaveform.m`|   
