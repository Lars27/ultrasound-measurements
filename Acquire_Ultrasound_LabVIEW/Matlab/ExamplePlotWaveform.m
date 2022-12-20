% ExamplePlotWaveform
%
% Example program, load and plot waveform saved from the 'Stream wfm' 
% functions written in LabVIEW at HBV-IMST

%src= 'PZ24_alone_sine_hanning_2cyc_5V_far_1.wfm';   % Name of the file saved from LabVIEW
src= 'PZ24_assembled_sine_hanning_2cyc_5V_far_1.wfm';   % Name of the file saved from LabVIEW

%--- Load raw data ---
wfm= readwfm(src);

%--- Create tim vector an plot pulse ---
t= [0:wfm.Np-1]*wfm.dt+wfm.t0;      % s   Time vector, including start time
subplot(2,1,1)

plot(t,wfm.v);                      %     Plot voltage as function of time
xlabel('Time [s]')
ylabel('Voltage [V]')

%--- Power spectrum ---
Nfft= 2^(nextpow2(wfm.Np)+2);       %     Pad with zeros to interpolate spectrum
fs = 1/wfm.dt;
f= [0:Nfft-1]/Nfft*fs;          % Hz  Frequency vector
Fv = fft(wfm.v,Nfft);
P  = abs(Fv.^2);                    %     Power spectrum
PdB= 10*log10(P/max(max(P)));       % dB  Power spectrum rel. max.

subplot(2,1,2)
plot(f,PdB);                        %     Plot power spectrum
xlim([0 16]*1e6);
ylim([-40 0]);
xlabel('Frequency [Hz]')
ylabel('Power [dB]')

