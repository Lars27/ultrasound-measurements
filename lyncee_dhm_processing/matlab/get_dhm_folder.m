function dhmFolder = get_dhm_folder(dhmPath)

if dhmPath(end)==filesep
    dhmPath=dhmPath(1:end-1);
end
separatorPositions=find(dhmPath(1:end)==filesep); 

lastPosition= separatorPositions(end);
dhmFolder= dhmPath(lastPosition+1:end);

kReplace= strfind(dhmFolder , "."|" ");
dhmFolder(kReplace) = "-";
