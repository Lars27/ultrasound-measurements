% Open Koala bin file into Matlab and import Metadata
%
% "a": imported image in radian (for phase images)
% "w": width of the image in pixel
% "h": height of the image in pixel
% "hconv": conversion factor to convert the phase image (in radian) to
% physical height. The hconv factor is determined by the sample settings
% (refractive index) set in Koala. To apply it, multiply "a" by "hconv"
% "pxsize": pixel size in meter. Determined by the configuration used
% in Koala to record the image
% "unit_code": 1 = radian, 2 = meter
% "fname": path for the image to import in Matlab
%
% example: [a, w, h, hconv, pxsize, unit_code]=read_mat_bin("C:\Users\USER\Desktop\phase.bin");
%
% @author: naspert, comments: brappaz


function [a, w, h, hconv, pxsize, unit_code]=read_mat_bin(fname)

% Read file
    fid = fopen(fname,'rb');   
    head_vers = fread(fid,1,'int8');
    endianness = fread(fid,1,'int8');
    head_size = fread(fid,1,'int32');
    w = fread(fid,1,'int32');
    h = fread(fid,1,'int32');
    pxsize = fread(fid,1,'float32');
    hconv = fread(fid,1,'float32');
    unit_code = fread(fid,1,'int8');
    tmp = fread(fid,[w,h],'float32'); 
    a = tmp';
    fclose(fid);
    
