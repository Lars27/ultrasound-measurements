function [cw]= SoundVelocitySeawater(T,S,D)
% function cw= SoundVelocity(T,S)
%
% Speed of sound in sea water as function of temperature 
% and salionmity
% Ref. Mackenzie, JASA, 1981
%
% cw   Speed of sound [m/s]
% S    Temperature sensitivity for speed of sound [m/s/C]
%
% T    Temperature [C]
% S    Salinity [parts per 1000]
% D    Depth [m]

% Lars Hoff, HSN, Feb 2016

aT= [ 1448.96;
         4.591
        -5.304e-2
         2.374e-4 ];

aD= [ 0
      1.630e-2
      1.675e-7 ];
  
cw= polyval(flipud(aT),T) + polyval(flipud(aD),D) ...
    +(S-35)*(1.340-1.025e-2*T) -7.139e-13*T*D^3;
    
 return
 
