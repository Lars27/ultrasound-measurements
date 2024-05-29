function [ M, hd ] = ReadOndaCalibration(src,N)
% function [ M, hd ] = ReadOndaCalibration(src)
%
% Read Onda calibration from text file  
N
fid=fopen(src)
n=0; stop=0;
while not(stop)
    n=n+1;
    hd{n}=fgetl(fid);
    stop = strncmp('HEADER_END',hd{n},10);
end
M = fscanf(fid,'%f',[N,inf])';
fclose(fid);
return
end

