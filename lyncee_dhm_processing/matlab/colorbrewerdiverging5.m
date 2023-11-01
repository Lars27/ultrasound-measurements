function map = colorbrewerdiverging5(m)
%colorbrewerdiverging5 Color map from Color Brewer 2.0
%   Diverging-type map made for data sets centered around a midpoint 
%   Yellow is neutral, negative go towards dark blue, positive towards dark
%   red
%
%   Returns a colormap with the same number of colors as the current
%   figure's colormap. If no figure exists, MATLAB uses the length of the
%   default colormap.
%
%   EXAMPLE
%
%   This example shows how to reset the colormap of the current figure.
%
%       colormap(colorbrewerdiverging5)
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
103,0,31
178,24,43
214,96,77
244,165,130
253,219,199
247,247,247
209,229,240
146,197,222
67,147,195
33,102,172
5,48,97
];
values=flipud(values)/256;

P = size(values,1);
map = interp1(1:size(values,1), values, linspace(1,P,m), 'linear');
