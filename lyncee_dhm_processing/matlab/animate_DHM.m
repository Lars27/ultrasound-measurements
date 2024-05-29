function animate_DHM
% function animate_DHM
%
% Load intensity and phase data from Koala, Lyncee Tec DHM
% Process raw data in Matlab 
%
% View as animated intensity and deflection images in one figure 
%
% Add folder to the Matlab-path
% Move to directory containing results from Koala (format 'yyyy.mm.dd hh-mm-ss')
% The program will load and process results from sub-folders 'intensity' and 'phase'
%

% Lars Hoff, USN, 2022

global CONTINUE    % Controls animation loop

%% Parameters for acquisition and display

writevideo = 0;                  % Export result to video
videofile  = 'Butterfly_1.avi';  % Name and format of videop file 

dynamic       = 0;          % Remove static displacements
filterorder   = 3;          % 2D lowpass filter length
%viewangle     = [-15 50];   % 3D animation view angle
viewangle     = [ 0 90];    % View from above, like intensity image
imageinterval = 0.3;        % [s] Animation speed as pause between frames

ys    = [ 650 950 ;  50 400 ]*1e-6;   % y-rangefor deflection measurement lines
xs    = [ 500 490 ; 520 490 ]*1e-6;   % x-range for deflection measurement lines
zscale= 200;                % [nm] Max displacement scale 
deflectioncolor = colorbrewerdiverging1;   % Colormap for deflection imagex

zunit= 1e-9;   % Displacement unit, nanometer
xunit= 1e-6;   % Lateral image unit, micrometer

%% Load raw data
fprintf('Video export %d. ', writevideo)
fprintf('Loading raw data ... ')

srcpath  = fullfile(cd, 'Intensity', 'Float', 'Bin');
intensity= read_DHM('*_intensity.bin' , srcpath);

srcpath = fullfile(cd, 'Phase', 'Float', 'Bin');
phase   = read_DHM('*_phase.bin' , srcpath);

%% Process raw data
fprintf('Processing ... ')
I = 10*log10(intensity.data);    % Intensity in dB
I = I-max(I,[],'all');           % Normalise to max over all values, space and time
 
[z,zmax] = calculate_vibration_DHM( phase.data, phase.hconv, filterorder, dynamic );  % Vibration from phase
z = z/zunit;                     % Scale deflection to selected unit 
zmax=zmax/zunit;

[w,h,n] = size(I);

%% Setup image
% Load first image frame to define image dimensions
Xmax= intensity.xmax/xunit;
Ymax= intensity.ymax/xunit;

% Intensity image
subplot(1,2,1)
h_int=imagesc( [0 Xmax], [0 Ymax], I(:,:,1), [-15 0]);

format_DHM_image( [0 Xmax], [0 Ymax], 0, 'Intensity [dB]' );
ttl= title(' ');

%% Deflection along selected line
[ms,ns] = size(xs);
col= {'r', 'b'};
hold on
for k=1:ms
    [Xsi, Ysi, Xdi, zs{k} ] = find_deflectionline( xs(k,:), ys(k,:), z, phase.pxsize );
    Xs{k}= Xsi/xunit;
    Ys{k}= Ysi/xunit;
    Xd{k}= Xdi/xunit;
    plot( Xs{k},    Ys{k},    'color', col{k}, 'LineStyle', '-' )
    plot( Xs{k}(1), Ys{k}(1), 'color', col{k}, 'Marker',    '*' );
end

%% Deflection image
subplot(2,2,2)
[X,Y] = meshgrid( linspace( 0, Xmax, w ), linspace( 0, Ymax, h ) );
h_vib= surf(X,Y, z(:,:,1), 'edgecolor', 'none');
set(gca, 'View', viewangle); 
set(gca,'DataAspectRatio',[Xmax Ymax 3*zscale])

format_DHM_image( [0 Xmax], [0 Ymax], zmax, 'Deflection [nm]' )
title('s: Stop    x: Quit    c: Continue')

set(h_int.Parent, 'Colormap', gray )            % May cause Matlab warning,
set(h_vib.Parent, 'Colormap', deflectioncolor ) % not critical, may be bug in Matlab

%% Deflection graph
subplot(2,2,4)
for k=1:ms
    h_zline(k)= plot( Xd{k}, zs{k}(:,1), 'color', col{k}, 'LineStyle', '-' );
    hold on
end
hold off
ylim(zmax*[-1 1])
grid on

xlabel('x-position [\mum]')
ylabel('Deflection [nm]')

set(gcf,'KeyPressFcn',@keypress);

%% Loop through all frames, update by replacing z-data
fprintf('Running animation ... ')
CONTINUE = 'c';
k=1;

if writevideo
    v = VideoWriter(videofile);
    v.FrameRate=4;
    open(v);
end

while not(CONTINUE=='x')
    switch CONTINUE
        case 'x', break   % Exit program
        case 's'          % Do not update, i.e. freeze image
        otherwise         % Any other key resumes animation
            h_int.CData  = I( :, :, k );
            h_vib.ZData  = z( :, :, k );

            for m=1:ms
                h_zline(m).YData= zs{m}(:,k);
            end
            
            ttl.String=sprintf('%d of %d', k, n);

            k=k+1;
            if writevideo
                if k>n, CONTINUE='x'; end  % Run through loop once
            else
                if k>n, k=1; end           % Restart loop until stopped
            end
    end
    if writevideo
        frame = getframe(gcf);
        writeVideo(v,frame);
    else
        pause(imageinterval)
    end
end
if writevideo
    close(v);
end
fprintf('Finished\n')

end

%% Local functions

% Start and stop animation
function keypress( src, event )
    global CONTINUE
    CONTINUE= lower( event.Key );
end