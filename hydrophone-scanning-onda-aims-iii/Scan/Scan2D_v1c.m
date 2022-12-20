function [Waveforms,fs] = Scan2D_v1c( X,Y,varargin)
% function [Waveforms,fs] = Scan2D_v1c( X,Y,varargin)
% Scan the xy plane at specific z and record pulses with hydrophone

global ps5000aSetting;

%--- Set up scan ---
ps5000aSetting.num_average=32;                % Averaging in Picoscope
fs = ps5000aSetting.fs;                       % Sample rate
cond= aims_get_conditions();                  
ps5000aSetting.trigger.delaysample=round(fs*cond.delay);
m_ps5000a_setting_update();

Xpos = linspace(X.low_pos,X.high_pos,X.points_num);  % Vector of x-positions
Ypos = linspace(Y.low_pos,Y.high_pos,Y.points_num);  % Vector of y-positions

calllib('SoniqClient','GetTemperature');
Waveforms = zeros([X.points_num,Y.points_num,ps5000aSetting.bufferLength]);

%-- Initialize figure to show results continously ---
figure
axis equal
xlim([X.low_pos X.high_pos]);
ylim([Y.low_pos Y.high_pos]);
hold on

%--- Run hydrophone scan ---
margin= 1e-6;     % Safety margin for delay
yIdx = 0;
for y = Ypos
    yIdx = yIdx + 1;   % y-index of result matrix
    calllib('SoniqClient','PositionerMoveAbs',Y.axist,y);
    cond  = aims_get_conditions();
    ps5000aSetting.trigger.delaysample=round(fs*(cond.delay-margin));
    m_ps5000a_setting_update();

    dir = (mod(yIdx,2)*2-1);
    xIdx = (X.points_num + 1)*mod((yIdx-1),2);
    for x = Xpos
        xIdx = xIdx + dir;  % x-index of result matrix
        calllib('SoniqClient','PositionerMoveAbs',X.axist,x);
        pause(0.1);
        
        wf= m_ps5000a_save_wf_autoscale();
        Waveforms(xIdx,yIdx,:) =wf(:,1);     % Store recorded trace in matrix, [x,y,v(t)]
        scatter(x,y,[], max(wf(:,1)),'filled','Marker','s')  %        % Show result in scatter plot
    end
    Xpos = flip(Xpos);
end

aims_move_xy(0,0);
if(nargin>=3)
    Waveforms = p_calib(Waveforms,fs);
end

end

%=== Internal functions ==========
function calib_waveforms = p_calib(Waveforms,fs)
%This function is internally used for calibration
[x,y,len] = size(Waveforms);
%data = zeros([x,y],'gpuArray'); %only active on MATLAB 64bits
B = reshape(Waveforms,x*y,len);
calib_waveforms = [];
parfor i = 1:x*y
    calib_waveforms(i,:) = m_calibration(squeeze(B(i,:))',fs);
end
len = length(calib_waveforms(1,:));
calib_waveforms = reshape(calib_waveforms,x,y,len);
m_ps5000a_close
end