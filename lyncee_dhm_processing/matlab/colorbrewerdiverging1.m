function map = colorbrewerdiverging1(m)
%colorbrewerdiverging1 Color map from Color Brewer 2.0
%   Diverging-type map made for data sets centered around a midpoint 
%   White is neutral, negative go towards dark green, positive towards dark
%   brown
%
%   Returns a colormap with the same number of colors as the current
%   figure's colormap. If no figure exists, MATLAB uses the length of the
%   default colormap.
%
%   EXAMPLE
%
%   This example shows how to reset the colormap of the current figure.
%
%       colormap(colorbrewerdiverging1)
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
84,48,5
140,81,10
191,129,45
223,194,125
246,232,195
245,245,245
199,234,229
128,205,193
53,151,143
1,102,94
0,60,48   
];
values=flipud(values)/256;

P = size(values,1);
map = interp1(1:size(values,1), values, linspace(1,P,m), 'linear');
