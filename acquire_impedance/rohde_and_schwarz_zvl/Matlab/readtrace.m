function trace= readtrace(tracefile)
% function trace= readtrace(tracefile)
%
% Read measured data stored as scaled single precicion float values
% Inspired by LabVIEW's 'waveform' format (wfm)
%
% This function is not suitable for very large recordings, as all results
% from the raw data file are into memory at once
% 
% Data storage structure:
%
% header: Short text identifying measurement type
%     Nc: [u32]  Number of data channels 
%     x0: [dbl]  Start value
%     dx: [dbl]  Interval between samples (Must be fixed)
%    eoh: [dbl]  'End of header'. File position where  header ends and
%                recorded data points start
%      y: [sgl]  Recorded data values, as scaled by recording program
%     Np: [dbl]  No. of sample points per channel
%

% Lars Hoff, HiVe, March 2011

src = fopen (tracefile,'rb','ieee-be');   % Data stored in 'IEEE big-endian' format, ref. LabVIEW

%Read header
Nhd = fread(src, 1, 'int32');                     % Read header
trace.header = readstring(src, Nhd);
trace.Nc     = fread(src, 1, 'uint32');
trace.x0     = fread(src, 1, 'float64');
trace.dx     = fread(src, 1, 'float64');
trace.eoh    = ftell(src);                           % Register where header ends and data starts
trace.y      = fread(src, [trace.Nc inf], '*float32');  % Read all data in onces

trace.y = trace.y';
trace.Np= max(size(trace.y));

fclose(src);

return

%=== Internal functions ===
function s= readstring(src,n)
ns= fread(src, n, '*uchar');
s = char(ns');
return
