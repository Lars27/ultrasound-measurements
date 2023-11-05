function plotssignals(usfile)

wfm= readwfm(usfile);
v = double(wfm.v);

fs= 1/wfm.dt;
fc= 5.0e6*[0.01 5];
wc= fc/(fs/2);
[b,a]=butter(4,wc);
vf=filtfilt(b,a,v);

t=wfm.t0+(0:wfm.Np-1)*dt;

plot(t,v,t,vf),
xlabel('Time [\mu s]')
ylabel('Voltage [V]')
