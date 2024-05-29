function [Waveforms,fs] = Scan2D_v1( X,Y,varargin)
%This function scan the plane at specific z
%[Waveforms,fs] = Scan2D( X,Y,calibration_enable)
%calibration can be included by add parameter 
global ps5000aSetting;
ps5000aSetting.num_average=32;
fs=ps5000aSetting.fs;
cond= aims_get_conditions();
cal_delay=round(fs*cond.delay);
ps5000aSetting.trigger.delaysample=cal_delay;
m_ps5000a_setting_update();
Xpos = linspace(X.low_pos,X.high_pos,X.points_num);
Ypos = linspace(Y.low_pos,Y.high_pos,Y.points_num);

calllib('SoniqClient','GetTemperature');
Waveforms = zeros([X.points_num,Y.points_num,ps5000aSetting.bufferLength]);
figure
axis equal
xlim([X.low_pos X.high_pos]);
ylim([Y.low_pos Y.high_pos]);
hold on
yIdx = 0;
for y = Ypos
    yIdx = yIdx + 1;
    calllib('SoniqClient','PositionerMoveAbs',Y.axist,y);
    cond= aims_get_conditions();
    margin=1e-6;%1us
cal_delay=round(fs*(cond.delay-margin));
ps5000aSetting.trigger.delaysample=cal_delay;
m_ps5000a_setting_update();

    dir = (mod(yIdx,2)*2-1);
    xIdx = (X.points_num + 1)*mod((yIdx-1),2);
    for x = Xpos
        xIdx = xIdx + dir;
        calllib('SoniqClient','PositionerMoveAbs',X.axist,x);
        pause(0.1);
        
        wf= m_ps5000a_save_wf_autoscale();
        Waveforms(xIdx,yIdx,:) =wf(:,1);
%         plot(wf(1:end,1));hold on
   %     scatter(x, y,[], max(wf(:,1)),'filled');
     scatter(x,y,[], max(wf(:,1)),'filled','Marker','s')
    end
    Xpos = flip(Xpos);
end

aims_move_xy(0,0);
if(nargin>=3)
    Waveforms = p_calib(Waveforms,fs);
end

end
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