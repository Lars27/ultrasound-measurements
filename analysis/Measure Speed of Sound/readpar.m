function par = readpar(src)
% function par = readpar(src)
%
% Read and interpret parameter file for a measurement
% File extension '.cpa'
% 
% Format per line: 
%    name1 value1 value2 ... % Comment
%    name2 value1 value2 ... % Comment
%
% Characters after '%' are ignored
%
% Return result in structure 'par' with fields 'name1', 'name2' ... etc.
%   If a letter is found, the value is interpreted as one string. This may
%      contain spaces
%   If no letter is found, the value is interpreted as an array of numbers,
%      separated by spaces. 
%
% Return format in variable 'par'
%   par.name1= [value1 value2 ...]
%   par.name2= [value1 value2 ...]
%     etc.

% Lars Hoff, USN, Nov 2019

%--- Add extension, check if file exists ---
[~,fname, ext] = fileparts(src);   
if isempty(ext), fname= sprintf('%s.cpa',fname);
else,            fname= src;
end

fid=fopen(fname);
if fid<0, error('Parameter file %s not found', fname); end

%--- Read and interpret parameter file
fprintf('\nReading measurement parameters from %s', fname)
finished=0;
k=1;
while not(finished)    
    tline= fgetl(fid);  % Read one line at a time
    if tline==-1         % End-of-file encountered
         finished=1;
    elseif not(isempty(tline))
        tstring= convertCharsToStrings(tline);
        tstring= extractBefore(tstring,'%'); % Ignore comments
        [sname,val]=strtok(tstring);       % Split field name and values
        if not(sname=="")
            val=strtrim(val);
            if any(isletter(val))
                par.(sname)=val;         % String, only one allowed per line
            else
                par.(sname)=sscanf(val,'%g'); % Numerical array
            end
            k=k+1;
        end
    end
end
fclose(fid);
fprintf(' Finished\n')

end

