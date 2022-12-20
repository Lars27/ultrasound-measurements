function par=FindSpeedofSound(src,swap)
% function par=FindSpeedofSound(parfile,swap)
%
% Find Speed of Sound
% Load measured traces, calculate speed of sound by different methods 

if nargin<2, swap=0; end

par=readpar(src);              % Read measurement parameters
   
figure(1)
par= timedifference(par,swap);  % Difference in arrival times
figure(2)
par= timedelay(par,swap);       % Cross-correlation inside sample

ds=par.ds*1e-3;                   % m     Distance through sample
par.csp= ds./(par.dtp+ds/par.cw); % m/s  Speed of sound from propagation time difference
par.csr= 2*ds./par.dtr;           % m/s  Speed of sound from reverberations inside sample

par.Zsp = par.rho*par.csp*1e-6;   % Rayl Characteristic acoustic impedance
par.Zsr = par.rho*par.csr*1e-6;
    
fprintf('\nSpeed of sound in sample')
fprintf('\nPropagation time difference: c=%.0f m/s',par.csp)
fprintf('\nReverberations inside sample: ')
fprintf('c=%.0f m/s   ',par.csr)
fprintf('\n')

return