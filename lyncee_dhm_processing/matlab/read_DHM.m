function DHM= read_DHM(mask, srcpath)
% function DHM= read_DHM(mask, srcpath)
% 
% Read sequence of files from Lyncee DHM using 'read_mat_bin' from LynceeTec
%
% Read all files in selected directory matching mask
% Stack 2D images in 3D matrix, 3rd dimension is image number
%
%    mask   File names to include, using wildcards
% srcpath   Path to search in. (Defaluts to current directory)
%
%     DHM   Result as struct, explained at end of file

% Lars Hoff, USN, 2022

if nargin<2
    srcpath=cd;
end

src = dir( fullfile( srcpath, mask ) );   % Raw data files, exported from Koala
n   = length(src);

%% Read first frame to initialise image, using 'read_mat_bin' from Lyncee
[a, w, h, hconv, pxsize, unit_code] = read_mat_bin( fullfile( srcpath, src(1).name ) );  

% Load images into 3D matrix
data = zeros(w,h,n);
for k=1:n   
    [a, w, h, hconv, pxsize, unit_code] = read_mat_bin( fullfile( srcpath, src(k).name ) );
    data(:,:,k)=a;
end

%% Format result into struct
DHM.data  = data;      % Raw data values
DHM.hconv = hconv;     % Conversion factor, phase to displacement [m/radian]
DHM.pxsize= pxsize;    % Conversion factor, pixel to lateral dimension [m/pixel]
DHM.xmax  = pxsize*w;  % [m] Image width 
DHM.ymax  = pxsize*h;  % [m] Image height

end
