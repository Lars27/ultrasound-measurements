function [vf, PdB ]= BeamIntensity(Waveforms, fc, fs)
% function [vf, PdB ]= BeamIntensity(Waveforms, fc, fs)
%
% Filter and calculate beam intensity

[Nx,Nz,Nt]=size(Waveforms);

%--- Band pass filter definition ---
if length(fc)==2
    flim=fc;
else
    flim = [0.9 1.1]*fc;     % bandpass filter limits
end
wn= flim/fs*2;
[b,a]=butter(2,wn);

%--- Filter and calculate pulse energy 
vf =zeros(Nx,Nz,Nt);
PdB=zeros(Nx,Nz);
for kx=1:Nx
    for kz=1:Nz
        vf(kx,kz,:)= filtfilt(b,a,Waveforms(kx,kz,:));
        PdB(kx,kz) = 10*log10(sum(abs(vf(kx,kz,:)).^2));
    end
end
PdB=PdB-max(max(PdB));

end