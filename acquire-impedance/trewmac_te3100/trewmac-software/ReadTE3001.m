function trace = ReadTE3001(src)
% function trace = ReadTE3001(src)
%
% Read csv-file from Trewmac Network Analyser
%
%      src  Path of source file
%
%     trace struct containing measurement result and parameters
%       f     Frequency [Hz]
%       S11   Reflection, complex 
%       Z     Impedance, complex valued [Ohm]
%       Zref  Reference (characteristic) impedance [Ohm]
%
% Assumes measurement was done as 1-port reflection, returning S-parameters, S11

% Lars Hoff, USN, 2022

fileID= fopen(src, 'r');

%% Read raw data csv-file into string lines
line     = string;   % Lines in CSV-file, as string array 
k        = 0;        % Line counter
finished = 0;        % Set to 1 when end of file detected
while not(finished)
    k = k+1;
    line(k)  = fgetl ( fileID );    % Read lines one by one
    finished = ( line(k)=="-1" );   % End-of-file identified fgetl returning string "-1"
end
N= k-1;  % Number of lines formatted, removing end-of-file character
fclose ( fileID );


%% Interpret csv-data 
kHeader = 0;   % Counter for header and ending lines
traceNo = 0;   % Counter for measurement traces

for k=1:N      % Run through all lines and interpret contents
    %--- Header and finishing lines start with '#' ---
    if contains( line(k), '#')   
        isHeader = 1;           % Flag indicating reading header 
        kHeader = kHeader+1;
        headerLine( kHeader ).text=line(k);     % Put header data into structure
        headerLine( kHeader ).no  =k;

        % Look for necessary information in header data. Identify contents by keywords in header
        hd = split( line(k) );  % Split header line into parts. (2) is the descriptive string, (4) is the data value   

        if contains( headerLine(kHeader).text, 'characteristic_impedance' )
            Zref = interpretNumericValue( hd(4) );

        elseif contains( headerLine(kHeader).text, 'velocity_factor' )
            velocityFactor = interpretNumericValue( hd(4) );

        elseif contains( headerLine(kHeader).text, 'data_type' )
            dataType= hd(4);
        
        elseif contains( headerLine(kHeader).text, 'new_trace' )
            traceName= hd(4);                        
        end
    
    %--- Other lines interpreted as measurement data
    else            
        if isHeader   % Reset data parameters if last line was header
            isHeader  = 0;                      % Reset heading flag
            traceNo = traceNo+1;                % Interpret following data as new trace, increase trace counter
            trace(traceNo).name = traceName;    % Put trace parameteres from header into struct
            trace(traceNo).Zref = Zref;         
            trace(traceNo).velocityFactor = velocityFactor;         
            trace(traceNo).dataType = dataType;         
            kData   = 0;                       
        end

        kData = kData+1;                        % Data line counter
        nCol= 3;                                % Measurement data are stored in three columns: Frequency, real and imaginary part
        lineData = ( split( line(k), ',' ) );   % Split columns in csv-file

        % Correct if comma are used as decimal separator, this will split each number into two columns
        if length( lineData ) == 2*nCol   
            val= zeros( nCol, 1 );  
            for col=1:nCol
                val(col) = double( join( lineData( 2*col+ [-1:0] ), '.' ) );  % Join two columns to create one decimal number
            end
        end

        f( kData,traceNo )   = val(1) * 1e6;         % [Hz]  Frequency in 1st column, assuming data was stored in MHz
        S11( kData,traceNo ) = val(2) + 1i*val(3);   %       S-parameters, real part in 2nd column, imaginary in 3rd
    end
end

% Convert from reflection to impedance
for k=1:length(trace) % Convert from reflection to impedance
    Z(:,k) = trace(k).Zref * ( 1+S11(:,k) )./( 1-S11(:,k) );   
end

% Save in struct for export
trace.f   = f;
trace.S11 = S11;
trace.Z   = Z;

end


%% Internal functions
% Convert string to numeric value
function val= interpretNumericValue( str )
    str = replace( str, ',' , '.' );   % Replace comma if used as decimal separator
    val = double( str );
end