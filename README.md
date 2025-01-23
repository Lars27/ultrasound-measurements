# Programs for Measurement Systems in the Ultrasound Lab
## University of South-Eastern Norway, Vestfold Campus

Collection of small applications to comunicate with and acquire data from the measurement systems in USN's ultrasound laboratory at the Vestfold Campus.
The programs were written over several years using different tools.

The LabVIEW programs are no longer maintained, the Matlab-code is still active, while new developments are done in Python.

Note that the LabVIEW and Matlab programs will need access to all files in their folders to function. The LabVIEW VIs and Matlab app_ are stand-alone programs with a graphical user interface.
The Matlab functions must be called from the Matlab console or from an other Matlab-function.

Details of the individual functions are found in the sub-folders.

## 1) Acquire Ultrasound Pulses. `acquire_ultrasound`

All programs save results to a common in-house defined binary file format called '.wfm'.
These results can be loaded by any of the toos, LabVIEW, Matlab, and Python, using dedicated functions.

a) Matlab - Active, but new developments will be in Python.
b) Python.
c) LabVIEW - No longer maintained

## Ultrasound Beam Profile Measurements
#### hydrophone-scanning-onda-aims-iii
Acquire and plot pulses from the Onda AIMS III hydrophone system in Matlab
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
|  Scan 2D beam profile of ultrasound transducer | Onda AIMS III | Matlab script | `BeamprofileScan.m` |
| Generate beam profile plots for a colection of measurements | Onda AIMS III | Matlab script | `BatchPlotBeamprofiles`|
| Calculate and plot beam profile in the axial plane (xz or yz) | Onda AIMS III | Matlab script | `PlotBeamshapeAxial`|
| Calculate and plot beam profile in the lateral plane (xy) | Onda AIMS III | Matlab script | `PlotBeamshapeLateral`|



## Analyse Results from LynceeTec DHM 2100L Holographic Microscope. `lyncee_dhm_processing`
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
|Create amimation from from digital holography raw data files | Lyncee Tec DHM-R2100L |Matlab | `animate_DHM.m |


## Acquire Impedance Spectra. `acquire_impedance`
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire S-parameter measurements         | Rhode & Schwartz ZVL vector netwotrk analyzer       | LabVIEW project | `Measure Impedance R&S ZVL.lvproj` |
| Example program to load and plot one impedance measurement saved as S11-parameters         | | Matlab-function | `ExamplePlotImpedance.m` |
| Example program to load and plot a group of impedance measurements saved as S11-parameters | | Matlab-function | `ExamplePlotImpedances.m` |
| Read measured data stored as scaled single presicion float (float32)                | | Matlab-function | `readtrace.m`|
| Acquire impedance measurements         | Trewmac TE3100                                       | Python-program | `read_trewmac_gui_continous.py`
| Read electrical impedance spectra stored as scaled single precision float  (float32) |            | Matlab-function | `read_impedance.m` |
