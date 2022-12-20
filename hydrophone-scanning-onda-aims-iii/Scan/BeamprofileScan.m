% BeamprofileScan
% Script 
% Scan 2D beam profiles of ultrasound transducer
% 

%--- File name basis ---
desc= '1200kHz';
d=datevec(now);
filebase=sprintf('wfs_%04d_%02d_%02d_%s_', d(1), d(2), d(3), desc );
fprintf('\nStarting measurement. Files saved to %s... \n', filebase)

%--- Define positions ---
X.axist   = 0;  %      Axis number
X.ref     = 0;  % mm   Reference position, for yz-scan 
X.low_pos =-60; % mm
X.high_pos= 60; % mm
X.d       = 1;  % mm
X.points_num = round((X.high_pos-X.low_pos)/X.d) +1;

Y.axist   = 1;  % Axis number
Y.ref     = 0;  % mm Reference position, for yz-scan 
Y.low_pos =-60; % mm
Y.high_pos= 60; % mm
Y.d       = 1;  % mm
Y.points_num = round((Y.high_pos-Y.low_pos)/Y.d) +1;

Z.axist   =   2;  % Axis number
Z.ref     =  80;  % mm Reference position, for yz-scan 
Z.low_pos =  30;  % mm
Z.high_pos= 100;  % mm
Z.d       =   1;  % mm
Z.points_num = round((Z.high_pos-Z.low_pos)/Z.d) +1;

%--- Start and run AIMS ---
aims_connect();

%--- Position calibration ---
%--- Normally done directly from Sonic, commented out
% calllib ('SoniqClient','FindPulseAutoMinMax');
% calllib ('SoniqClient','SetScopeSensitivity',1,0.02);
% calllib ('SoniqClient','FindPulse');
% calllib ('SoniqClient','AutoScale');

aims_get_single_waveform

%--- Scan 3 planes: XZ, YZ, and XY ---
fprintf('\nxz-plane ...')
aims_move_xy(X.ref,Y.ref);
[Waveforms,fs] = Scan2D( X,Z);
cond= GetAIMSconditions;
filename = sprintf('%sXZ',filebase);
save(filename,'Waveforms','X','Y','Z','fs','cond');
fprintf('\tReady. Saved to %s', filename)

fprintf('\nyz-plane ...')
aims_move_xy(X.ref,Y.ref);
[Waveforms,fs] = Scan2D(Y,Z);
cond= GetAIMSconditions;
filename = sprintf('%sYZ',filebase);
save(filename,'Waveforms','X','Y','Z','fs','cond');
fprintf('\tReady. Saved to %s', filename)

fprintf('\nxy-plane ...')
aims_move_xyz( X.ref,Y.ref,Z.ref);
[Waveforms,fs] = Scan2D(X,Y);
cond= GetAIMSconditions;
filename = sprintf('%sXY',filebase);
save(filename,'Waveforms','X','Y','Z','fs','cond');
fprintf('\tReady. Saved to %s', filename)

fprintf('\nMeasurement sequence finished\n')

aims_move_xy(0,0);
aims_close();


