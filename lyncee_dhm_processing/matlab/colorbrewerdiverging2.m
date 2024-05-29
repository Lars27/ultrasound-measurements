function map = colorbrewerdiverging2(m)
% colorbrewerdiverging2 Color map from Color Brewer 2.0
%   Diverging-type map made for data sets centered around a midpoint 
%   White is neutral, negative go towards  green, positive towards pink
%
%   Returns a colormap with the same number of colors as the current
%   figure's colormap. If no figure exists, MATLAB uses the length of the
%   default colormap.
%
%   EXAMPLE
%
%   This example shows how to reset the colormap of the current figure.
%
%       colormap(colorbrewerdiverging2)
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
142,1,82
197,27,125
222,119,174
241,182,218
253,224,239
247,247,247
230,245,208
184,225,134
127,188,65
77,146,33
39,100,25
];
values=flipud(values)/256;

P = size(values,1);
map = interp1(1:size(values,1), values, linspace(1,P,m), 'linear');
