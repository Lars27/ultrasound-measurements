function [f, Z]= read_TE3001(src)
% ffunction [f, Z]= read_TE3001(src)
%
% Read csv-file from Trewmac Network Analyser
%
%  src  Path of source file
%
%    f  Frequency [Hz]
%    Z  Impedance, complex valued

% Lars Hoff, USN, 2022

file_id= fopen(src, 'r');

%% Read raw data csv-file into string lines
line     = string;
k        = 0;
finished = 0;
while not(finished)
    k = k+1;
    line(k)  = fgetl(file_id);      % Each line stored as string array in
    finished = ( line(k)=="-1" );   % End-of-file identified by string "-1"
end
N= k-1;  % Number of lines formatted, excluding end-of-file character
fclose(file_id);


%% Interpret csv-data 
khead = 0;    
kdata = 0;    
for k=1:N
    % Header and finishing lines start with '#'
    if contains( line(k), '#')   
        khead = khead+1;
        headerline(khead).text=line(k);
        headerline(khead).no  =k;

        % Interpret header data
        hd=split(headerline(khead).text);                 % Read reference impedance 
        if contains( hd(2), 'characteristic_impedance' )
            hd(4) = replace(hd(4), ',' , '.');            % Replace comma if used as decimal separator
            Zref= double(hd(4));
        end
    
    % Other lines interpreted as measurement data
    else                        
        kdata = kdata+1;
        linedata = ( split( line(k), ',' ) ); % csv-file, columns separated by comma
        n_data= 3;
        n_col = length(linedata);   % Data are stored in three columns.      
        if n_col==2*n_data          % Join data split if using comma as decimal separator
            val= zeros( n_data, 1 );  
            for col=1:n_data
                val(col) = double( join( linedata( 2*col+[-1:0] ), '.' ) );
            end
        end
        f(kdata)  = val(1)*1e6;           % [Hz]  Frequency values, assuming data was stored in MHz
        S11(kdata)= val(2) + 1i*val(3);   %       S-parameters
    end
end
Z = Zref* (1+S11)./(1-S11);   % Convert from reflection to impedance 

end
