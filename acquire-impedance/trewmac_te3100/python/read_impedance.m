function trace= read_impedance(tracefile)
% function trace= readtrace(tracefile)
%
% Read electrical impedance spectra stored as scaled single precicion float values
%
% This function is not suitable for very large recordings, as all results
% from the raw data file are into memory at once
% 
% Data storage structure:
%
% header: Short text identifying measurement type
% timer : Measurement time and date as string 
%     Nc: [u32]  Number of data channels 
%    eoh: [dbl]  'End of header'. File position where  header ends and
%                recorded data points start
%      f: [sgl]  Frequency vector
%      Z: [sgl]  Impedance as [ magnitude , phase ]
%      Z: [dbl]  No. of sample points per channel
%
% Based on version for ultrasound time-traces, Lars Hoff, HiVe, March 2011
% Adapted to electrical impedance spectra from Trewmac TE300x, Dec 2022
% Lars Hoff, USN, Jan 2023

src = fopen (tracefile,'rb','ieee-be');   % Data stored in 'IEEE big-endian' format, ref. LabVIEW

Nhd = fread(src, 1, 'int32');                % Read header
trace.header = readstring(src, Nhd);
Ntm = fread(src, 1, 'int32');                % Read time marker
trace.time   = readstring(src,  Ntm);
trace.Nc     = fread(src, 1, 'uint32');
trace.eoh    = ftell(src);                   % Register where header ends and data starts

y = fread(src, [trace.Nc inf], '*float32');  % Read all data into one matrix
trace.f = double( y(1,:)'   );
trace.Z = double( y(2:3,:)' );
trace.Np= length( trace.f );

fclose(src);

return

%% Internal functions 
function s= readstring(src,n)
ns= fread(src, n, '*uchar');
s = char(ns');
return
