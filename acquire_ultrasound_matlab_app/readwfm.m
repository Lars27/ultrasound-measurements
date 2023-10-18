function wfm= readwfm(wfmfile)
% function wfm= readwfm(wfmfile)
%
% Read measured data stored as scaled single precicion float values
% Inspired by LabVIEW's 'waveform' format (wfm)
%
% This function is not suitable for very large recordings, as all results
% from the raw data file are into memory at once
% 
%
% Data storage structure:
%
% header: Short text identifying measurement type
%      N: [u32]  Number of data channels 
%     t0: [dbl]  Start time of measurement, seconds following LabVIEW's standard
%     dt: [dbl]  Sample interval [s]
%    dtr: [dbl]  Not used in this configuration, otherwise interval between records
%    eoh: [dbl]  'End of header'. File position where  header ends and
%                recorded data points start
%      v: [sgl]  Recorded data values, as scaled by recording program
%     Np: [dbl]  No. of sample points per channel
%

% Lars Hoff, HiVe, March 2011

src = fopen (wfmfile,'rb','ieee-be');   % Data stored in 'IEEE big-endian' format, ref. LabVIEW

%Read header
Nhd = fread(src, 1, 'int32');                     % Read header
wfm.header = readstring(src, Nhd);
wfm.N      = fread(src, 1, 'uint32');
wfm.t0     = fread(src, 1, 'float64');
wfm.dt     = fread(src, 1, 'float64');
wfm.dtr    = fread(src, 1, 'float64');
wfm.eoh    = ftell(src);                           % Register where header ends and data starts
wfm.v      = fread(src, [wfm.N inf], '*float32');  % Read all data in once

wfm.v = wfm.v';
wfm.Np= max(size(wfm.v));

fclose(src);

return

%=== Internal functions ===
function s= readstring(src,n)
ns= fread(src, n, '*uchar');
s = char(ns');
return
