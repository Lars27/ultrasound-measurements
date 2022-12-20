function Vrange = Picoscope5000a_GetVranges(RangeNames)
% function Vrange = Picoscope5000a_GetVranges(RangeNames)
%
% Generate table of allowed voltage ranges in Picoscope 5000 
%
%    RangeNames : Voltage ranges defined as by PicoScope.
%                 See Picoscope documentation for definition
% 
%        Vrange : Table of voltage ranges
%                 Fields
%                      v : Voltage
%                   name : Range name as defined as by PicoScope
%                  range : Range no.     

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

%%
% Scan through and parse range names 
s = fields(RangeNames);
N = length(s);
v = zeros(N,1);
Vrange = struct('v',0,'name','', 'range', 0);
Vrange = repmat(Vrange,N,1);

for k=1:N
    L = textscan(s{k},'%s %f%s','Delimiter','_');
    if not(isempty(L{2}))
        switch upper(L{3}{1})
            case 'MV', m=1e-3;
            case 'V',  m=1;
            otherwise, ('Error: Unknown voltage multiplier');
        end
        v(k)=L{2}*m;
    else
        v(k)=0;
    end 
    
    % Organise in struct
    Vrange(k).v   = v(k);
    Vrange(k).name= s{k};
    Vrange(k).range= k-1;
end

end

