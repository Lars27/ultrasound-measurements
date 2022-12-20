function PlotExcitationPulse(src, printresult)
% function PlotExcitationPulse(src, printresult)
%
% Load and plot waveform saved from the 'Stream wfm' 
% functions written in LabVIEW at HBV-IMST

% Lars Hoff, HSN, May 2017

if nargin<2,    printresult=0;  end

%--- Load raw data ---

[srcpath, srcname, srcext]= fileparts(src);

wfm= readwfm(src);

%--- Create time vector and plot pulse ---
t= [0:wfm.Np-1]*wfm.dt+wfm.t0;      % s   Time vector, including start time
fs= 1/wfm.dt;


v=double(wfm.v(:,1));
vh=hilbert(v);
vhn=vh/max(abs(vh));
k=find(abs(vhn(1:floor(0.9*end)))>0.7);
Vrms=sqrt(mean(v(k).^2));
V0  = sqrt(2)*Vrms;

%--- Plot pulse and calculate spectrum ---
tc= t(max(k))*1e6;
tscale= [-5 30]*1e-6;
[PdB,f]=PlotPulse(t,v, tscale, 10*[-1 1]);
Nfft= length(f);

%--- Add text ---
% subplot(2,1,1)
% text(tc+2, 5, sprintf('V_{RMS}=%4.2f V', Vrms))
% text(tc+2, 8, sprintf('V_{0}=%4.2f V', V0))

%--- Frequency from cross-correlation ---
vc= v(1:floor(end/2));
N=length(vc);
xc=xcorr(vc);
xc=xc(N:end);

[cmin nmin]=min(xc);
[cmax nmax]=max(xc(nmin:end));
n0=nmax+nmin-1;
T0= n0/fs;
f0=1/T0;

% %---Frequency from -6 dB limits
% Nc = floor(Nfft/2);
% fp= f(1:Nc);
% Pp= PdB(1:Nc);
% 
% [Pm km]= max(Pp);
% fm=fp(km);
% flim=BeamLimits(Pp,fp,km);
% fc= 1/2*(max(flim)+min(flim));
% 
% subplot(2,1,2)
% text(2*f0/1e6, -10, sprintf('f_{0}=%4.0f kHz', fc/1e3))

%--- Plot figure ---
[axpos] = pdffigure(21);

if (printresult)
    print('-dpdf', sprintf('%s_pulse',srcname))
end

return
end

% %=== INTERNAL FUNCTIONS ===================
% %--- Beam limits ---
% function flim=BeamLimits(Pc,f,k0)
% Plim=-6;
% fmin=interp1(Pc(1:k0),  f(1:k0),  Plim,'pchip');
% fmax=interp1(Pc(k0:end),f(k0:end),Plim,'pchip');
% flim= [fmin fmax];
% end


