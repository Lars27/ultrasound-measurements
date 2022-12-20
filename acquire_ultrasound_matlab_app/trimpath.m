function newpath= trimpath(filepath,n)
% newpath= trimpath(filepath,n)
%
% Remove n last files/folders in filepath

% Lars Hoff, USN, Nov 2020

ksep=find(filepath(1:end-1)==filesep);  % Fileseparator positions. Excludes last character, as this may or may not be filesep
n=min(length(ksep),n);
newpath= filepath(1:ksep(end-n+1)-1);

end

