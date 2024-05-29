function trace = read_e4990(src)
% function trace = read_e4990(src)
%
% Read csv-file from Keysight E4990A Impedance Analyser
%
%      src  Path of source file
%
%     trace struct containing measurement result and parameters
%       f     Frequency [Hz]
%       Zref  Reference (characteristic) impedance [Ohm]
%
% Assumes measurement was done as 1-port reflection, returning S-parameters, S11

% Lars Hoff, USN, 2024

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
nLines= k-1;  % Number of lines formatted, removing end-of-file character
fclose ( fileID );

%% Interpret csv-data 
kHeader = 0;        % Counter for header and ending lines
startData = inf;    % Line with irst data point



for k=1:nLines      % Run through all lines and interpret contents
    %--- Header and finishing lines start with '#' ---
    if contains( line(k), '!')   
        isHeader = 1;           % Flag indicating reading header 
        kHeader = kHeader+1;
        headerLine( kHeader ).text=line(k);     % Put header data into structure
        headerLine( kHeader ).no  =k;

    elseif contains( line(k), 'BEGIN')   
        description = line(k);
    
    elseif contains( line(k), 'Frequency')   
        contents = line(k);
        startData = k+1;    

    elseif contains( line(k), 'END')   
        endData = k-1;

    end
end

kData = 0;
for k=startData:endData      % Run through lines containing data points

    kData = kData+1;                        % Data line counter
    nCol= 3;                                % Measurement data are stored in three columns: Frequency, real and imaginary part
    lineData = ( split( line(k), ',' ) );   % Split columns in csv-file

    % Correct if comma are used as decimal separator, this will split each number into two columns
    if length( lineData ) == 2*nCol
        val= zeros( nCol, 1 );
        for col=1:nCol
            val(col) = double( join( lineData( 2*col+ [-1:0] ), '.' ) );  % Join two columns to create one decimal number
        end

    else % Comma not used as decimal separator, convert from strings to number
        val= double(lineData);
    end

    f( kData) = val(1);      % [Hz]  Frequency in 1st column, assuming data was stored in MHz
    Z( kData) = val(2)*1e3;      % [Ohm] Impedance magnitude

end

% Save in struct for export
trace.f   = f;
trace.Z   = Z;

end


%% Internal functions
% Convert string to numeric value
function val= interpretNumericValue( str )
    str = replace( str, ',' , '.' );   % Replace comma if used as decimal separator
    val = double( str );
end