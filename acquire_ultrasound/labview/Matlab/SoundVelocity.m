function [cw S]= SoundVelocity(T)
% function cw= SoundVelocity(T)
%
% Speed of sound in pure water as function of temperature 
% Ref. Del Grosso, JASA, 1972
%
% cw   Speed of sound [m/s]
% S    Temperature sensitivity for speed of sound [m/s/C]
% T    Temperature [C]

% Lars Hoff, HSN, Feb 2016

k = [0.140238754e4
     0.503711129e1
    -0.580852166e-1
     0.334198834e-3
    -0.147800417e-5
     0.314643091e-8 ]; % Del Grosso 1972, Table III, col. 4
 
 kd= [1:length(k)-1]'.*k(2:end);  % Derivatives polynomial
   
 cw= polyval(flipud(k) ,T);    % m/s    Speed of sound
 S = polyval(flipud(kd) ,T);    % m/s/C  Sensitivity, speed of sound vs. temperature
 
 return
 
