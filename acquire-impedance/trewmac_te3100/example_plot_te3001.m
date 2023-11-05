% Example of plotting impedance from Trewmac TE3001

src='TE_2023_01_11_0002.trc';
[f, Z]= read_TE3001(src); 
Y = 1./Z;
C = imag(Y)./(2*pi*f);

fMHz = f/1e6;

%% Magnitude - phase
subplot(2,3,1)
semilogy( fMHz , abs(Z) )
xlabel( 'Frequency [MHz]' )
ylabel( 'Impedance magnitude [Ohm]' )
grid on

subplot(2,3,4)
plot( fMHz , rad2deg( angle(Z) ) )
xlabel( 'Frequency [MHz]' )
ylabel( 'Impedance phase [Deg]' )
ylim( [-90 90] )
yticks( -90:30:90 )
grid on

%% Resistance - reactance
subplot(2,3,2)
plot( fMHz , real(Z), fMHz , imag(Z) )
xlabel( 'Frequency [MHz]' )
ylabel( 'Resistance and Reactance [Ohm]' )
grid on
legend ("R", "X")

%% Conductance - susceptance
subplot(2,3,3)
plot( fMHz , real(Y), fMHz , imag(Y) )
xlabel( 'Frequency [MHz]' )
ylabel( 'Conductance and Susceptance [Ohm]' )
grid on
legend ("B", "G")

%% Capacitance
subplot(2,3,5)
plot( fMHz , C )
xlabel( 'Frequency [MHz]' )
ylabel( 'Capacitance [F]' )
grid on


