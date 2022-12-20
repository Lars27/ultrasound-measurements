% BatchPlotBeamprofiles

printresult=1;

include.T1600    = 1;
include.T1900    = 1;
include.T11200   = 1;
include.T1impulse= 1;
include.T2600    = 1;
include.T2900    = 1;
include.T21200   = 1;
include.T2impulse= 1;

if include.T1600    
    fc= 600e3;   % Hz   Center frequency
    src= 'wfs_2017_06_21_T1_600kHz_XZ.mat';   PlotBeamshapeAxial(src,fc,'x',0,printresult)
    src= 'wfs_2017_06_21_T1_600kHz_YZ.mat';   PlotBeamshapeAxial(src,fc,'y',0.5,printresult)
    src= 'wfs_2017_06_21_T1_600kHz_XY.mat';   PlotBeamshapeLateral(src,fc,printresult)
end

if include.T1900    
    fc= 900e3;   % Hz   Center frequency
    src= 'wfs_2017_07_03_T1_900kHz_XZ.mat';   PlotBeamshapeAxial(src,fc,'x',0,printresult)
    src= 'wfs_2017_07_03_T1_900kHz_YZ.mat';   PlotBeamshapeAxial(src,fc,'y',0.75,printresult)
    src= 'wfs_2017_07_03_T1_900kHz_XY.mat';   PlotBeamshapeLateral(src,fc,printresult)
end

if include.T11200    
    fc= 1200e3;   % Hz   Center frequency
    src= 'wfs_2017_06_22_T1_1200kHz_XZ.mat';   PlotBeamshapeAxial(src,fc,'x',0,printresult)
    src= 'wfs_2017_06_22_T1_1200kHz_YZ.mat';   PlotBeamshapeAxial(src,fc,'y',0,printresult)
    src= 'wfs_2017_06_22_T1_1200kHz_XY.mat';   PlotBeamshapeLateral(src,fc,printresult)
end

if include.T1impulse
    fc= [400 1800]*1e3;   % Hz  Filter limits frequency
    src= 'wfs_2017_06_26_T1_impulse_XZ.mat';   PlotBeamshapeAxial(src,fc,'x',0,printresult)
    src= 'wfs_2017_06_26_T1_impulse_YZ.mat';   PlotBeamshapeAxial(src,fc,'y',0.5,printresult)
    src= 'wfs_2017_06_26_T1_impulse_XY.mat';   PlotBeamshapeLateral(src,fc,printresult)
end

if include.T2600    
    fc= 600e3;   % Hz   Center frequency
    src= 'wfs_2017_07_06_T2_600kHz_XZ.mat';   PlotBeamshapeAxial(src,fc,'x',0,printresult)
    src= 'wfs_2017_07_06_T2_600kHz_YZ.mat';   PlotBeamshapeAxial(src,fc,'y',1,printresult)
    src= 'wfs_2017_07_06_T2_600kHz_XY.mat';   PlotBeamshapeLateral(src,fc,printresult)
end

if include.T2900    
    fc= 900e3;   % Hz   Center frequency
    src= 'wfs_2017_07_07_T2_900kHz_XZ.mat';   PlotBeamshapeAxial(src,fc,'x',0,printresult)
    src= 'wfs_2017_07_07_T2_900kHz_YZ.mat';   PlotBeamshapeAxial(src,fc,'y',1,printresult)
    src= 'wfs_2017_07_07_T2_900kHz_XY.mat';   PlotBeamshapeLateral(src,fc,printresult)
end

if include.T21200    
    fc= 1200e3;   % Hz   Center frequency
    src= 'wfs_2017_06_27_T2_1200kHz_XZ.mat';   PlotBeamshapeAxial(src,fc,'x',0,printresult)
    src= 'wfs_2017_06_27_T2_1200kHz_YZ.mat';   PlotBeamshapeAxial(src,fc,'y',0.5,printresult)
    src= 'wfs_2017_06_27_T2_1200kHz_XY.mat';   PlotBeamshapeLateral(src,fc,printresult)
end

if include.T2impulse
    fc= [400 1800]*1e3;   % Hz  Filter limits frequency
    src= 'wfs_2017_07_09_T2_impulse_XZ.mat';   PlotBeamshapeAxial(src,fc,'x',0,printresult)
    src= 'wfs_2017_07_09_T2_impulse_YZ.mat';   PlotBeamshapeAxial(src,fc,'y',1,printresult)
    src= 'wfs_2017_07_09_T2_impulse_XY.mat';   PlotBeamshapeLateral(src,fc,printresult)
end

