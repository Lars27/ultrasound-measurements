function PlotBeamshapeAxial(src,fc,axname,shift,printresult)
% function PlotBeamshapeAxial(src,fc,printresult)
% 
% Load and plot result of Onda AIAMS III beam profile measurement
% 

if nargin<5,     printresult=0; end
if nargin<4,     shift=0; end
if nargin<3,     axname='x';       end

[srcpath, srcname, srcext]= fileparts(src);

%-- Load raw data from AIMS III
load(src);
%t=[0:Nt-1]/fs;

[vf, PdB]= BeamIntensity(Waveforms, fc, fs);

% Empirical correction for appearent 'hysteresis' of backward-going scans latereal motion
if shift>0
    b(2)= shift;
    b(1)= 1-b(2);
    PdB(:, 2:2:end)= filter(b,1,PdB(:, 2:2:end));
elseif shift<0
    b(2)= -shift;
    b(1)= 1-b(2);
    PdB= flipud(PdB);    
    PdB(:, 2:2:end)= filter(b,1,PdB(:, 2:2:end));
    PdB= flipud(PdB);        
end

x=linspace(X.low_pos,X.high_pos,X.points_num);
z=linspace(Z.low_pos,Z.high_pos,Z.points_num);

%--- Axial Beam profile, intensity plot ---
figure(1)
imagesc( x,z,PdB', [-50 0]); 
colormap(jet)
xlabel(sprintf('%s [mm]', axname));
ylabel('z [mm]')
c=colorbar;
ylabel(c, 'Pulse energy [dB re max]')
axis('equal');
xmax= max(abs(x));
axis([xmax*[-1 1] min(z) max(z)]);

pdffigure(1);
if printresult
    print('-dpdf', sprintf('intensity_%s', srcname));
end


%=== Beam profiles ===
[Pmax n] = max(PdB(:));
[kx0 ky0] = ind2sub(size(PdB),n);

%--- Plot lateral beam profiles at selected depths ---
figure(2)
clf

zr= [40:20:100];        % mm   Depths to plot beam profile
kr=zeros(size(zr));
symb= {'b-','r-', 'k-', 'g-'};
for k=1:length(zr)
    tmp = abs(z-zr(k));
    [dz,kr] = min(tmp);

    Pcx = PdB(:, kr);
    Pcx=Pcx-max(Pcx);

    plot(x,Pcx,symb{k} )
    hold on
    leg{k}= sprintf('z= %.f mm', z(kr));
end
grid on
hold off
ylabel('Pulse energy [dB re max at depth]')
xlabel(sprintf('Lateral position (%s) [mm]', axname));
axis([30*[-1 1] -20 0]);
yticks([-60:2:0])
legend(leg)

pdffigure(5);
if printresult
    print('-dpdf', sprintf('lateralprofile_%s', srcname))
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



