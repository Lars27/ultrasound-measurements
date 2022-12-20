function plotsignals(src)

wfm= readwfm(src);
v = double(wfm.v);

fs= 1/wfm.dt;
fc= 5.0e6*[0.01 3];
wc= fc/(fs/2);
[b,a]=butter(4,wc);
vf=filtfilt(b,a,v);

t=wfm.t0+(0:wfm.Np-1)*wfm.dt;

plot(t,vf)
xlabel('Time [\mus]')
ylabel('Voltage [V]')
grid on
legend('Ch 0','Ch 1','Location','NorthEast')
title(src, 'Interpreter','None')

end
