function Deflectioncurve = find_deflectioncurve(Deflectioncurve, z, pixelSize)
% function Deflectioncurve = find_deflectioncurve(Deflectioncurve, z, pixelSize)
%
% Define line in 2D image
% Find pixel positions and z-values along line

% Lars Hoff, USN, 2022


%% Find indices of line
[pxMax, pyMax, frameMax] = size(z);
pStart = findIndex(Deflectioncurve.start, pixelSize, [1 pxMax]);
pEnd = findIndex(Deflectioncurve.end, pixelSize, [1 pyMax]);
nDeflectionpoints =max(abs(pEnd-pStart));

for k=1:2       % Indices of points to calculate deflectioncurves
    p(k,:)= round(linspace(pStart(k), pEnd(k), nDeflectionpoints));
end
x= p*pixelSize;               % [m]  Lateral position of deflectioncurves
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

function p= findIndex(x, pixelSize, pixelLim )
p= round(x/pixelSize);

p(p<min(pixelLim))= min(pixelLim);
p(p>max(pixelLim))= max(pixelLim);

end