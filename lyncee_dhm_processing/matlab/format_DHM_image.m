function format_DHM_image( xrange, yrange, zscale, ztext )
% function format_DHM_image( xrange, yrange, zscale, ztext )
%
% Format axes for image from Lyncee Tec DHM
%
%  xrange  Max on x-axis, min ia always 0
%  yrange  Max on y-axis, min ia always 0
%  zscale  z-axis scale, -zscale to +zscale
%   ztext  Label on z-axis and color bar

% Lars Hoff, USN, 2022

if nargin<4
    ztext ='';
end

cb= colorbar;
cb.Label.String = ztext;   

%% Format as 3D surface if z-scale exists, 2D intensity image if not
if zscale>0    
    zlim(zscale*[-1 1])
    set(gca,'clim', zscale*[-1 1])
    zlabel(ztext)
else           
    set(gca,'YDir','normal') 
    axis('equal')
end

%% Axis scales and labels
xlim(xrange)
ylim(yrange)

xlabel('Width [\mum]')
ylabel('Height [\mum]')

end
