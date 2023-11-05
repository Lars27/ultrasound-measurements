function ExamplePlotImpedances(code,no)
% function ExamplePlotImpedances(src)
%
% Example program
% Load and plot a group of impedance measurements from HP8753, 
% saved as S11-parameters
% From functions written in LabVIEW at HBV-IMST

Zref = 50;                             % Ohm   Reference impedance

%-- Build fileames --
Nf = length(no);
for k=1:Nf
    src{k}= sprintf('%s%04d.trc', code, no(k));
end
   
for k=1:Nf
    %--- Load raw data ---    
    trc(k)= readtrace(src{k});

    %--- Create frequency vector, calculate Z, and plot impedance  ---
    f{k}= [0:trc.Np-1]*trc.dx+trc.x0;      % Hz   Frequency vector
end

    S11{k} = double(trc.y(:,1)+ 1i*trc.y(:,2));
    Z = Zref* (1+S11{k})./(1-S11{k});         % Ohm  Complex impdance
end
keyboard
subplot(2,2,1)
semilogy(f,abs(Z));
xlabel('Frequency [Hz]')
ylabel('Impedance magnitude [Ohm]')
grid on

subplot(2,2,3)
phi = angle(Z);
plot(f,rad2deg(phi));
xlabel('Frequency [Hz]')
ylabel('Phase [deg]')
ylim([-90 90])
set(gca, 'ytick', [-90:30:90])
grid on

subplot(2,2,2)
plot(f, real(Z), 'b-', f, imag(Z), 'r-');
xlabel('Frequency [Hz]')
ylabel('Impedance [Ohm]')
grid on

subplot(2,2,4)
plot(f, real(S11), 'b-', f, imag(S11), 'r-');
xlabel('Frequency [Hz]')
ylabel('S11')
ylim([-1 1])
grid on

keyboard
return
