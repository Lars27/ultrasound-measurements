function par= timedelay(par,swap)
%function par= timedelay(par,swap)
%
% Find time-delay between reverberations, to calculate speed of sound in sample 
%
% Channels organized as [Reflected Transmitted]

%
% Filenames and measuremept parameters stored in structure par.
% Fields used
%  par.Mfile   Measurement with sample
%  par.fc      Center frequency, used to specify noise filter
%  par.Rint    Interval to search for reverbeations in reflected signals
%  par.Tint    Interval to search for reverbeations in transmitted signals
%
% Results exported into same variable, par
% New fields
%  par.dtr     Reverberation times
%

% Load data from raw data file 'usfile'
% This file contains two channels
%  1) Pulse-echo. Reflection from sample surface, and reverberations
%  2) Through-transmission. Transmitted through sample, and reverberations
%  Results from these two channels are calculated independently
%
% The input 'swap' is used to specify if channels were swapped during measurement
%
% The interval tlim must be selected to contain all samle echoes, including
% reverberations. For the standard setup, this is set to between 60 and 90
% us.

if nargin<2, swap=0; end

fprintf('\nTime between reverberations ')

%--- Load and interpret raw data file ----------------------------------
wfm= readwfm(par.Mfile);
if swap, wfm.v= flip(wfm.v,2); end

v = double(wfm.v);              % Voltage traces
t = wfm.t0+(0:wfm.Np-1)*wfm.dt; % Common time vactor
vname={'Reflected from sample'
       'Transmitted through sample'};                                 

flim= [0.3 1.5]*par.fc*1e6;         % Noise reduction filter limits
fs= 1/wfm(1).dt;
wc= flim*2/fs;                    
[b,a]=butter(4,wc);
vf=filtfilt(b,a,v);

%--- Plot results for inspection -------------------------------------
subplot(2,1,1)
hp=plotpulse(t,vf,[],[],vname, ...
    sprintf('Reverberations inside sample. %s', par.Mfile));

%--- Find delays between reverberations inside sample ---
subplot(2,2,3)
dt(1)=finddelay(vf(:,1),t,par.Rint*1e-6, hp(1).Color,'Reflected pulses');

subplot(2,2,4)
dt(2)=finddelay(vf(:,2),t,par.Tint*1e-6, hp(2).Color, 'Transmitted pulses');

%--- Export result ---
par.dtr=dt;

fprintf(' dt=%4.2f us', dt*1e6 );
fprintf('\n' );

end

%=== Internal functions ===========================================
%--- Find delay between reverberations, from auto-correlation 
function td=finddelay(v,t,tlim,col,tit)
if nargin<4, tit=''; end
if nargin<3, col=[]; end

dt=t(2)-t(1);
ki=find((t>min(tlim)) & (t<max(tlim)));
vi=v(ki);
ti=t(ki);
[xc,lags]=xcorr(vi,vi,'normalized');
tlag=lags'*dt;
xh=abs(hilbert(xc));  % Remove peak around td=0
ks=find((xh<1/20) & (tlag>0), 1 );
k0=find(tlag>3*tlag(ks),1);
kmax=ParabolicMax(abs(xc(k0:end))) +(k0-1);
td = interp1(tlag,kmax);

if not(isempty(col))
    plotpulse(ti,vi,tlim,col,[],tit);
    hold on
    [vt,nt]=max(vi);
    vt=0.7*vt;
    tline=1e6*(ti(nt)+[0 td]);
    plot(tline, vt*[1 1], 'kx-');
    text(mean(tline), vt, ...
        sprintf('%s= %.3f %s','\Deltat', td*1e6, '\mus' ), ...
     'VerticalAlignment', 'bottom', 'Horizontalalignment', 'Center');
    hold off
end
end

%--- Plot pulses for inspection ---
function hp=plotpulse(t,v,int,col,leg,tit)
hp=plot(t*1e6,v);
if not(isempty(col)), set(hp, 'Color', col), end
if not(isempty(int)), xlim(int*1e6), end
xlabel('Time [\mus]')
ylabel('Voltage [V]')
if not(isempty(tit)), title(tit, 'interpreter', 'none'); end
if not(isempty(leg)), legend(leg); end
grid on
end
