function Configuration = read_dhm_configuration(Configuration)
% function Configuration = read_dhm_configuration(Configuration)
%
% Read configuration of DHM stroboscope
%

% Lars Hoff, USN, July 2024

Strobosetup = readstruct(Configuration.filename);

Configuration.name= Strobosetup.KoalaSetup.ConfigName;

Configuration.samplesPeriod=  Strobosetup.Setup.GeneralSettings.SamplesNbPerPeriod;
Configuration.frequency= Strobosetup.Setup.GeneralSettings.FrequencyHz;
Configuration.dutycycle= Strobosetup.Setup.GeneralSettings.DutyCyclePerCent;
Configuration.waveform = Strobosetup.Setup.GeneralSettings.Channels.WaveFormName;

return