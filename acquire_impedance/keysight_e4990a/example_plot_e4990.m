% Plot impedance 
%
% Example on plotting impedance from
% measurement with Keysight E4990

src='HELENERFID3.CSV';

trace = read_e4990(src);

subplot( 2,1,1 )
plot( trace.f/1e6, abs(trace.Z) )
xlabel( 'Frequency [MHz] ')
ylabel( 'Magnitude |Z| [\Omega]')
grid on

subplot( 2,1,2 )
plot( trace.f/1e6, rad2deg( angle( trace.Z ) ) )
xlabel( 'Frequency [MHz] ')
ylabel( 'Phase \angleZ [Degrees]')
ymax = 90;
ylim  ( ymax*[ -1 1 ] )
yticks(  -ymax :30:ymax   )
grid on
