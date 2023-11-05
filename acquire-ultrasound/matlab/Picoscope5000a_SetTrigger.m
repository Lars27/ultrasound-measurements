function   TriggerStatus= Picoscope5000a_SetTrigger(Device,DSO)
%function   TriggerStatus= Picoscope5000a_SetTrigger(Device,DSO)
%
% Configure Picoscope 5000 trigger settings
% 
% Input
% ps5000aDeviceObj : Picoscope device object defined in Matlab's
%                    Instrument Control Toolbox
% DSO : Configuration of digital oscilloscope
%       Fields
%       horiz : Sampling (Horizontal scale)
%               Fields
%                  fs : Actual sample rate [S/s]
%                Npre : Number of pre-trigger samples
%               Npost : Number of post-trigger samples
%
%     trigger : Trigger configuration
%               Fields
%               delay : Trigger delay [s]
%               level : Trigger level [V]
%              enable : Trigger enabled (logical 0-1)
%                auto : Auto-trigger wait time [s]
%              source : Trigger source [Ch 0 ... 3, EXT:4]
%                mode : Trigger mode (Rising: 2, Falling: 3)
%       internaltimer : Internal trigger period [s].
%                       Overrides 'auto', normally used when enable=0

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

%%

% Scale input as defined in Picoscope documentation
delay    = round(DSO.trigger.delay*DSO.horiz.fs);
threshold= DSO.trigger.level*1e3;

% Send to instrument
set(Device, 'numPreTriggerSamples', DSO.horiz.Npre);
set(Device, 'numPostTriggerSamples', DSO.horiz.Npost);

triggerGroupObj = get(Device, 'Trigger');
triggerGroupObj = triggerGroupObj(1);
if DSO.trigger.enable    
    set(triggerGroupObj, 'autoTriggerMs', DSO.trigger.auto/milli);
    set(triggerGroupObj, 'delay', delay);    
    TriggerStatus = invoke(triggerGroupObj, 'setSimpleTrigger', DSO.trigger.source, threshold, DSO.trigger.mode);
else
    invoke(triggerGroupObj,'settriggeroff');
    TriggerStatus = invoke(triggerGroupObj, 'ps5000aSetAutoTriggerMicroSeconds', round(DSO.trigger.internaltimer/micro) );
end

end
