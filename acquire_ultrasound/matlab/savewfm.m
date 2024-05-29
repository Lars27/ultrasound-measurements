function savewfm( wfmfile, wfm, overwrite )
% function wfm= savewfm(wfmfile)
%
% Save measured data stored as scaled single precicion float values
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

% Lars Hoff, USN, Oct 2023
 if nargin<3
     overwrite=0;
 end


if( isfile( wfmfile ) && not(overwrite) )
    error ('File exists')    
else
    src = fopen (wfmfile,'w+b','ieee-be');   % Data stored in 'IEEE big-endian' format, ref. LabVIEW

    hd= '<WFM_Matlab_float32>';
    Nhd = length(hd);

    fwrite( src,    Nhd, 'int32' );  
    fwrite( src,     hd, 'uint8' );  
    fwrite( src,  wfm.N, 'uint32' );
    fwrite( src, wfm.t0, 'float64');
    fwrite( src, wfm.dt, 'float64');
    fwrite( src,      0, 'float64');
    fwrite( src,  wfm.v', 'float32');  

    fclose(src);
end

return

