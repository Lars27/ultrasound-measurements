% BeamprofileScan
% Script 
% Scan 2D beam profiles of ultrasound transducer
% 
% Measurement sequence 27 Mar 2019, for Astri Mikalsen: xy-scans at a selected z-positions
% 6 MHz, 4.2 mm square Doppler-transducer

%--- File name basis ---
m_ps5000a_connect
ps5000aSetting.num_average=8;
ps5000aSetting.bufferLength=4000;
ps5000aSetting.trigger.threahold_mode = ps5000aEnuminfo.enPS5000AThresholdDirection.PS5000A_RISING;
ps5000aSetting.trigger.threahold_mv = 1000;
ps5000aSetting.trigger.delaysample=0;
ps5000aSetting.preSampleNum=0;
m_ps5000a_setting_update();


desc= 'Gold';
d=datevec(now);
filebase=sprintf('wfs_%04d_%02d_%02d_%s_', d(1), d(2), d(3), desc );
fprintf('\nStarting measurement. Files saved to %s \n', filebase)

%--- Define positions ---
X.axist   = 0;  %      Axis number
X.ref     = 0;  % mm   Reference position, for yz-scan 
X.high_pos= 7;  % mm   
X.low_pos =-X.high_pos; 
X.d       = 0.1;  % mm
X.points_num = round((X.high_pos-X.low_pos)/X.d) +1;

Y = X;
Y.axist   = 1;  % Axis number

depth =  [ 3 5 10 ];  % mm Depths to scan xy-planes

Z.axist   =   2;  % Axis number
% Z.ref     =  5 ;  % mm Reference position, for yz-scan 
% Z.low_pos =  5;   % mm
% Z.high_pos= 10;   % mm
% Z.d       =  2;   % mm
% Z.points_num = round((Z.high_pos-Z.low_pos)/Z.d) +1;

%--- Start and run AIMS ---
aims_connect();

%--- Position calibration ---
%--- Normally done directly from Sonic, commented out
% calllib ('SoniqClient','FindPulseAutoMinMax');
% calllib ('SoniqClient','SetScopeSensitivity',1,0.02);
% calllib ('SoniqClient','FindPulse');
% calllib ('SoniqClient','AutoScale');

aims_get_single_waveform

fprintf('\nScanning ')
%=== Scan xy planes, at distances specified by Z.ref ============
Nz = length(depth);

for k=1:Nz
    Z.ref= depth(k);
    fprintf('\nxy-plane %d of %d, z=%.1f mm ...', k, Nz, Z.ref);
    aims_move_xyz( X.ref,Y.ref,Z.ref);
    [Waveforms,fs] = Scan2D_v1(X,Y);
    cond= GetAIMSconditions;
    filename = sprintf('%sXY_z_%03.0f_mm',filebase,Z.ref);
    save(filename,'Waveforms','X','Y','Z','fs','cond', 'ps5000aSetting');  
    fprintf('\tReady. Saved to %s', filename)
end
fprintf('\nMeasurement sequence finished\n')
m_notification_push('Measurement','DONE');
aims_move_xy(0,0);
aims_close();


