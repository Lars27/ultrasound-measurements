function [Waveforms,fs] = Scan2D( X,Y,varargin)
%This function scan the plane at specific z
%[Waveforms,fs] = Scan2D( X,Y,calibration_enable)
%calibration can be included by add parameter 
Xpos = linspace(X.low_pos,X.high_pos,X.points_num);
Ypos = linspace(Y.low_pos,Y.high_pos,Y.points_num);
calllib ('SoniqClient','ClearWaveformParameters');
calllib ('SoniqClient','SetScopeUseCorrelation',true );
calllib ('SoniqClient','SetScopeWFRemoteAveraging',8);
calllib ('SoniqClient','SetScopeWFAveraging',8);
calllib ('SoniqClient','SetWaveformAutoscale',1);
calllib('SoniqClient','GetTemperature');
calllib('SoniqClient','ClearWaveform');
calllib('SoniqClient','DigitizeWaveform');
pBufferLength = calllib('SoniqClient','GetWaveformPoints');
Buff = zeros([1 pBufferLength]);
Waveforms = zeros([X.points_num,Y.points_num,pBufferLength]);
pBuffer = libpointer('doublePtr',Buff);
yIdx = 0;
for y = Ypos
    yIdx = yIdx + 1;
    calllib('SoniqClient','PositionerMoveAbs',Y.axist,y);
    dir = (mod(yIdx,2)*2-1);
    xIdx = (X.points_num + 1)*mod((yIdx-1),2);
    for x = Xpos
        xIdx = xIdx + dir;
        calllib('SoniqClient','PositionerMoveAbs',X.axist,x);%pause(0.2);
        calllib('SoniqClient','ClearWaveform');
        calllib('SoniqClient','DigitizeWaveform');
        if(calllib('SoniqClient','GetDataValid') ~= 0)
            calllib('SoniqClient','GetWaveformData',pBuffer,pBufferLength);
            Waveforms(xIdx,yIdx,:) = pBuffer.value;
            
            %             plot(pBuffer.value); grid on;pause(2);
        else
            calllib ('SoniqClient','MessageBox','Can not get waveform' ,0);
        end
    end
    Xpos = flip(Xpos);
end
aims_move_xy(0,0);
timebase = calllib('SoniqClient','GetScopeTimebase');
fs = pBufferLength/(10*timebase)*1e6;
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

end