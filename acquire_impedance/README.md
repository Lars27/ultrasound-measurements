# Programs for Measurement Systems in the Ultrasound Lab
## University of South-Eastern Norway, Vestfold Campus

Collection of small applications to comunicate with and acquire data from the measurement systems in USN's ultrasound laboratory at the Vestfold Campus.
The programs were written over several years using different tools. 

Note that the LabVIEW and Matlab programs will need access to all files in their folders to function.The LabVIEW VIs and Matlab-apps are stand-alone programs with a graphical user interface.
The Matlab functions are to be called from the Matlab console or from antoher Matlab-function.

## Acquire Impedance Spectra. `acquire_impedance`
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire S-parameter measurements         | Rhode & Schwartz ZVL vector netwotrk analyzer       | LabVIEW project | `Measure Impedance R&S ZVL.lvproj` |
| Example program to load and plot one impedance measurement saved as S11-parameters         | | Matlab-function | `ExamplePlotImpedance.m` |
| Example program to load and plot a group of impedance measurements saved as S11-parameters | | Matlab-function | `ExamplePlotImpedances.m` |
| Read measured data stored as scaled single presicion float (float32)                | | Matlab-function | `readtrace.m`|
| Acquire impedance measurements         | Trewmac TE3100                                       | Python-program | `read_trewmac_gui_continous.py`
| Read electrical impedance spectra stored as scaled single precision float  (float32) |            | Matlab-function | `read_impedance.m` |
