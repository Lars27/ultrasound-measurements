function map = colorbrewerdiverging3(m)
% colorbrewerdiverging3 Color map from Color Brewer 2.0
%   Diverging-type map made for data sets centered around a midpoint 
%   White is neutral, negative go towards dark green, positive towards
%   violet
%
%   Returns a colormap with the same number of colors as the current
%   figure's colormap. If no figure exists, MATLAB uses the length of the
%   default colormap.
%
%   EXAMPLE
%
%   This example shows how to reset the colormap of the current figure.
%
%       colormap(colorbrewerdiverging3)
%
%   Function based on Matlab's perula, The MathWorks, Inc.
%   Color map values from https://colorbrewer2.org/#

%   Lars Hoff, USN, 2021

if nargin < 1
   f = get(groot,'CurrentFigure');
   if isempty(f)
      m = size(get(groot,'DefaultFigureColormap'),1);
   else
      m = size(f.Colormap,1);
   end
end

values = [
64,0,75
118,42,131
153,112,171
194,165,207
231,212,232
247,247,247
217,240,211
166,219,160
90,174,97
27,120,55
0,68,27  
];
values=flipud(values)/256;

P = size(values,1);
map = interp1(1:size(values,1), values, linspace(1,P,m), 'linear');
