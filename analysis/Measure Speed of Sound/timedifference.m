function par= timedifference(par, swap)
%function par= timedifference(par,swap)
%
% Find time-difference between propagation times with and without sample 
% in water
%
% Channels organized as [Reflected Transmitted]
% swap  Specifies that channels were swapped during measurement
%
% Filenames and measuremept parameters stored in structure par.
% Fields used
%  par.Mfile   Measurement with sample
%  par.Rfile   Reference measurement without sample
%  par.fc      Center frequency, used to specify noise filter
%  par.T       Temperature used to find speed of sound in water
%  par.Tw      Approximate arrival time, used to specify search interval
%
% Results exported into same variable, par
% New fields
%  par.dtp     Propagaqtion time difference
%  par.cw      Speed of sound in water
%  par.dw      Distance between transducers, calculated from speed of sound 
%
% Load data from raw data files with and without sample
% This file contains two channels
%  1) Pulse-echo. Reflection from sample surface, and reverberations
%  2) Through-transmission. Transmitted through sample, and reverberations
%  Results from these two channels are calculated independently
%

if nargin<2, swap=0; end
    
fprintf('\nDifference in propagation time ')

%--- Load and interpret raw data file ----------------------------------
wfm(1)= readwfm(par.Mfile);    % Measurement with sample
wfm(2)= readwfm(par.Rfile);    % Reference measurement in water
Nm= length(wfm);

if swap
    for k=1:Nm
        wfm(k).v= flip(wfm(k).v,2);
    end
end

%--- Organize and filter results ---
v= double([wfm(1).v wfm(2).v]);          % Voltage traces in columns
vname={'Reflected from sample'
       'Transmitted through sample'
       'Reflected from water'
       'Transmitted through water' };                                                        
   
t = wfm(1).t0+(0:wfm(1).Np-1)*wfm(1).dt; % Time vector, common

flim= [0.3 1.5]*par.fc*1e6;         % Noise reduction filter limits
fs= 1/wfm(1).dt;
wc= flim*2/fs;                    
[b,a]=butter(4,wc);
vf=filtfilt(b,a,v);

%--- Find distance from propagation time in water  --------------------
[cw,~]= SoundVelocity(par.T);   % Speed of sound in water from temperature
Tint= [(par.Tw-20)*1e-6 ,inf];  % Time window to look for pulses
tp= finddifference(vf(:,3:4), t, Tint ); % Propagation time through water
                                         % From one- and two way transmissions
dw= tp*cw; % Propagation distance through water, from speed of sound

Tint= (par.Tw+[-20 20])*1e-6;
td=finddifference(vf(:,[2 4]) ,t, Tint); % Propagation time difference

%--- Plot results for inspection -------------------------------------
% Transmitted pulses
subplot(2,1,1)
plotnos= [4 2]; % Organization of plots to show
plotpulse(t,vf(:,plotnos));
legend( vname{plotnos});
title(sprintf('Propagation time difference. %s', par.Mfile), ...
               'interpreter', 'none')
hold off

% Zoom in on arrival times
subplot(2,1,2)
Tlim= tp+td/2+abs(td)*[-1 1]+[-1 1]*1e-6;
plotpulse(t,vf(:,plotnos),Tlim);
title('Arrival times')
hold on

[vmax,kmax]=max(vf(:,4));
vt=0.7*vmax; 
tmax=t(kmax);
tline=(tmax+[0 td])*1e6;
plot(tline, vt*[1 1], 'kx-' )

text(mean(tline), vt, ...
     sprintf(' %s= %4.2f %s','\Deltat', td*1e6, '\mus' ), ...
     'VerticalAlignment', 'bottom', 'Horizontalalignment', 'Center');
hold off

%--- Export results ----------------------------------------------------
par.dtp= td; 
par.cw= cw;
par.dw= dw;

fprintf(' dt=%4.2f us', td*1e6 );

end

function [td]=finddifference(v,t,tlim)
dt=t(2)-t(1);
ki= (t>min(tlim) & t<max(tlim));
vi= v(ki,:);
[xc,lags]=xcorr(vi(:,1),vi(:,2),'normalized');
tlag=lags*dt;
kmax=ParabolicMax(abs(xc));
td = interp1(tlag,kmax);
end

function hp=plotpulse(t,v,int,col)
hp=plot(t*1e6,v);
if nargin>3, set(hp, 'Color', col), end
if nargin>2, xlim(int*1e6), end
xlabel('Time [\mus]')
ylabel('Voltage [V]')
grid on

end
