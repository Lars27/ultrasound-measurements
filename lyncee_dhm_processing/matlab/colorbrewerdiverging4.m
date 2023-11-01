function map = colorbrewerdiverging4(m)
%colorbrewerdiverging4 Color map from Color Brewer 2.0
%   Diverging-type map made for data sets centered around a midpoint 
%   White is neutral, negative go towards purple, positive towards tan
%
%   Returns a colormap with the same number of colors as the current
%   figure's colormap. If no figure exists, MATLAB uses the length of the
%   default colormap.
%
%   EXAMPLE
%
%   This example shows how to reset the colormap of the current figure.
%
%       colormap(colorbrewerdiverging4)
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
127,59,8
179,88,6
224,130,20
253,184,99
254,224,182
247,247,247
216,218,235
178,171,210
128,115,172
84,39,136
45,0,75 
];
values=flipud(values)/256;

P = size(values,1);
map = interp1(1:size(values,1), values, linspace(1,P,m), 'linear');
