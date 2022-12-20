function ExportSpeedofSound(fid,par)
% function ExportSpeedofSound(fid,par)
%
% Export speed of sound measurement results

% Lars Hoff, USN, Nov 2019


header=nargin<2;

if header % Write file header
    fprintf(fid,'Result of speed of sound measurement\n');
    fprintf(fid,'Processed %s\n', datestr(now(),0));
    fprintf(fid,'%s\t', ["Measurement","Reference","Sample ID"] );
    fprintf(fid,'%s\t', ["Thickness","Density","Temperature"] );
    fprintf(fid,'%s\t', ["Water sound speed","Transducer distance"]);
    fprintf(fid,'%s\t', ["Delay", "", ""] );
    fprintf(fid,'%s\t', ["Speed of sound", "", ""] );
    fprintf(fid,'%s\t', ["Acoustic impedance", "", "" ]);
    fprintf(fid,'\n');
    fprintf(fid,'%s\t', repmat("",1,8));
    fprintf(fid,'%s\t', repmat(["Ref water" "Reflections" "Transmissions"],1,3) );
    fprintf(fid,'\n');
    fprintf(fid,'%s\t', repmat("",1,3));
    fprintf(fid,'%s\t', ["[mm]","[kg/m3]","[C]"]);
    fprintf(fid,'%s\t', ["[m/s]","[m]"]);
    fprintf(fid,'%s\t', repmat("[s]",1,3));
    fprintf(fid,'%s\t', repmat("[m/s]",1,3));
    fprintf(fid,'%s\t', repmat("[MRayl]",1,3));
    fprintf(fid,'\n');
else    
    fprintf(fid,'%s\t', [par.Mfile, par.Rfile, par.ID]);
    fprintf(fid,'%f\t', [par.ds, par.rho, par.T ]);
    fprintf(fid,'%f\t', par.cw, par.dw );
    fprintf(fid,'%.8e\t', [par.dtp, par.dtr] );
    fprintf(fid,'%f\t', [par.csp, par.csr] );
    fprintf(fid,'%f\t', [par.Zsp, par.Zsr] );
    fprintf(fid,'\n');
end

