# Programs for Measurement Systems in the Ultrasound Lab
## University of South-Eastern Norway, Vestfold Campus

Collection of small applications to comunicate with and acquire data from the measurement systems in USN's ultrasound laboratory at the Vestfold Campus.
The programs were written over several years using different tools. 

Note that the LabVIEW and Matlab programs will need access to all files in their folders to function.The LabVIEW VIs and Matlab-apps are stand-alone programs with a graphical user interface.
The Matlab functions are to be called from the Matlab console or from antoher Matlab-function.

## Ultrasound Beam Profile Measurements
#### hydrophone-scanning-onda-aims-iii
Acquire and plot pulses from the Onda AIMS III hydrophone system in Matlab
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
|  Scan 2D beam profile of ultrasound transducer | Onda AIMS III | Matlab script | `BeamprofileScan.m` |
| Generate beam profile plots for a colection of measurements | Onda AIMS III | Matlab script | `BatchPlotBeamprofiles`|
| Calculate and plot beam profile in the axial plane (xz or yz) | Onda AIMS III | Matlab script | `PlotBeamshapeAxial`|
| Calculate and plot beam profile in the lateral plane (xy) | Onda AIMS III | Matlab script | `PlotBeamshapeLateral`|
