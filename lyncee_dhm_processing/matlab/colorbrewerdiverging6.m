function map = colorbrewerdiverging6(m)
%colorbrewerdiverging6 Color map from Color Brewer 2.0
%   Diverging-type map made for data sets centered around a midpoint 
%   White is neutral, negative go towards dark blue, positive towards dark
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
%       colormap(colorbrewerdiverging6)
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
165,0,38
215,48,39
244,109,67
253,174,97
254,224,144
255,255,191
224,243,248
171,217,233
116,173,209
69,117,180
49,54,149
];
values=flipud(values)/256;

P = size(values,1);
map = interp1(1:size(values,1), values, linspace(1,P,m), 'linear');
