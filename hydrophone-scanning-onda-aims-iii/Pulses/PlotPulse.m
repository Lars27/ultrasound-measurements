function [PdB,f]=PlotPulse(t,v, tscale, vscale)
% function [PdB,f]=PlotPulse(t,v, tscale, vscale)
% 
% Plot ultrasound pulse and its power spectrum
%
% LH, HSN, May 2017

if nargin<4, vscale= [-1 1]*max(abs(v)); end
if nargin<3, tscale= [min(t) max(t)];    end

%--- Time trace ---
subplot(2,1,1)
plot(t*1e6,v,'k-');                      %     Plot voltage as function of time
xlabel('Time [\mus]')
ylabel('Voltage [V]')
xlim(tscale*1e6)
ylim(vscale)
grid on

%--- Pulse amplitude ---
vh=hilbert(v);
vhn=vh/max(abs(vh));
k=find(abs(vhn(1:floor(0.9*end)))>0.7);  % Find pulse from envelope
tp= t(k);     
vp= v(k);    % Pulse

k0=find(abs(diff(sign(vp)))>0); 

Vrms=sqrt(mean(vp.^2));    % RMS voltage, between zero-crossings in main pulse
V0  = sqrt(2)*Vrms;        % Amplitude taken from RMS assuming sine wave
Vpp = max(v(k))-min(v(k)); % Peak to peak voltage, taken within pulse

ax=axis;
tc= ax(2);
vc= ax(4)*[0.7 0.3];
text(tc, vc(1), sprintf('V_{PP} = %.3g V ', Vpp), 'HorizontalAlignment', 'right' )
text(tc, vc(2), sprintf('V_{RMS}= %.3g V ', Vrms), 'HorizontalAlignment', 'right')
%text(tc, vc(2), sprintf('V_{0}=%4.2f V', V0))

%--- Power spectrum ---
Nt=length(t);
fs= 1/(t(2)-t(1));
Nfft= 2^(nextpow2(Nt)+2);       %     Pad with zeros to interpolate spectrum
f= [0:Nfft-1]/Nfft*fs;          % Hz  Frequency vector
Fv = fft(v,Nfft);
P  = abs(Fv.^2);                %     Power spectrum
[Pmax kmax]=max(P(1:end/2)); 
PdB= 10*log10(P/Pmax);          % dB  Power spectrum rel. max.

subplot(2,1,2)
plot(f/1e3,PdB,'k-');                        %     Plot power spectrum
xlim([0 3e3]);
ylim([-50 0]);
grid on
xlabel('Frequency [kHz]')
ylabel('Power [dB]')

%---Frequency from -6 dB limits
Nc = floor(Nfft/2);
fp= f(1:Nc);
Pp= PdB(1:Nc);
flim=BeamLimits(Pp,fp);
fc= 1/2*(max(flim)+min(flim));

ax=axis;
text(ax(2),-10, sprintf('f_{0}=%4.0f kHz ', fc/1e3), 'HorizontalAlignment', 'right' );

end

%=== INTERNAL FUNCTIONS ===================
%--- Beam limits ---
function flim=BeamLimits(P,f)
[Pm km]= max(P);
fm=f(km);
Plim=-6;
kl=      find(P(1:km)  < Plim, 1, 'last');  %  Largest index where P<Plim
kh= km-1+find(P(km:end)< Plim, 1, 'first');  %  Largest index where P<Plim

fmin= (f(kl+1)-f(kl))/(P(kl+1)-P(kl))*(Plim-P(kl))+f(kl);
fmax= (f(kh)-f(kh-1))/(P(kh)-P(kh-1))*(P(kh)-Plim)+f(kh);

if not(isempty(P(kl:kl+1))) && not(isempty(P(kl:kl+1)))
    fmin=interp1(P(kl:kl+1),  f(kl:kl+1),  Plim,'linear');
    fmax=interp1(P(kh-1:kh),  f(kh-1:kh),  Plim,'linear');
else
    fmin=0;
    fmax=0;
end
flim= [fmin fmax];
end


