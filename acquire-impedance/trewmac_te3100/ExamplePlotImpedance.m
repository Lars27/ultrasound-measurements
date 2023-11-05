function ExamplePlotImpedance(src)
% function ExamplePlotImpedance(src)
%
% Example program, load and plot impedance measurement from HP8753, 
% saved as S11-parameters
% From functions written in LabVIEW at HBV-IMST

%--- Load raw data ---
trc= read_impedance(src);

%--- Create frequency vector, calculate Z, and plot impedance  ---
%f= [0:trc.Np-1]*trc.dx+trc.x0;      % Hz   Frequency vector
% 
% f     = double( trc.y(:,1) );
% Zabs  = double( trc.y(:,2) ); 
% Zphase= double( trc.y(:,3) ); 
% 
% Z = Zabs.*exp(1i*Zphase);

subplot(2,1,1)
semilogy( trc.f, trc.Z(:,1) );
xlabel('Frequency [Hz]')
ylabel('Impedance magnitude [Ohm]')
grid on

subplot(2,1,2)
plot( trc.f, trc.Z(:,2)/pi );
xlabel('Frequency [Hz]')
ylabel('Phase [rad]')
ylim( 1/2*[-1 1] )
set(gca, 'ytick', [-1/2:1/6:1/2] )
grid on

return
