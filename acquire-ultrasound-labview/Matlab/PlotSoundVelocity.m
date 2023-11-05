% Plot speed of sound

T=[0:0.1:100];
[cw S]=SoundVelocity(T);

subplot(2,1,1)
plot(T,cw)
grid on
ylabel('Speed of sound [m/s]')

subplot(2,1,2)
plot(T,S)
grid on
ylabel('Temperature Sensitivity [m/s/C]')