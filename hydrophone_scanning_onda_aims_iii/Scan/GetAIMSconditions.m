function y= GetAIMSconditions
% function y= GetAIMSconditions
%

y.temp = calllib ('SoniqClient','GetTemperature');
y.c    = calllib ('SoniqClient','GetVelocity');
y.delay= calllib ('SoniqClient','GetDistanceTrackingDelay')*1e-6;
end