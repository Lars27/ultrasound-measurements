function [resultfile,filename,n] = FindFilename(prefix,ext,dir)
% function [resultfile,filename,n] = FindFilename(prefix,dir)
% 
% Create filename from prefix and today's date
% Format: 'prefix_yyyy_mm_dd_nnnn.ext'
% 
%   prefix : Code identifying file type
%   ext    : File extension
%   dir    : Directory (optional)
%
%   resultfile : Name of reult file, full path if dir was given
%   filename   : Filename without path
%   n          : File counter 
%
% Advences counter by one and stores last file number in counter-file prefix.cnt
%

% Lars Hoff, USN, Nov 2020

if nargin<3, dir=[]; end
if nargin<2, ext=[]; end

%  Remove leading '.' from 'ext'
if not(isempty(ext))                    
    if ext(1)=='.'
        ext=ext(2:end);
    end
end

%  Check if result directory is a folder
if isempty(dir) 
    dir=cd;
elseif not(exist(dir,'dir'))
    mkdir(dir);
end  

% Read last number from counter file
counterfile=fullfile(dir, sprintf('%s.cnt',prefix));
if exist(counterfile, 'file')
    fid=fopen(counterfile, 'r+t');
    n=fscanf(fid,'%d');    
    fclose(fid);
else
    n=0;
end

% Create file name and check whether it already exists
finished=0;
while not(finished)
    n=n+1;
    filename=sprintf('%s_%s_%04d.%s', prefix, datestr(now, 'yyyy_mm_dd'), n, ext );
    resultfile=fullfile(dir, filename);
    finished=not(exist(resultfile, 'file'));
end

% Update counter file
fid=fopen(counterfile, 'w+t');
fprintf(fid,'%d',n);
fclose(fid);

end
