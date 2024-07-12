function Deflectioncurve = find_deflectioncurve(Deflectioncurve, z, pxsize)
% function Deflectioncurve = find_deflectioncurve(Deflectioncurve, z, pxsize)
%
% Define line in 2D image
% Find pixel positions and z-values along line

% Lars Hoff, USN, 2022


%% Find indices of line
pStart = findIndex(Deflectioncurve.start, pxsize);
pEnd = findIndex(Deflectioncurve.end, pxsize);
nDeflectionpoints =max(abs(pEnd-pStart));

for k=1:2       % Indices of points to calculate deflectioncurves
    p(k,:)= round(linspace(pStart(k), pEnd(k), nDeflectionpoints));
end
x= p*pxsize;                  % [m] Lataral position of deflectioncurves
d=sqrt(sum((x-x(:,1)).^2));   % [m]  Distance along deflection curve
 
%% Find deflection values
[~, ~, nFrames]= size(z);
deflection= zeros(nDeflectionpoints, nFrames);
for k=1:nDeflectionpoints
    deflection(k,:) = z(p(2,k), p(1,k), :);       
end

Deflectioncurve.x= x;   
Deflectioncurve.d= d;
Deflectioncurve.z= deflection;   

end

function [n, N] = findIndex(x, pxsize)
n= round(x/pxsize);
N= max(n)-min(n)+1 ;
end