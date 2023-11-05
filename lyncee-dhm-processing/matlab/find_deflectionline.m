function [Xs, Ys, Xd, zs ] = find_deflectionline( x, y, z, pxsize )
% function [Xs, Ys, Xd, zs ] = find_deflectionline( x, y, pxsize )
%
% Define line in 2D image
% Find pixel positions and z-values along line

% Lars Hoff, USN, 2022


%% Find indices of line
[nx, Nx]= find_N( x, pxsize );
[ny, Ny]= find_N( y, pxsize );
Nd = max( [Nx, Ny]);

nxs = round( linspace( nx(1), nx(2), Nd ) );
nys = round( linspace( ny(1), ny(2), Nd ) );

%% Scale to coordinates, 2D image and along line
Xs = nxs*pxsize;
Ys = nys*pxsize;
Xd = sqrt( ( Xs-Xs(1) ).^2 + ( Ys-Ys(1) ).^2 );

%% Find deflection values
[ ~, ~,n]= size(z);
zs= zeros( Nd, n );
for k=1:Nd
    zs(k,:) = z( nys(k), nxs(k), :);   
end

end

%% Internal functions
function [n, N]= find_N( x, pxsize )
n = round( x/pxsize );

N = max(n) - min(n) + 1 ;

end