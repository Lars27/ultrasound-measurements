function pulse= MakePulse(pulse, ploton)
% function pulse= MakePulse(pulse, ploton)
% 
% Make ultrasound pulse from description in struct 'pulse'
% Output fields are added to the input structure
%
%     ploton : Optional, Plot result
%
% Input fields  
%    envelope: Pulse envelope as one of Matlab's window functions
%              hann, rectwin, tukeywin, etc.
%       shape: Pulse shape from Matlab function 'sine', 'square',
%                   'triangular', sawtooth
%          f0: Center frequency [Hz]
%          Nc: Length as number of cycles
%          fs: Sample rate [1/s]
%
% Output fields
%           t: Time vector [s]
%           v: Normalized voltage vector
%           f: Frequenyc vector [Hz]
%         PdB: Power spectrum [dB re max.]

%  Lars Hoff, USN, Nov 2020

if nargin<2, ploton=0; end

if not(isfield(pulse, 'phase')), pulse.phase=0; end

%% Pulse definition 
dt= 1/pulse.fs;
T = pulse.Nc/pulse.f0;
t = (0:dt:T)';
N = length(t);

wt= 2*pi*pulse.f0*t + deg2rad(pulse.phase); 
switch lower(pulse.shape)
    case 'square',     y= square(wt);
    case 'sine',       y= sin(wt);
    case 'triangular', y= sawtooth(wt,1/2);        
    case 'sawtooth',   y= sawtooth(wt);        
end

% Add envelope: Multiply by window
w= feval(pulse.envelope,N);  
y= w.*y;

% Add extra zero at end 
t(end+1)=max(t)+dt;
y(end+1)=0;  

%% Spectrum 
Nfft=2^(nextpow2(N)+1);
Nfft=max(1024,Nfft);       % Minumum no. of points in spectrum
Fy = fft(y,Nfft);
P  = abs(Fy.^2);
PdB= 10*log10(P/max(P));
f  = (0:Nfft-1)'/Nfft*pulse.fs;

%% Output to struct
pulse.t = t;
pulse.v = y;
pulse.f = f;
pulse.PdB= PdB;

%% Plot result for inspection 
if ploton
    subplot(2,1,1)
    plot(pulse.t,pulse.v);
    xlabel('Time [s]')
    ylabel('Amplitude [relative]')
    grid on

    subplot(2,1,2)
    plot(pulse.f,pulse.PdB);
    xlabel('Frequency [Hz]')
    ylabel('Power [dB re. max]')
    xlim([0 4*pulse.f0])
    ylim([-40 0]);
    grid on
end
end
