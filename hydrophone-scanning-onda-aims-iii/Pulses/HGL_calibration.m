clf

[M,hd] = ReadOndaCalibration('HGL0200-1765_xxxxxx-xxxx-xx_xx_20151117.txt',5);
fH=M(:,1)*1e6;
SH=M(:,3);
SHdB=M(:,2);
CH= M(:,5)*1e-12;

S0= 1e6;
SHc= 10.^(SHdB/20)*S0;


subplot(3,1,1)
plot(fH,SH,'k-');
%xlabel('Frequency [Hz]')
str= sprintf('Hydrophone Sensitivity [V/Pa]');
ylabel(str)
%axis([0 20 [4 6]*1e-8])
grid on


%===========================================
[M,hd] = ReadOndaCalibration('AG-2010-20-060-1132_1-20t_151117.txt',4);

fA=M(:,1)*1e6;
GA=M(:,2);
CA=M(:,4)*1e-12;

subplot(3,1,2)
plot(fA,GA,'k-')
%xlabel('Frequency [Hz]')
str= sprintf('Amplifier Gain [dB]');
ylabel(str)
%axis([0 20 [4 6]*1e-8])
grid on


SdB = SHdB + GA;
S0= 10.^(SdB/20)*S0;

c= CH./(CH+CA);
Sc= S0.*c;

subplot(3,1,3)
plot(fA,Sc,'k-')
xlabel('Frequency [Hz]')
str= sprintf('Total Sensitivity [V/Pa]');
ylabel(str)
%axis([0 20 [4 6]*1e-8])
grid on

 [axpos] = pdffigure_1(6);
 print('-dpdf', 'sensitivity')
 

