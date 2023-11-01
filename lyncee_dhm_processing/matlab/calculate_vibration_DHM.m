function [z, zmax] = calculate_vibration_DHM(phi, hconv, L, dynamic)
% function [z, zmax] = calculate_vibration_DHM(phi, hconv, L, dynamic)
%
% Calculate vertical vibration from phase data
% Lyncee Tec DHM
%
%      phi  Phase data from DHM [radians]
%    hconv  Conversion factor, radians to m
%        L  Spatial averaging filter length, 2D filter
%  dynamic  Remove static displacement to visualise motion (default)
%
%        z  Vertical deflection [m]
%     zmax  Max vertical deflection (aliasing limit)
%
% Requires 
%   Image Processing Toolbox   for 2D median filter
%   signal Processing Toolbox  for 2D linear filter

% Lars Hoff, USN, 2022

if nargin<4
    dynamic = 1;
end

[w,h,n] = size(phi);

%% Calculate vertical deflection 
if dynamic % Remove static displacements
    phim = mean(phi,3);
    phim = repmat(phim,1,1,n);
    phi = phi-phim;    % Phase after removing static deflection
end
z    = phi*hconv;   % [m] Deflection 
zmax = pi*hconv;    % Displacement axis scale (aliasing limit). Max phase shift is pi radians

%% Filters
% Median filter to remove outliers   
fprintf('Median filter ... ')
M = 3;          
for k=1:n
    z(:,:,k)=medfilt2(z(:,:,k), [M,M]);
end

% Linear 2D filter for lateral smoothing
fprintf('Low pass filter ... ')
b = ones(L,L);    % Running average filter
%b = conv2(b,b);  % Activate to create tapered filter
b = b/sum(sum(b));
for k=1:n
    z(:,:,k)=filter2( b, z(:,:,k) );
end

end
 