function newPath= trimpath(filePath, nDirs)
% function newpath= trimpath(filePath, nDirs)
%
% Remove last files/folders in filepath

% Lars Hoff, USN, Nov 2020
%     July 2024 Updated to allow only one argument

if nargin<2
    nDirs=1;
end

% Fileseparator positions. Last character may or may not be filesep
separatorPositions=find(filePath(1:end-1)==filesep);  

nDirs=min(length(separatorPositions), nDirs); 
lastPosition= separatorPositions(end-nDirs+1);
newPath= filePath(1:lastPosition);

end

