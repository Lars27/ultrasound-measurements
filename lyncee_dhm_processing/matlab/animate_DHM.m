function animate_dhm
% function animate_dhm
%
% Load intensity and phase data from Koala, Lyncee Tec DHM
% Process raw data in Matlab 
%
% View as animated intensity and deflection images in one figure 
%
% Operation
%   1) Add folder with this function to the Matlab-path
%   2) Move to directory containing results from Koala (folder name format 'yyyy.mm.dd hh-mm-ss')
%   3) Run this file. The program will load and process DHM-results stored in sub-folders 'intensity' and 'phase'
%

% Lars Hoff, USN, 2022. Revised and updated July 2024
%       

curveColor = colororder;

%% Parameters for acquisition and display
% Animation
Animation.save= false;           %     Export result to video
Animation.framerate= 4;          %     Frame rate of saved video file
Animation.imageinterval= 0.1;    % [s] Animation speed, interval between frames

% Display
Display.removestatic= true;    % Remove static displacements
Display.medianfilter= 0;       % 2D median filter length
Display.filterlength= 5;        % 2D lowpass filter length
Display.viewangle= [-15 50];  % 3D animation view angle
%Display.viewangle= [ 0 90];    % View flat from from above, intensity image
%Display.colormap= colorbrewerdiverging1;   % Colormap for deflection image
Display.colormap= colorbrewerdiverging5;   % Colormap for deflection image
Display.zunit= 1e-9;             % Displacement unit, deflection (z)
Display.xunit= 1e-6;             % Lateral dimension unit (x and y)
Display.zMax= 25;                 % [nm] Max displacement scale. 0 for full scale 
Display.offset= -0;             % [nm] Offset for z-axis   
Display.intensityscale = [-12 0];% [dB] Scaling of intensity image

% Analysis. Deflection curves
Deflectioncurve.start= [];  % Start of deflection curve, lateral coordinates 
Deflectioncurve.end= [];    % End of deflection curve, lateral coordinates 
Deflectioncurve.color= [];  % Colors of deflection curves
Deflectioncurve.x= [];      % Lateral coordinates for deflection curve 
Deflectioncurve.d= [];      % Distance along deflection curve 
Deflectioncurve.z= [];      % Deflection along deflection curve 

kCurve=1;
curveStart(kCurve,:)= [  0  90]; 
curveEnd(kCurve,:)  = [482  15];

kCurve=kCurve+1;
curveStart(kCurve,:)= [  0 240]; 
curveEnd(kCurve,:)  = [482 165];

kCurve=kCurve+1;
curveStart(kCurve,:)= [  0 165];
curveEnd(kCurve,:)  = [482  90];

kCurve=kCurve+1;
curveStart(kCurve,:)= [114   0];
curveEnd(kCurve,:)  = [182 480];

nDeflectioncurves= kCurve;

for kCurve=1:nDeflectioncurves
    Deflectioncurve(kCurve).color = curveColor(kCurve,:);
    Deflectioncurve(kCurve).start= curveStart(kCurve,:) *Display.xunit;
    Deflectioncurve(kCurve).end= curveEnd(kCurve,:) *Display.xunit;
end

%% Parameters read from data files, do not change
% Configuration parameters read from strobosetup.xml
Configuration.filename= 'strobosetup.xml';
Configuration.name= [];
Configuration.samplesPeriod= 0;
Configuration.frequency= 0;
Configuration.dutycycle= 0;
Configuration.waveform= '';

Configuration = read_dhm_configuration(Configuration);
configurationText= sprintf(...
    'Configuration %s. Frequency %4.4f MHz, %d samples/period', ...
    Configuration.name, ...
    Configuration.frequency/1e6, ...
    Configuration.samplesPeriod);

fprintf(configurationText)   
fprintf('\n')   

% Data from Lyncee DHM used in calculations
dhmData.source= cd;
dhmData.intensity= [];
dhmData.phase= [];

% Processed results
Image.intensitydb= [];
Image.deflection= [];

% Start loading 
if Animation.save
    folderName = get_dhm_folder(cd);
    if Display.removestatic
        folderName= append(folderName,'-ac');
    end
    Animation.filename= append( folderName,'.avi');
    fprintf('Video exported to %s', Animation.filename)
else
    fprintf('Video not exported')   
end

%% Load raw data
fprintf('\nLoading raw data from %s', dhmData.source )

fprintf('\nIntensity image ... ' )
intensitySource= fullfile(dhmData.source, 'Intensity', 'Float', 'Bin');
dhmData.intensity= read_dhm('*_intensity.bin' , intensitySource);
[Image.nX, Image.nY, Image.nFrames ]= size(dhmData.intensity.data);

fprintf('Phase data' )
phaseSource  = fullfile(dhmData.source, 'Phase', 'Float', 'Bin');
dhmData.phase = read_dhm('*_phase.bin' , phaseSource);

%% Process raw data
fprintf('\nProcessing raw data. ')
I= 10*log10(dhmData.intensity.data);    
Image.intensitydb= I-max(I,[],'all');   % Normalised intensity in dB
 
[z,zMax]= calculate_vibration(dhmData.phase.data, ...
                              dhmData.phase.dz, ...
                              Display.filterlength, Display.medianfilter, ...
                              Display.removestatic );  % Vibration from phase
Image.deflection = z/Display.zunit;

if not(Display.removestatic)
    Image.deflection  = Image.deflection - Display.offset;  
end
if Display.zMax==0
    Display.zMax=zMax/Display.zunit;
end
for k=1:nDeflectioncurves    
    Deflectioncurve(k)= find_deflectioncurve(Deflectioncurve(k), ...
                                            Image.deflection, ...
                                            dhmData.phase.dx );
end

%% Plot first images in animation 
Display.xMax= dhmData.intensity.xMax/Display.xunit;
Display.yMax= dhmData.intensity.yMax/Display.xunit;
kFrame = 1;

% Intensity image
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
          Color=Deflectioncurve(k).color, Marker="o" );
end
hold off

% Deflection image
subplot(1,2,2)
xScale= linspace(0, Display.xMax, Image.nX);
yScale= linspace(0, Display.yMax, Image.nY);
[X,Y]= meshgrid(xScale, yScale );

Image.hDeflection= surf(X, Y, Image.deflection(:,:,kFrame), 'edgecolor', 'none');

set(gca, 'View', Display.viewangle); 
set(gca, 'Zdir', 'reverse')
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
set(gca, 'Ydir', 'reverse')
hold off

%% Loop through all frames, update by replacing data in existing image
fprintf('Running animation ... ')
if Animation.save   % Set up video recorder
    resultVideo= VideoWriter(Animation.filename);
    resultVideo.FrameRate= Animation.framerate;
    open(resultVideo);
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
        writeVideo(resultVideo,frame);
    else
        pause(Animation.imageinterval)
    end
end

if Animation.save
    close(resultVideo);
end
fprintf('\nFinished\n')

end
