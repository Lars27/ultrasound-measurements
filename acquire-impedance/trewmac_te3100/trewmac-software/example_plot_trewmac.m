% Plot impedance and S-parameters
%
% Example on plotting reflection coefficients and impedance from
% measurement with Trewmac TE3001

src= 'test_4.csv';
trace = ReadTE3001(src);

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
ylim ( [ -90 90 ] )
grid on

subplot( 2,2,2 )
plot( trace.f/1e6, abs(trace.Z) )
xlabel( 'Frequency [MHz] ')
ylabel( 'Impedance magnitude \angleZ[\Omega]')
grid on

subplot( 2,2,4 )
plot( trace.f/1e6, rad2deg( angle( trace.Z ) ) )
xlabel( 'Frequency [MHz] ')
ylabel( 'Impedance phase |Z| [Degrees]')
ylim ( [ -90 90 ] )
grid on
