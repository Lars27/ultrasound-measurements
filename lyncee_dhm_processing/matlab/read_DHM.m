function DHM= read_dhm(mask, rawdatadir)
% function DHM= read_dhm(mask, rawdatadir)
% 
% Read sequence of files from Lyncee DHM using 'read_mat_bin' from LynceeTec
%
% Read all files in selected directory matching mask
% Stack 2D images in 3D matrix, 3rd dimension is image number
%
%    mask     File names to include, using wildcards
% rawdatadir  Path to search in. (Defaluts to current directory)
%
%        DHM  Result as struct, explained at end of file

% Lars Hoff, USN, 2022

if nargin<2
    rawdatadir=cd;
end

rawdatafiles = dir(fullfile(rawdatadir, mask));   % Raw data files, exported from Koala
nFiles= length(rawdatafiles);

%% Read first frame to initialise image, using 'read_mat_bin' from Lyncee
[a, w, h, hconv, pxsize, unit_code]= ...
    read_mat_bin(fullfile(rawdatadir, rawdatafiles(1).name));  

% Load images into 3D matrix
data=zeros(w, h, nFiles);
for kFile=1:nFiles   
    [a, w, h, hconv, pxsize, unit_code]= ...
        read_mat_bin(fullfile(rawdatadir, rawdatafiles(kFile).name));  
    data(:,:,kFile)=a;
end

%% Format result into struct
DHM.data= data;   % Raw data values
DHM.dz= hconv;    % Conversion factor, phase to displacement [m/radian]
DHM.dx= pxsize;   % Conversion factor, pixel to lateral dimension [m/pixel]
DHM.xMax= pxsize*w;  % [m] Image width 
DHM.yMax= pxsize*h;  % [m] Image height

end
