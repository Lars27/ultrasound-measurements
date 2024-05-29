% Plot impedance and S-parameters
%
% Example on plotting reflection coefficients and impedance from
% measurement with Trewmac TE3001

src= 'helene-rfid-impedans.csv';
trace = read_te3001(src);

subplot( 2,2,1 )
plot( trace.f/1e6, abs(trace.S11) )
xlabel( 'Frequency [MHz] ')
ylabel( 'Reflection magnitude |S_{11}| ')
ylim( [0 1 ] )
grid on

subplot( 2,2,3 )
plot( trace.f/1e6, rad2deg( angle( trace.S11 ) ) )
xlabel( 'Frequency [MHz] ')
ylabel( 'Reflection phase \angleS_{11} [Degrees]')
ymax= 180;
ylim  ( ymax*[ -1 1 ] )
yticks( -ymax:45:ymax )

grid on

subplot( 2,2,2 )
plot( trace.f/1e6, abs(trace.Z) )
xlabel( 'Frequency [MHz] ')
ylabel( 'Impedance magnitude |Z| [\Omega]')
grid on

subplot( 2,2,4 )
plot( trace.f/1e6, rad2deg( angle( trace.Z ) ) )
xlabel( 'Frequency [MHz] ')
ylabel( 'Impedance phase \angleZ [Degrees]')
ymax = 90;
ylim  ( ymax*[ -1 1 ] )
yticks( -ymax :30:ymax   )
grid on
