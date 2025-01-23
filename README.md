# Programs for Measurement Systems in the Ultrasound Lab
## University of South-Eastern Norway, Vestfold Campus

Collection of small applications to comunicate with and acquire data from the measurement systems in USN's ultrasound laboratory at the Vestfold Campus.
The programs were written over several years using different tools. 

Note that the LabVIEW and Matlab programs will need access to all files in their folders to function.The LabVIEW VIs and Matlab-apps are stand-alone programs with a graphical user interface.
The Matlab functions are to be called from the Matlab console or from antoher Matlab-function.


## Acquire Ultrasound Pulses

All programs save results to a common in-house defined binary file format called '.wfm'.
These results can be loaded by any of the toos, LabVIEW, Matlab, and Python, using dedicated functions.

#### Matlab - Active, but new developments will be in Python.
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire and display ultrasound pulses. Save result to Matlab .mat-file   | PicoScope 5000  | Matlab-app       | `AcquirePulses_Picoscope5000a.mlapp` |
| Acquire and display ultrasound pulses. Save result to binary file (wfm)  | PicoScope 5000  | Matlab-app       | `AcquirePulses_Picoscope5000a_wfm.mlapp` |
| Load measured ultrasound pulses from binary file (wfm)                   |                 | Matlab-function  | `readwfm.m`|

#### Python.
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire and display ultrasound pulses. Save result to binary file (wfm) | PicoScope 5000 |  Python with GUI  | `acquire_ultrasound.py` |
| Acquire and display ultrasound pulses. Save result to binary file (wfm) | PicoScope 5000 |  Python script    | `acquire_ultrasound_raw_ps5000a.py` |
| Acquire and display ultrasound pulses. Save result to binary file (wfm) | PicoScope 2000 |  Python script    | `acquire_ultrasound_raw_ps2000a.py` |
| Wrappers for c-type functions to interact with instrument from  from Python | PicoScope 5000 |  Python class | `ps5000a_ultrasound_wrappers.py` |
| Wrappers for c-type functions to interact with instrument from  from Python | PicoScope 2000 |  Python class | `ps2000a_ultrasound_wrappers.py` |
| Collection of functions to alalyse and plot the ultrasound results.         |                | Python class  | `ultrasound_utilities.py` |  

### LabVIEW - No longer maintained
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire and display ultrasound pulses | National Instruments high-speed data acquisition boards (NI Scope)  | LabVIEW project | `Aquire Ultrasound.lvproj` |
| Load, analyse, and display aquired ultrasound pulses | Any                                                  | Matlab function, example | `ExamplePlotWaveform.m`|   

## Ultrasound Beam Profile Measurements
#### hydrophone-scanning-onda-aims-iii
Acquire and plot pulses from the Onda AIMS III hydrophone system in Matlab
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
|  Scan 2D beam profile of ultrasound transducer | Onda AIMS III | Matlab script | `BeamprofileScan.m` |
| Generate beam profile plots for a colection of measurements | Onda AIMS III | Matlab script | `BatchPlotBeamprofiles`|
| Calculate and plot beam profile in the axial plane (xz or yz) | Onda AIMS III | Matlab script | `PlotBeamshapeAxial`|
| Calculate and plot beam profile in the lateral plane (xy) | Onda AIMS III | Matlab script | `PlotBeamshapeLateral`|





## Analyse Results from LynceeTec DHM 2100L Holographic Microscope
#### lyncee_dhm_processing
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
|Create amimation from from digital holography raw data files | Lyncee Tec DHM-R2100L |Matlab | `animate_DHM.m |


## Acquire Impedance Spectra
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire S-parameter measurements         | Rhode & Schwartz ZVL vector netwotrk analyzer       | LabVIEW project | `Measure Impedance R&S ZVL.lvproj` |
| Example program to load and plot one impedance measurement saved as S11-parameters         | | Matlab-function | `ExamplePlotImpedance.m` |
| Example program to load and plot a group of impedance measurements saved as S11-parameters | | Matlab-function | `ExamplePlotImpedances.m` |
| Read measured data stored as scaled single presicion float (float32)                | | Matlab-function | `readtrace.m`|
| Acquire impedance measurements         | Trewmac TE3100                                       | Python-program | `read_trewmac_gui_continous.py`
| Read electrical impedance spectra stored as scaled single precision float  (float32) |            | Matlab-function | `read_impedance.m` |
