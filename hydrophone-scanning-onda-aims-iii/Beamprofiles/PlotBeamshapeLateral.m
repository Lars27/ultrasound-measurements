function PlotBeamshapeLateral(src,fc,printresult)
% function PlotBeamshape(rawdatafile,printresult)
% 
% Load and plot result of Onda AIAMS III beam profile measurement
% 

if nargin<2
    printresult=0;
end

[srcpath, srcname, srcext]= fileparts(src);

%-- Load raw data from AIMS III
load(src);
[vf, PdB ]= BeamIntensity(Waveforms, fc, fs);

vmax= max(max(max(abs(vf))));

%--- Plot intensities 
x=linspace(X.low_pos,X.high_pos,X.points_num);
y=linspace(Y.low_pos,Y.high_pos,Y.points_num);

%--- Lateral Beam profile, intensity plot ---
figure(1)
imagesc( x,y,PdB', [-50 0]); 
colormap(jet)
%colormap(gray(256));
xlabel('x [mm]')
ylabel('y [mm]')
c=colorbar;
ylabel(c, 'Pulse energy [dB re max]')
axis('equal');
xmax= max([abs(x) abs(y)]);
axis(xmax*[-1 1 -1 1]);

%--- Contour plots
hold on
contour( x,y,PdB', -6*[1 1],'k-');
contour( x,y,PdB', -20*[1 1],'k-');
hold off

pdffigure(21);
if printresult
     print('-dpdf', sprintf('lateralintensity_%s', srcname))
end


%--- Beam profiles through center 
ky0 = find(y==0);
kx0 = find(x==0);

[Pmax n] = max(PdB(:));
[kx0 ky0] = ind2sub(size(PdB),n);

%--- Plot lateral beam profiles
figure(2)
clf
Pcx = PdB(:, ky0);
Pcy = PdB(kx0,:);

plot(x,Pcx,'b-', y,Pcy,'r-' )

x6=BeamLimits(Pcx,x,ky0,'b',1);
text(x6(2), -4.0, sprintf('%.1f mm', diff(x6)),'color', 'b');
x6=BeamLimits(Pcy,y,kx0,'r',2);
text(x6(2), -8.0, sprintf('%.1f mm', diff(x6)),'color', 'r');

grid on
ylabel('Pulse energy [dB re max]')
xlabel('Lateral position (x and y) [mm]')
axis([xmax*[-1 ] 69 -50 0]);
set(gca, 'ytick', [-60:5:0])

% axes('position',[0.69 0.69 .20 .20])
% plot(x,Pcx,'b-', y,Pcy,'r-' )
% set(gca, 'color', 1*[1 1 1])
% grid on
% axis([10*[-1 1] -8 0]);
% set(gca, 'xtick', [-20:5:20])

pdffigure(5);
if printresult
    print('-dpdf', sprintf('lateralprofile_%s', srcname))
end

%--- Wavefield plots
figure(3)
v=squeeze(Waveforms(:,ky0,:))';
vmax=max(max(abs(v)));
Nt= length(v);
t =[0:Nt-1]/fs;
imagesc( x,t*1e6,v, vmax*[-1 1]); 
set(gca,'ydir','normal');
colormap(gray(256));
xlabel('x [mm]')
ylabel('Time [us]')
axis([xmax*[-1 1] 0 max(t*1e6)/2 ] );

pdffigure(1);
if printresult
    wavefieldfile= sprintf('wavefield_%s', srcname)
    print('-dpdf', wavefieldfile )
end

%--- Plot received pulse ---
figure(4)
v=squeeze(Waveforms(kx0,ky0,:));

[PdB,f]=PlotPulse(t,v, [0 35]*1e-6);

%--- Plot figure ---
[axpos] = pdffigure(21);
if (printresult)
    pulsefile= sprintf('receivedpulse_%s', srcname)
    print('-dpdf', pulsefile )
end

end


%--- Beam limits ---

function xlim=BeamLimits(Pc,x,k0,c,p)
Plim=-6;
xmin=interp1(Pc(1:k0),  x(1:k0),  Plim,'pchip');
xmax=interp1(Pc(k0:end),x(k0:end),Plim,'pchip');
xlim= [xmin xmax];
hold on
plot(xlim,Plim*[1 1], 'x-', 'color', c)
%text(xmax, Plim, sprintf('%.0f dB limit. %.1f mm', Plim, diff(xlim)));
%text(xlim(p), Plim, sprintf('%.1f mm', diff(xlim)),'color', c);
hold off
end



