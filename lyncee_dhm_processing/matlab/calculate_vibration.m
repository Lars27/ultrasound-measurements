function [z, zmax] = calculate_vibration(phase, dz, filterL, medianM, removeStatic)
%function [z, zmax] = calculate_vibration(phase, dz, filterL, medianM, removeStatic)
%
% Calculate vertical vibration from phase data
% Lyncee Tec DHM
%
%          phase  Phase data from DHM [radians]
%             dz  Conversion factor, radians to m
%        medianM  Spatial averaging median filter length, 2D filter
%        filterL  Spatial averaging filter length, 2D filter
%   removeStatic  Remove static displacement to visualise motion (default)
%
%        z  Vertical deflection [m]
%     zmax  Max vertical deflection (aliasing limit)
%
% Requires 
%   Image Processing Toolbox   for 2D median filter
%   Signal Processing Toolbox  for 2D linear filter

% Lars Hoff, USN, 2022

if nargin<5
    removeStatic = 0;
end

[~,~,nFrames] = size(phase);

%% Calculate vertical deflection 
if removeStatic % Remove static displacements
    phaseMean= mean(phase,3);
    phaseMean= repmat(phaseMean, 1, 1, nFrames);
    phase= phase-phaseMean;    % Phase after removing static deflection
end
z= phase*dz;   % [m] Deflection 
zmax= pi*dz;    % Displacement axis scale (aliasing limit). Max phase shift is pi radians

%% Filters
% Median filter to remove outliers   
if medianM>0
    fprintf('Median filter ... ')
    for k=1:nFrames
        z(:,:,k)=medfilt2(z(:,:,k), [medianM, medianM]);
    end
end

% Linear 2D filter for lateral smoothing
fprintf('Low pass filter ... ')
b= ones(filterL, filterL);    % Running average filter
b= b/sum(sum(b));
for k=1:nFrames
    z(:,:,k)=filter2(b,z(:,:,k));
end

end
 