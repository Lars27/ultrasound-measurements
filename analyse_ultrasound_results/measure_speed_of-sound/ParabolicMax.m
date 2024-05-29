function kimax=ParabolicMax(y, check)
% function kimax=ParabolicMax(y, check)
%
% Find position of maximum of curve y.
% Subsample-interpolation by parabolic fit

% Lars Hoff, USN, July 2019

if nargin<2, check=0; end

[~, kmax]= max(y);
yz=y(kmax+(-1:1) );

c = yz(2);               % Fit polynomial y=ax^2 + bx + c
a= (yz(3)+yz(1))/2-c;    % Analytic solution for three points around max
b= (yz(3)-yz(1))/2;

kzmax=-b/(2*a);
kimax= kzmax+kmax;

if check  % Plot result for check              
    n=linspace(-3,3,1000);
    yn=a*n.^2+b*n+c;
    plot(n+kmax,yn, 'b-', kmax+(-1:1), yz, 'bo')
end

end
 