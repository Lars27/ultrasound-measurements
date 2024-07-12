function animate_DHM
% function animate_DHM
%
% Load intensity and phase data from Koala, Lyncee Tec DHM
% Process raw data in Matlab 
%
% View as animated intensity and deflection images in one figure 
%
% Operation
%   1) Add folder with this function to the Matlab-path
%   2) Move to directory containing results from Koala (format 'yyyy.mm.dd hh-mm-ss')
%   3) Run this file. The program will load and process DHM-results stored in sub-folders 'intensity' and 'phase'
%

% Lars Hoff, USN, 2022. Revised and updated July 2024
%       

%% Parameters for acquisition and display

% Animation
Animation.save= false;           %     Export result to video
Animation.filename= 'test.avi';  %     Name and format of video file 
Animation.framerate= 4;          %     Frame rate of saved video file
Animation.imageinterval= 0.1;    % [s] Animation speed, interval between frames

% Display
Display.removestatic = false;    % Remove static displacements
Display.filterlength = 1;        % 2D lowpass filter length
%Display.viewangle = [-15 50];  % 3D animation view angle
Display.viewangle = [ 0 90];    % Flat from from above, intensity image
Display.colormap= colorbrewerdiverging1;   % Colormap for deflection image
Display.zunit= 1e-9;             % Displacement unit, deflection (z)
Display.xunit= 1e-6;             % Lateral dimension unit (x and y)
Display.zMax= 200;               % [nm] Max displacement scale 
Display.intensityscale = [-20 0];% [dB] Scaling of intensity image

% Analysis. Deflection curves
Deflectioncurve.start= [];
Deflectioncurve.end= [];
Deflectioncurve.color= [];
Deflectioncurve.x= [];   
Deflectioncurve.d= [];
Deflectioncurve.z= [];  
Deflectioncurve.handle= [];

Deflectioncurve(1).start= [ 17 89]*Display.xunit; 
Deflectioncurve(1).end  = [450 25]*Display.xunit;
Deflectioncurve(1).color = 'b';

Deflectioncurve(2).start= [ 17 169]*Display.xunit;
Deflectioncurve(2).end  = [450 105]*Display.xunit;
Deflectioncurve(2).color = 'r';

nDeflectioncurves= length(Deflectioncurve);

% Data from Lyncee DHM used in calculations
DHMdata.source = ' ';
DHMdata.intensity= [];
DHMdata.phase = [];

% Processed results
Image.intensitydb = [];
Image.deflection = [];

if Animation.save
    fprintf('Video exported to %s', Animation.filename)
else
    fprintf('Video not exported')
    
end

%% Load raw data
DHMdata.source= cd;
fprintf('\nLoading raw data from %s', DHMdata.source )

intensitySource = fullfile(DHMdata.source, 'Intensity', 'Float', 'Bin');
DHMdata.intensity= read_dhm('*_intensity.bin' , intensitySource);

[Image.nX, Image.nY, Image.nFrames ] = size(DHMdata.intensity.data);

phaseSource  = fullfile(DHMdata.source, 'Phase', 'Float', 'Bin');
DHMdata.phase = read_dhm('*_phase.bin' , phaseSource);

%% Process raw data
fprintf('\nProcessing raw data. ')
I = 10*log10(DHMdata.intensity.data);    
Image.intensitydb = I-max(I,[],'all');   % Normalised intensity in dB
 
[z,zMax]= calculate_vibration(DHMdata.phase.data, ...
                              DHMdata.phase.dz, ...
                              Display.filterlength, 0, ...
                              Display.removestatic );  % Vibration from phase

Image.deflection = z/Display.zunit;  
Display.zMax=zMax/Display.zunit;

for k=1:nDeflectioncurves
    Deflectioncurve(k)= find_deflectioncurve(Deflectioncurve(k), ...
                                            Image.deflection, ...
                                            DHMdata.phase.dx );
end

%% Plot first images in animation 
Display.xMax= DHMdata.intensity.xMax/Display.xunit;
Display.yMax= DHMdata.intensity.yMax/Display.xunit;
kFrame = 1;

% Intensity 
subplot(2,2,1)
Image.hIntensity=imagesc([0 Display.xMax], [0 Display.yMax], ...
                         Image.intensitydb(:,:,kFrame), ...
                         Display.intensityscale);

Image.hTitle= title(' ');
format_image([0 Display.xMax], [0 Display.yMax], 0, 'Intensity [dB]');
set(Image.hIntensity.Parent, 'Colormap', gray )    

% Mark lines where deflection curves are measured
hold on
for k=1:nDeflectioncurves
    plot( Deflectioncurve(k).x(1,:)/Display.xunit, ...
          Deflectioncurve(k).x(2,:)/Display.xunit, ...
          Color=Deflectioncurve(k).color, LineStyle='-' );

    plot( Deflectioncurve(k).x(1,1)/Display.xunit, ...
          Deflectioncurve(k).x(2,1)/Display.xunit, ...
          Color=Deflectioncurve(k).color, Marker="*" );
end
hold off

% Deflection image
subplot(1,2,2)
xScale= linspace(0, Display.xMax, Image.nX);
yScale= linspace(0, Display.yMax, Image.nY);
[X,Y]= meshgrid(xScale, yScale );

Image.hDeflection= surf(X, Y, Image.deflection(:,:,kFrame), 'edgecolor', 'none');

set(gca, 'View', Display.viewangle); 
set(gca, 'DataAspectRatio',[Display.xMax Display.yMax 3*Display.zMax])

format_image([0 Display.xMax], [0 Display.yMax], Display.zMax, 'Deflection [nm]' )

set(Image.hDeflection.Parent, 'Colormap', Display.colormap )

%% Deflection graph
subplot(2,2,3)
for k=1:nDeflectioncurves
    Deflectioncurve(k).handle= plot(Deflectioncurve(k).d/Display.xunit, ...
                                    Deflectioncurve(k).z(:,kFrame), ...
                                    Color=Deflectioncurve(k).color, ...
                                    LineStyle='-' );
    hold on
end

ylim(Display.zMax*[-1 1])
grid on

xlabel('Position [\mum]')
ylabel('Deflection [nm]')


%% Loop through all frames, update by replacing data in existing image
fprintf('Running animation ... ')

if Animation.save   % Set up video recorder
    v= VideoWriter(Animation.filename);
    v.FrameRate= Animation.framerate;
    open(v);
end

for kFrame= 1:Image.nFrames
    Image.hIntensity.CData= Image.intensitydb(:, :, kFrame);
    Image.hDeflection.ZData= Image.deflection(:, :, kFrame);

    for k=1:nDeflectioncurves
        Deflectioncurve(k).handle.YData= Deflectioncurve(k).z(:,kFrame);
    end
            
   Image.hTitle.String=sprintf('%d of %d', kFrame, Image.nFrames);

    if Animation.save
        frame= getframe(gcf);
        writeVideo(v,frame);
    else
        pause(Animation.imageinterval)
    end
end

if Animation.save
    close(v);
end
fprintf('\nFinished\n')

end
