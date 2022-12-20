function [d, cw]=soundspeed2distance(Temp, usfile, offset)
% function d=soundspeed2distance(Temp, usfile, offset)
%
% Calculate distance between transducers using speed of sound from water temperature
% Four diffrent estimates
%   1) Time of flight, one way, between transducers
%   2) Time of flight, two-way, pulse-echo
%   1) Time of flight, two-way, autocorrelation of pulse-echo 
%   1) Cross-correlation between transmitted and reflected pulses

% Lars Hoff, USN, July 2019

% Look up sound velocity from temperature
[cw,~]= SoundVelocity(Temp);   % Speed of sound cw and S=dcw/dT from temperature in deg. C

%- Load, interpret, and plot measurement 
wfm= readwfm(usfile);
vw = double(wfm.v);

fs= 1/wfm.dt;
fc= 5.0e6*[0.01 5];
wc= fc/(fs/2);
[b,a]=butter(4,wc);
vwf=filtfilt(b,a,vw);
t=time(wfm.t0-offset,(1:wfm.Np),wfm.dt);
 
plot(t*1e6, vwf);
xlabel('Time [us]')
ylabel('Voltage [V]')
xlim(1e6*[min(t) max(t)]);
grid on

%--- Estimate 1 ---
%    Transmitted signal (ch 2), time-of-flight across tank 
Pw= abs(hilbert(vw(:,2)));
kmax=ParabolicMax(Pw);  % Pulse max
tmax=time(wfm.t0-offset,kmax,wfm.dt);
d(1,1)= tmax*cw;   % m  Distance between trasnducers

ts=pulsestart(t,vw(:,2),15e-6);
d(2,1)= ts*cw;   % m  Distance between trasnducers

%--- Estimate 2 ---
%    Reflected signal (ch 1), two-way time-of-flight across tank 
Pw= abs(hilbert(vw(:,1)));
k0=find(t>15e-6,1);
kmax=ParabolicMax(Pw(k0:end))+(k0-1);

tmax=time(wfm.t0-offset,kmax,wfm.dt);
d(1,2)= tmax/2*cw;   % m  Distance between trasnducers

ts=pulsestart(t,vw(:,1),15e-6);
d(2,2)= ts/2*cw;   % m  Distance between trasnducers

%--- Estimate 3 ---
%    Reflected wave, cross-correlation between excitation and echo
[xc,lags]=xcorr(vw(:,1),vw(:,1));
tlag=lags*wfm.dt;
k0=find(tlag>15e-6,1);
kmax=ParabolicMax(abs(xc(k0:end)))+(k0-1);

tmax = interp1(tlag,kmax);
d(1,3)= tmax/2*cw;   % m  Distance between trasnducers

%--- Estimate 4 ---
%    Transmitted and reflected wave, cross-correlation echoes
k0=find(t>15e-6,1);
[xc,lags]=xcorr(vw(k0:end,1),vw(k0:end,2));
tlag=lags*wfm.dt;
kmax=ParabolicMax(abs(xc));

tmax = interp1(tlag,kmax);
d(1,4)= tmax*cw;   % m  Distance between trasnducers

ts1=pulsestart(t,vw(:,1),15e-6);  % First arrival, reflected pulse
ts2=pulsestart(t,vw(:,2),15e-6);  % First arrival, transmittedpulse
ts=ts1-ts2;
d(2,4)= ts*cw;   % m  Distance between trasnducers


end
 
%--- Internal functions ---
function t=time(t0,n,dt)
t=t0+(n-1)*dt;
end

function ts=pulsestart(t,v,t0)
k0=find(t>t0, 1);
Vmax= max(abs(v(k0:end)));
ks= find(abs(v(k0:end))>0.05*Vmax, 1);  % Start of pulse
ts= interp1(t,ks+k0-1);
end

