# Programs for Measurement Systems in the Ultrasound Lab
## University of South-Eastern Norway, Vestfold Campus

Collection of small applications to comunicate with and acquire data from the measurement systems in USN's ultrasound laboratory at the Vestfold Campus.
The programs were written over several years using different tools. 

Note that the LabVIEW and Matlab programs will need access to all files in their folders to function.The LabVIEW VIs and Matlab-apps are stand-alone programs with a graphical user interface.
The Matlab functions are to be called from the Matlab console or from antoher Matlab-function.


## Acquire Ultrasound Pulses

#### Acquire_Ultrasound_LabVIEW
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire and display ultrasound pulses | National Instruments high-speed data acquisition boards (NI Scope)  | LabVIEW project | `Aquire Ultrasound.lvproj` |
| Load, analyse, and display aquired ultrasound pulses | Any                                                  | Matlab function, example | `ExamplePlotWaveform.m`|   

#### acquire_ultrasound_matlab_app
| Description |  Hardware | Type | Function Name | 
| -- | -- | -- | -- | 
| Acquire and display ultrasound pulses. Save result to Matlab .mat-file   | PicoScope 5000  | Matlab-app       | `AcquirePulses_Picoscope5000a.mlapp` |
| Acquire and display ultrasound pulses. Save result to binary file (wfm)  | PicoScope 5000  | Matlab-app       | `AcquirePulses_Picoscope5000a_wfm.mlapp` |
| Load measured ultrasound pulses from binary file (wfm)                   |                 | Matlab-function  | `readwfm.m`|

#### acquire_ultrasound_python 
Porting of the Matlab-apps for PicoScope 5000 to Python. Work in progress
