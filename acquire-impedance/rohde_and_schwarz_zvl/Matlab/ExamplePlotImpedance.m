function ExamplePlotImpedance(src)
% function ExamplePlotImpedance(src)
%
% Example program, load and plot impedance measurement from HP8753, 
% saved as S11-parameters
% From functions written in LabVIEW at HBV-IMST

Zref = 50;                             % Ohm   Reference impedance

%--- Load raw data ---
trc= readtrace(src);

%--- Create frequency vector, calculate Z, and plot impedance  ---
f= [0:trc.Np-1]*trc.dx+trc.x0;      % Hz   Frequency vector

S11 = double(trc.y(:,1)+ 1i*trc.y(:,2)); 
Z = Zref* (1+S11)./(1-S11);         % Ohm  Complex impdance

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
% 
% Y= 1./Z;
% plot(real(Y), imag(Y), '-');

return
