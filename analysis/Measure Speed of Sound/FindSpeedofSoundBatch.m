
% Find speed of sound in samples
% Batch version, process a series of measurements
% Load measured traces and calculate speed of sound by different methods 

% List of parameter files (*.cpa) containing measurement information
parfile={ ...
    'US_2020_09_14_0034' };
N=length(parfile);

exportfile='SpeedofsoundResults.txt';
fid=fopen(exportfile,'w');
if fid<0
    fprintf('\nCannot open file %s for writing\n', exportfile)
    return
end
ExportSpeedofSound(fid);

swap=0; % Measurements were done with reflected and transmtted channels swapped
for k=1:N
    src=parfile{k};
    par=FindSpeedofSound(src,swap);
    ExportSpeedofSound(fid,par);
end
fclose(fid);
fprintf('\nResults of %d measurements exported to file %s\n', N, exportfile )
