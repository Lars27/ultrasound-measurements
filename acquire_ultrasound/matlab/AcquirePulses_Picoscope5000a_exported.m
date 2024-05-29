classdef AcquirePulses_Picoscope5000a_exported < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        AcuireUltrasoundGUI           matlab.ui.Figure
        StatusLabel                   matlab.ui.control.Label
        TransmitButton                matlab.ui.control.StateButton
        SavingPanel                   matlab.ui.container.Panel
        TabGroup                      matlab.ui.container.TabGroup
        FileTab                       matlab.ui.container.Tab
        ResultFileEditField           matlab.ui.control.EditField
        SaveButton                    matlab.ui.control.Button
        CounterEditField              matlab.ui.control.NumericEditField
        CounterEditFieldLabel         matlab.ui.control.Label
        PathTab                       matlab.ui.container.Tab
        ResultpathTextArea            matlab.ui.control.TextArea
        AcquisitionPanel              matlab.ui.container.Panel
        AcuisitionTabGroup            matlab.ui.container.TabGroup
        VerticalTab                   matlab.ui.container.Tab
        BWlimitbDropDown              matlab.ui.control.DropDown
        BWlimitADropDown              matlab.ui.control.DropDown
        BWlimitDropDownLabel          matlab.ui.control.Label
        RangeLabel                    matlab.ui.control.Label
        CouplingLabel                 matlab.ui.control.Label
        OffsetASpinner                matlab.ui.control.Spinner
        OffsetVSpinnerLabel           matlab.ui.control.Label
        OffsetBSpinner                matlab.ui.control.Spinner
        CouplingBDownDropDown         matlab.ui.control.DropDown
        EnableBButton                 matlab.ui.control.StateButton
        CouplingADownDropDown         matlab.ui.control.DropDown
        EnableAButton                 matlab.ui.control.StateButton
        ChBDropDown                   matlab.ui.control.DropDown
        ChADropDown                   matlab.ui.control.DropDown
        TriggerTab                    matlab.ui.container.Tab
        InternalTriggerSpinner        matlab.ui.control.Spinner
        InternalTriggermsLabel        matlab.ui.control.Label
        TriggerAutoDelaySpinner       matlab.ui.control.Spinner
        AutodelaymsLabel              matlab.ui.control.Label
        TriggerDelaySpinner           matlab.ui.control.Spinner
        DelaysSpinnerLabel            matlab.ui.control.Label
        TriggerPositionSpinner        matlab.ui.control.Spinner
        PositionSpinnerLabel          matlab.ui.control.Label
        TriggerLevelSpinner           matlab.ui.control.Spinner
        LevelVSpinnerLabel            matlab.ui.control.Label
        ModeLabel                     matlab.ui.control.Label
        SourceLabel                   matlab.ui.control.Label
        TriggerSourceDropDown         matlab.ui.control.DropDown
        TriggerModeDropDown           matlab.ui.control.DropDown
        SamplingTab                   matlab.ui.container.Tab
        NoofsampleskptsSpinner        matlab.ui.control.Spinner
        NoofsampleskptsSpinnerLabel   matlab.ui.control.Label
        SampleRateMSsEditField        matlab.ui.control.NumericEditField
        SampleRateMSsEditFieldLabel   matlab.ui.control.Label
        FilterTab                     matlab.ui.container.Tab
        FilterDropDown                matlab.ui.control.DropDown
        FilterOrderSpinner            matlab.ui.control.Spinner
        OrderLabel                    matlab.ui.control.Label
        FilterFHSpinner               matlab.ui.control.Spinner
        UpperlimitMHzLabel            matlab.ui.control.Label
        FilterFLSpinner               matlab.ui.control.Spinner
        LowerlimitMHzLabel            matlab.ui.control.Label
        SignalGeneratorPanel          matlab.ui.container.Panel
        AmplitudeVSpinner             matlab.ui.control.Spinner
        AmplitudeVSpinnerLabel        matlab.ui.control.Label
        PhaseDegSpinner               matlab.ui.control.Spinner
        PhaseDegSpinnerLabel          matlab.ui.control.Label
        DurationCylesSpinner          matlab.ui.control.Spinner
        DurationCylesLabel            matlab.ui.control.Label
        FrequencyMHzSpinner           matlab.ui.control.Spinner
        FrequencyMHzLabel             matlab.ui.control.Label
        ShapeDropDown                 matlab.ui.control.DropDown
        ShapeLabel                    matlab.ui.control.Label
        EnvelopeDropDown              matlab.ui.control.DropDown
        EnvelopeLabel                 matlab.ui.control.Label
        ZoomendSpinner                matlab.ui.control.Spinner
        ZoomstartSpinner              matlab.ui.control.Spinner
        dBlimSpinner                  matlab.ui.control.Spinner
        fhMHzSpinner                  matlab.ui.control.Spinner
        flMHzSpinner                  matlab.ui.control.Spinner
        FreezeButton                  matlab.ui.control.StateButton
        Image                         matlab.ui.control.Image
        StopButton                    matlab.ui.control.StateButton
        AcquireUltrasoundTracesLabel  matlab.ui.control.Label
        Picoscope5000seriesLabel      matlab.ui.control.Label
        TransmitPulsePlot             matlab.ui.control.UIAxes
        ZoomedVoltagePlot             matlab.ui.control.UIAxes
        SpectrumPlot                  matlab.ui.control.UIAxes
        VoltagePlot                   matlab.ui.control.UIAxes
    end

    
    properties (Access = private)
        Device % Description
        Enuminfo % Description
        File % Description
        wfm % Description
        GUI % Description
        AWG % Description
        DSO % Description
        status % Description
        filter % Description
    end
    
    methods (Access = private)
        
        %=== Acquire traces from DSO and plot result ====
        function  AcquireAndPlot(app)
            position= {'left', 'right'};
            blockGroupObj = get(app.Device, 'Block');
            blockGroupObj = blockGroupObj(1);
            
            app.status.stopped=0;
            while not(app.StopButton.Value)
                if app.FreezeButton.Value
                    app.StatusLabel.BackgroundColor=app.GUI.color.freeze;
                    app.StatusLabel.Text = 'Frozen';
                else
                    app.StatusLabel.BackgroundColor=app.GUI.color.running;
                    app.StatusLabel.Text = 'Running';
                    
                    % Acquire traces from oscilloscope
                    app.wfm= Picoscope5000a_GetBlock(blockGroupObj, app.DSO);
                    t = app.wfm.t0+(0:app.wfm.Np-1)'*app.wfm.dt;
                    
                    vf = app.wfm.v;
                    % Filter results
                    switch lower(app.filter.state)
                        case 'ac'
                            for k=1:app.wfm.N
                                vf(:,k)=app.wfm.v(:,k) - mean(app.wfm.v(:,k));
                            end
                        case 'bandpass'
                            for k=1:app.wfm.N
                                vf(:,k)=filtfilt(app.filter.b , app.filter.a, app.wfm.v(:,k) );
                            end
                    end
                    
                    % Zoom in on interval
                    tlim(1)=app.ZoomstartSpinner.Value*micro;
                    tlim(2)=app.ZoomendSpinner.Value*micro;
                    nin=find( t>min(tlim) & t<max(tlim));
                    tin= t(nin);
                    vin= vf(nin,:);
                    
                    % Calculate spectrum
                    Nfft= 2048;
                    F   = fft(vin, Nfft);
                    PdB = 20*log10(abs(F));
                    PdB = PdB-max(PdB);
                    f   = (0:Nfft-1)/Nfft*app.DSO.horiz.fs;
                    
                    % Plot graphs
                    r = 1; floor(app.wfm.Np/300);    % Decimate before plotting
                    tr= t(1:r:end);
                    vr= app.wfm.v(1:r:end,:);
                    for k=1:app.wfm.N
                        visible= app.DSO.visible(k);
                        color  = app.GUI.color.ch{k};
                        
                        yyaxis(app.VoltagePlot, position{k}),
                        plot(app.VoltagePlot, tr/micro, vr(:,k), 'Visible',visible, 'Color',color);
                        
                        yyaxis(app.ZoomedVoltagePlot,position{k}),
                        plot(app.ZoomedVoltagePlot, tin/micro, vin(:,k), 'Visible',visible, 'Color',color );
                        
                        plot(app.SpectrumPlot, f/Mega, PdB(:,k), 'Visible',visible, 'Color', color );
                        hold(app.SpectrumPlot, 'on')
                    end
                    if app.AWG.exist
                        plot(app.SpectrumPlot, app.AWG.f/Mega,  app.AWG.PdB, 'color', app.GUI.color.AWG );
                    end
                    hold(app.SpectrumPlot, 'off')
                    
                    % Plot markers for interval
                    hold(app.VoltagePlot, 'on')
                    yl=ylim(app.VoltagePlot);
                    for k=1:length(tlim)
                        plot(app.VoltagePlot, tlim(k)/micro*[1 1], yl, 'k-');
                    end
                    hold(app.VoltagePlot, 'off')
                end
                drawnow
            end
            Picoscope5000a_AWGOnOff(app.Device, 0)
            app.StatusLabel.BackgroundColor=app.GUI.color.stopped;
            app.StatusLabel.Text = 'Stopped';
            app.status.stopped=1;
            disconnect(app.Device);
            delete(app.Device);
            delete(app)
        end
        
        %==== Set trigger ====
        function SetTrigger(app)
            app.DSO.trigger.source =str2double(app.TriggerSourceDropDown.Value);
            if app.DSO.trigger.source <0
                app.DSO.trigger.enable = 0;
            else
                app.DSO.trigger.enable = 1;
            end
            app.DSO.trigger.level = app.TriggerLevelSpinner.Value;
            app.DSO.trigger.delay = app.TriggerDelaySpinner.Value*micro;
            app.DSO.trigger.mode  = str2double(app.TriggerModeDropDown.Value);
            app.DSO.trigger.auto  = app.TriggerAutoDelaySpinner.Value*milli;
            app.DSO.trigger.internaltimer=app.InternalTriggerSpinner.Value*milli;
            
            app.DSO.horiz.fs= app.SampleRateMSsEditField.Value*Mega;    % Read sample rate
            app.DSO.horiz= Picoscope5000a_SetTimebase(app.Device, app.DSO.horiz);   % Find and set timebase
            app.SampleRateMSsEditField.Value=app.DSO.horiz.fs/Mega;     % Update to actual sample rate
            
            app.DSO.trigger.reference = app.TriggerPositionSpinner.Value;
            app.DSO.horiz.Npts = 1000*app.NoofsampleskptsSpinner.Value;
            app.DSO.horiz.Npre = app.DSO.horiz.Npts*app.DSO.trigger.reference/100;
            app.DSO.horiz.Npost= app.DSO.horiz.Npts - app.DSO.horiz.Npre;
            app.DSO.horiz.t0=-app.DSO.horiz.dt*app.DSO.horiz.Npre;
            
            Picoscope5000a_SetTrigger(app.Device, app.DSO);
            UpdateTriggerGUI(app);
        end
        
        %==== Set Vertical scale: function SetVoltagescale(app) ====
        function SetVoltagescale(app)
            % Read configuration from GUI
            display = [ app.EnableAButton,         app.EnableBButton  ];
            coupling= [ app.CouplingADownDropDown, app.CouplingBDownDropDown  ];
            offset  = [ app.OffsetASpinner,        app.OffsetBSpinner  ];
            range   = [app.ChADropDown,            app.ChBDropDown ] ;
            
            % Organize in struct and send to instrument
            for k=1:length(display)
                if display(k).Value
                    app.DSO.visible(k)="on";
                    display(k).BackgroundColor=app.GUI.color.ch{k};
                else
                    app.DSO.visible(k)="off";
                    display(k).BackgroundColor=app.GUI.color.dimmed;
                end
                app.DSO.ch(k).coupling= str2double(coupling(k).Value);
                app.DSO.ch(k).offset  = offset(k).Value;
                
                Vrange= Picoscope5000a_FindVrange(str2double(range(k).Value), app.Enuminfo.enPS5000ARange);
                app.DSO.ch(k).range= Vrange.range;
                app.DSO.ch(k).V    = Vrange.v;
                
                Picoscope5000a_SetChannel(app.Device, app.DSO.ch(k))
            end
            
            % Plot result
            yyaxis(app.VoltagePlot,'left'),  app.VoltagePlot.YLim = app.DSO.ch(1).V*[-1 1];
            yyaxis(app.VoltagePlot,'right'), app.VoltagePlot.YLim = app.DSO.ch(2).V*[-1 1];
        end
        
        %==== Update trigger on GUI ====
        function UpdateTriggerGUI(app)
            if app.DSO.trigger.enable
                app.TriggerModeDropDown.Enable = 1;
                app.TriggerDelaySpinner.Enable = 1;
                app.TriggerLevelSpinner.Enable = 1;
                app.TriggerAutoDelaySpinner.Enable= 1;
                app.InternalTriggerSpinner.Enable = 0;
            else
                app.TriggerModeDropDown.Enable = 0;
                app.TriggerDelaySpinner.Enable = 0;
                app.TriggerLevelSpinner.Enable = 0;
                app.TriggerAutoDelaySpinner.Enable= 0;
                app.InternalTriggerSpinner.Enable = 1;
            end
        end
        
        %==== Configure signal generator output ====
        function results = ConfigureSignalgenerator(app)
            
            % Read configuration from GUI
            app.AWG.envelope= app.EnvelopeDropDown.Value;
            app.AWG.shape   = app.ShapeDropDown.Value;
            app.AWG.f0      = app.FrequencyMHzSpinner.Value*Mega;
            app.AWG.Nc      = app.DurationCylesSpinner.Value;
            app.AWG.Vpp     = app.AmplitudeVSpinner.Value;
            app.AWG.phase   = app.PhaseDegSpinner.Value;
            app.AWG.fs      = app.DSO.horiz.fs;       % Taken from oscilloscope, actual fs for AWG can differ
            app.AWG.T       = app.AWG.Nc /app.AWG.f0; % Duration of pulse
            app.AWG.Transmit= app.TransmitButton.Value;
            
            %--- Calculate and display pulse
            app.AWG= MakePulse(app.AWG,0);
            plot(app.TransmitPulsePlot, app.AWG.t/micro, app.AWG.v, 'color', app.GUI.color.AWG );
            
            if app.AWG.Transmit
                app.TransmitButton.BackgroundColor = app.GUI.color.AWG;
            else
                app.TransmitButton.BackgroundColor = app.GUI.color.dimmed;
                xm=mean(xlim(app.TransmitPulsePlot));
                ym=mean(ylim(app.TransmitPulsePlot));
                text(app.TransmitPulsePlot, xm, ym, ' Off ', ...
                    'Fontsize', 60, 'Color', 0.8*[1 1 1], 'Horizontalalignment', 'center');
            end
            
            % Send settings to Signal generator
            app.AWG.TriggerSource = app.Enuminfo.enPS5000ASigGenTrigSource.PS5000A_SIGGEN_SCOPE_TRIG;  % Oscilloscope controls trigger, always
            Picoscope5000a_ConfigureAWG(app.Device,app.AWG)
            results=0;
        end
        
        %==== Define default colors for GUI ====
        function results = DefineColors(app)
            color=colororder;
            app.GUI.color.dimmed= 0.5*[1 1 1];
            app.GUI.color.dimmedplot= 0.90*[1 1 1];
            app.GUI.color.freeze= 0.7*[0 1 1];
            app.GUI.color.ch{1}=color(1,:);
            app.GUI.color.ch{2}=color(2,:);
            app.GUI.color.AWG=color(5,:);
            app.GUI.color.running= 0.4*[0 1 0];
            app.GUI.color.stopped= 0.5*[1 0 0];
            results=0;
        end
        
        %==== Initialize signal generator ====
        function results = InitializeAWG(app)
            AWGObj= get(app.Device, 'Signalgenerator');
            AWGObj= AWGObj(1);
            app.AWG.exist = (AWGObj.sigGenType==2);
            if app.AWG.exist
                app.SignalGeneratorPanel.Enable='on';
                app.TransmitPulsePlot.Visible  ='on';
                ConfigureSignalgenerator(app);
            else
                app.SignalGeneratorPanel.Enable='off';
                app.TransmitPulsePlot.Visible = 'off';
                app.TransmitButton.Enable =     'off';
            end
            results=0;
        end
        
        %==== Define bandpass filter ====
        function results = DefineFilter(app)
            app.filter.fl   = app.FilterFLSpinner.Value*Mega;
            app.filter.fh   = app.FilterFHSpinner.Value*Mega;
            app.filter.N    = app.FilterOrderSpinner.Value;
            app.filter.state= app.FilterDropDown.Value;
            results=0;
            
            switch(app.filter.state)
                case 'none'
                    app.FilterFHSpinner.Enable   = 'off';
                    app.FilterFLSpinner.Enable   = 'off';
                    app.FilterOrderSpinner.Enable= 'off';
                otherwise
                    app.FilterFHSpinner.Enable   = 'on';
                    app.FilterFLSpinner.Enable   = 'on';
                    app.FilterOrderSpinner.Enable= 'on';
            end
            if not(isempty(app.wfm))
                [app.filter.b, app.filter.a] = butter(app.filter.N, [app.filter.fl app.filter.fh]*(app.wfm.dt*2)  );
            end
        end
    end

    % Callbacks that handle component events
    methods (Access = private)

        % Code that executes after component creation
        function startupFcn(app)
            
            %=== Initialisation ===
            % Paths to instrument driver
            addpath(genpath('..\picotech-picosdk-ps5000a-matlab-instrument-driver\'));
            addpath(genpath('..\picotech-picosdk-matlab-picoscope-support-toolbox\'));
            
            % File naming
            mpath = mfilename('fullpath');
            basedir= trimpath(mpath,2);  % Remove filename and current directory.
            app.File.resultdir=sprintf('%s%s%s', basedir, filesep,'results');
            app.File.prefix= 'US';
            
            % Constants
            DefineColors(app);
            app.DSO.ch(1).no=0;  app.DSO.ch(1).enabled=1;
            app.DSO.ch(2).no=1;  app.DSO.ch(2).enabled=1;
            
            % Force start values on GUI
            app.StopButton.Value  = 0;
            app.FreezeButton.Value= 0;
            
            %=== Connect and configure Device ===
            instrreset;                     % Disconnect all instrument. Safe and simple, modify if more instruments are used
            PS5000aConfig;                  % Load configuration information
            app.Enuminfo= ps5000aEnuminfo;  % Constants for Picoscope driver
            app.Device= icdevice('picotech_ps5000a_generic', '');  % Create a device object.
            connect(app.Device);
            
            app.DSO.ADCresolution= Picoscope5000a_ADCresolution(app.Device, 15);
            SetTrigger(app);
            SetVoltagescale(app);
            InitializeAWG(app);
            DefineFilter(app);
            
            %=== Start data acquisition ===
            app.status.stoprequest =0;
            AcquireAndPlot(app);
        end

        % Value changed function: ChADropDown, ChBDropDown, 
        % CouplingADownDropDown, CouplingBDownDropDown, 
        % EnableAButton, EnableBButton, OffsetASpinner, 
        % OffsetBSpinner
        function DSOValueChanged(app, event)
            SetVoltagescale(app);
        end

        % Value changed function: NoofsampleskptsSpinner, 
        % SampleRateMSsEditField, TriggerAutoDelaySpinner, 
        % TriggerDelaySpinner, TriggerLevelSpinner, 
        % TriggerModeDropDown, TriggerPositionSpinner, 
        % TriggerSourceDropDown
        function TriggerValueChanged(app, event)
            SetTrigger(app);
        end

        % Value changed function: dBlimSpinner
        function dBlimSpinnerValueChanged(app, event)
            dBlow = app.dBlimSpinner.Value;
            ylim(app.SpectrumPlot, [dBlow, 0])
        end

        % Value changed function: fhMHzSpinner, flMHzSpinner
        function flimSpinnerValueChanged(app, event)
            flim=[app.flMHzSpinner.Value, app.fhMHzSpinner.Value];
            xlim(app.SpectrumPlot,         flim)
        end

        % Button pushed function: SaveButton
        function SaveButtonPushed(app, event)
            [resultfile,filename,n] = FindFilename(app.File.prefix, 'mat', app.File.resultdir);
            app.File.name=filename;
            wfms=app.wfm;
            save(resultfile, '-struct', 'wfms', '-mat');
            
            app.ResultFileEditField.Value= filename;
            app.CounterEditField.Value   = n;
            app.ResultpathTextArea.Value = resultfile;
        end

        % Button down function: VoltagePlot
        function VoltagePlotButtonDown(app, event)
            x=event.IntersectionPoint(1:2);
            tk= round(x(1));
            if x(2)>0, app.ZoomendSpinner.Value=tk;    %  Click in upper part of graph
            else,      app.ZoomstartSpinner.Value=tk;  %  Click in lower part of graph
            end
        end

        % Value changed function: BWlimitADropDown, BWlimitbDropDown
        function BandwidthValueChanged(app, event)
            app.DSO.ch(1).BWL = str2double(app.BWlimitADropDown.Value);
            app.DSO.ch(2).BWL = str2double(app.BWlimitbDropDown.Value);
            for k=1:2
                invoke(app.Device, 'ps5000aSetBandwidthFilter',app.DSO.ch(k).no, app.DSO.ch(k).BWL )
            end
        end

        % Value changed function: FreezeButton
        function FreezeButtonValueChanged(app, event)
            if app.FreezeButton.Value
                app.FreezeButton.BackgroundColor = app.GUI.color.freeze;
            else
                app.FreezeButton.BackgroundColor = app.GUI.color.dimmed;
            end
        end

        % Value changed function: AmplitudeVSpinner, 
        % DurationCylesSpinner, EnvelopeDropDown, 
        % FrequencyMHzSpinner, PhaseDegSpinner, ShapeDropDown, 
        % TransmitButton
        function AWGValueChanged(app, event)
            ConfigureSignalgenerator(app);
        end

        % Close request function: AcuireUltrasoundGUI
        function AcuireUltrasoundGUICloseRequest(app, event)
            Picoscope5000a_AWGOnOff(app.Device, 0)  % Turn off signal generator
            delete(app)
        end

        % Value changed function: FilterFHSpinner, FilterFLSpinner, 
        % FilterOrderSpinner
        function FilterValueChanged(app, event)
            DefineFilter(app)
        end

        % Value changed function: FilterDropDown
        function FilterDropDownValueChanged(app, event)
            value = app.FilterDropDown.Value;
            DefineFilter(app);
        end
    end

    % Component initialization
    methods (Access = private)

        % Create UIFigure and components
        function createComponents(app)

            % Create AcuireUltrasoundGUI and hide until all components are created
            app.AcuireUltrasoundGUI = uifigure('Visible', 'off');
            app.AcuireUltrasoundGUI.Color = [0.9412 0.9412 0.9412];
            app.AcuireUltrasoundGUI.Position = [0 0 1105 707];
            app.AcuireUltrasoundGUI.Name = 'Acquire Ultrasound Pulses - Picoscope';
            app.AcuireUltrasoundGUI.CloseRequestFcn = createCallbackFcn(app, @AcuireUltrasoundGUICloseRequest, true);

            % Create VoltagePlot
            app.VoltagePlot = uiaxes(app.AcuireUltrasoundGUI);
            title(app.VoltagePlot, 'Raw Traces')
            xlabel(app.VoltagePlot, 'Time [\mus]')
            ylabel(app.VoltagePlot, 'Voltage [V]')
            app.VoltagePlot.PlotBoxAspectRatio = [4.66292134831461 1 1];
            app.VoltagePlot.XGrid = 'on';
            app.VoltagePlot.YGrid = 'on';
            app.VoltagePlot.Box = 'on';
            app.VoltagePlot.ButtonDownFcn = createCallbackFcn(app, @VoltagePlotButtonDown, true);
            app.VoltagePlot.Position = [271 474 820 230];

            % Create SpectrumPlot
            app.SpectrumPlot = uiaxes(app.AcuireUltrasoundGUI);
            title(app.SpectrumPlot, 'Power Spectra')
            xlabel(app.SpectrumPlot, 'Frequency [MHz]')
            ylabel(app.SpectrumPlot, 'Power [dB re. max]')
            app.SpectrumPlot.PlotBoxAspectRatio = [2.57386363636364 1 1];
            app.SpectrumPlot.XLim = [0 10];
            app.SpectrumPlot.YLim = [-30 0];
            app.SpectrumPlot.YTick = [-60 -54 -48 -42 -36 -30 -24 -18 -12 -6 0];
            app.SpectrumPlot.XGrid = 'on';
            app.SpectrumPlot.YGrid = 'on';
            app.SpectrumPlot.YMinorGrid = 'on';
            app.SpectrumPlot.Box = 'on';
            app.SpectrumPlot.Position = [591 8 500 230];

            % Create ZoomedVoltagePlot
            app.ZoomedVoltagePlot = uiaxes(app.AcuireUltrasoundGUI);
            title(app.ZoomedVoltagePlot, 'Zomed Interval')
            xlabel(app.ZoomedVoltagePlot, 'Time [\mus]')
            ylabel(app.ZoomedVoltagePlot, 'Voltage [V]')
            app.ZoomedVoltagePlot.PlotBoxAspectRatio = [2.58857142857143 1 1];
            app.ZoomedVoltagePlot.XMinorTick = 'on';
            app.ZoomedVoltagePlot.YMinorTick = 'on';
            app.ZoomedVoltagePlot.XGrid = 'on';
            app.ZoomedVoltagePlot.XMinorGrid = 'on';
            app.ZoomedVoltagePlot.YGrid = 'on';
            app.ZoomedVoltagePlot.Box = 'on';
            app.ZoomedVoltagePlot.Position = [591 237 500 230];

            % Create TransmitPulsePlot
            app.TransmitPulsePlot = uiaxes(app.AcuireUltrasoundGUI);
            title(app.TransmitPulsePlot, 'Transmit Off')
            xlabel(app.TransmitPulsePlot, 'Time [\mus]')
            ylabel(app.TransmitPulsePlot, 'Voltage [V]')
            app.TransmitPulsePlot.Toolbar.Visible = 'off';
            app.TransmitPulsePlot.PlotBoxAspectRatio = [1.44767436107924 1 1];
            app.TransmitPulsePlot.YLim = [-1.2 1.2];
            app.TransmitPulsePlot.XGrid = 'on';
            app.TransmitPulsePlot.YGrid = 'on';
            app.TransmitPulsePlot.Box = 'on';
            app.TransmitPulsePlot.Position = [271 240 300 227];

            % Create Picoscope5000seriesLabel
            app.Picoscope5000seriesLabel = uilabel(app.AcuireUltrasoundGUI);
            app.Picoscope5000seriesLabel.FontSize = 14;
            app.Picoscope5000seriesLabel.FontWeight = 'bold';
            app.Picoscope5000seriesLabel.FontAngle = 'italic';
            app.Picoscope5000seriesLabel.Position = [60 659 155 22];
            app.Picoscope5000seriesLabel.Text = 'Picoscope 5000 series';

            % Create AcquireUltrasoundTracesLabel
            app.AcquireUltrasoundTracesLabel = uilabel(app.AcuireUltrasoundGUI);
            app.AcquireUltrasoundTracesLabel.FontSize = 16;
            app.AcquireUltrasoundTracesLabel.FontWeight = 'bold';
            app.AcquireUltrasoundTracesLabel.Position = [41 680 210 22];
            app.AcquireUltrasoundTracesLabel.Text = 'Acquire Ultrasound Traces';

            % Create StopButton
            app.StopButton = uibutton(app.AcuireUltrasoundGUI, 'state');
            app.StopButton.Text = 'Stop';
            app.StopButton.BackgroundColor = [0.6353 0.0784 0.1843];
            app.StopButton.FontWeight = 'bold';
            app.StopButton.FontColor = [1 1 1];
            app.StopButton.Position = [97 573 60 28];

            % Create Image
            app.Image = uiimage(app.AcuireUltrasoundGUI);
            app.Image.Position = [42 600 191 60];
            app.Image.ImageSource = 'USN_logo_En_rgb.png';

            % Create FreezeButton
            app.FreezeButton = uibutton(app.AcuireUltrasoundGUI, 'state');
            app.FreezeButton.ValueChangedFcn = createCallbackFcn(app, @FreezeButtonValueChanged, true);
            app.FreezeButton.Text = 'Freeze';
            app.FreezeButton.BackgroundColor = [0.502 0.502 0.502];
            app.FreezeButton.FontWeight = 'bold';
            app.FreezeButton.FontColor = [1 1 1];
            app.FreezeButton.Position = [460 195 60 28];

            % Create flMHzSpinner
            app.flMHzSpinner = uispinner(app.AcuireUltrasoundGUI);
            app.flMHzSpinner.ValueChangedFcn = createCallbackFcn(app, @flimSpinnerValueChanged, true);
            app.flMHzSpinner.Position = [631 219 60 22];

            % Create fhMHzSpinner
            app.fhMHzSpinner = uispinner(app.AcuireUltrasoundGUI);
            app.fhMHzSpinner.Limits = [0.1 100];
            app.fhMHzSpinner.ValueChangedFcn = createCallbackFcn(app, @flimSpinnerValueChanged, true);
            app.fhMHzSpinner.Position = [1024 219 60 22];
            app.fhMHzSpinner.Value = 10;

            % Create dBlimSpinner
            app.dBlimSpinner = uispinner(app.AcuireUltrasoundGUI);
            app.dBlimSpinner.Step = 6;
            app.dBlimSpinner.Limits = [-120 0];
            app.dBlimSpinner.ValueChangedFcn = createCallbackFcn(app, @dBlimSpinnerValueChanged, true);
            app.dBlimSpinner.Position = [532 51 60 22];
            app.dBlimSpinner.Value = -30;

            % Create ZoomstartSpinner
            app.ZoomstartSpinner = uispinner(app.AcuireUltrasoundGUI);
            app.ZoomstartSpinner.Step = 0.1;
            app.ZoomstartSpinner.Limits = [-1000 1000];
            app.ZoomstartSpinner.Position = [631 448 60 22];

            % Create ZoomendSpinner
            app.ZoomendSpinner = uispinner(app.AcuireUltrasoundGUI);
            app.ZoomendSpinner.Step = 0.1;
            app.ZoomendSpinner.Position = [1024 447 60 22];
            app.ZoomendSpinner.Value = 10;

            % Create SignalGeneratorPanel
            app.SignalGeneratorPanel = uipanel(app.AcuireUltrasoundGUI);
            app.SignalGeneratorPanel.Title = 'Signal Generator';
            app.SignalGeneratorPanel.BackgroundColor = [0.902 0.902 0.902];
            app.SignalGeneratorPanel.FontWeight = 'bold';
            app.SignalGeneratorPanel.Position = [9 190 248 159];

            % Create EnvelopeLabel
            app.EnvelopeLabel = uilabel(app.SignalGeneratorPanel);
            app.EnvelopeLabel.HorizontalAlignment = 'right';
            app.EnvelopeLabel.Position = [29 111 66 22];
            app.EnvelopeLabel.Text = 'Envelope ';

            % Create EnvelopeDropDown
            app.EnvelopeDropDown = uidropdown(app.SignalGeneratorPanel);
            app.EnvelopeDropDown.Items = {'Rectangular', 'Hann', 'Hamming', 'Triangular', 'Tukey'};
            app.EnvelopeDropDown.ItemsData = {'rectwin', 'hann', 'hamming', 'triang', 'tukeywin'};
            app.EnvelopeDropDown.ValueChangedFcn = createCallbackFcn(app, @AWGValueChanged, true);
            app.EnvelopeDropDown.Position = [94 111 100 22];
            app.EnvelopeDropDown.Value = 'hann';

            % Create ShapeLabel
            app.ShapeLabel = uilabel(app.SignalGeneratorPanel);
            app.ShapeLabel.HorizontalAlignment = 'right';
            app.ShapeLabel.Position = [35 90 60 22];
            app.ShapeLabel.Text = 'Shape ';

            % Create ShapeDropDown
            app.ShapeDropDown = uidropdown(app.SignalGeneratorPanel);
            app.ShapeDropDown.Items = {'Sine', 'Square', 'Triangular', 'Sawtooth'};
            app.ShapeDropDown.ValueChangedFcn = createCallbackFcn(app, @AWGValueChanged, true);
            app.ShapeDropDown.Position = [94 90 100 22];
            app.ShapeDropDown.Value = 'Sine';

            % Create FrequencyMHzLabel
            app.FrequencyMHzLabel = uilabel(app.SignalGeneratorPanel);
            app.FrequencyMHzLabel.HorizontalAlignment = 'right';
            app.FrequencyMHzLabel.Position = [9 68 116 22];
            app.FrequencyMHzLabel.Text = 'Frequency [MHz] ';

            % Create FrequencyMHzSpinner
            app.FrequencyMHzSpinner = uispinner(app.SignalGeneratorPanel);
            app.FrequencyMHzSpinner.Step = 0.1;
            app.FrequencyMHzSpinner.Limits = [0.1 40];
            app.FrequencyMHzSpinner.ValueDisplayFormat = '%4.2f';
            app.FrequencyMHzSpinner.ValueChangedFcn = createCallbackFcn(app, @AWGValueChanged, true);
            app.FrequencyMHzSpinner.Position = [124 68 70 22];
            app.FrequencyMHzSpinner.Value = 2;

            % Create DurationCylesLabel
            app.DurationCylesLabel = uilabel(app.SignalGeneratorPanel);
            app.DurationCylesLabel.HorizontalAlignment = 'right';
            app.DurationCylesLabel.Position = [15 47 110 22];
            app.DurationCylesLabel.Text = 'Duration [Cyles] ';

            % Create DurationCylesSpinner
            app.DurationCylesSpinner = uispinner(app.SignalGeneratorPanel);
            app.DurationCylesSpinner.Step = 0.5;
            app.DurationCylesSpinner.Limits = [0.5 50];
            app.DurationCylesSpinner.ValueDisplayFormat = '%4.1f';
            app.DurationCylesSpinner.ValueChangedFcn = createCallbackFcn(app, @AWGValueChanged, true);
            app.DurationCylesSpinner.Position = [124 47 70 22];
            app.DurationCylesSpinner.Value = 2;

            % Create PhaseDegSpinnerLabel
            app.PhaseDegSpinnerLabel = uilabel(app.SignalGeneratorPanel);
            app.PhaseDegSpinnerLabel.HorizontalAlignment = 'right';
            app.PhaseDegSpinnerLabel.Position = [34 26 91 22];
            app.PhaseDegSpinnerLabel.Text = 'Phase [Deg] ';

            % Create PhaseDegSpinner
            app.PhaseDegSpinner = uispinner(app.SignalGeneratorPanel);
            app.PhaseDegSpinner.Limits = [-360 360];
            app.PhaseDegSpinner.ValueChangedFcn = createCallbackFcn(app, @AWGValueChanged, true);
            app.PhaseDegSpinner.Position = [124 26 70 22];

            % Create AmplitudeVSpinnerLabel
            app.AmplitudeVSpinnerLabel = uilabel(app.SignalGeneratorPanel);
            app.AmplitudeVSpinnerLabel.HorizontalAlignment = 'right';
            app.AmplitudeVSpinnerLabel.Position = [29 5 89 22];
            app.AmplitudeVSpinnerLabel.Text = 'Amplitude [V] ';

            % Create AmplitudeVSpinner
            app.AmplitudeVSpinner = uispinner(app.SignalGeneratorPanel);
            app.AmplitudeVSpinner.Step = 0.01;
            app.AmplitudeVSpinner.Limits = [0.01 4];
            app.AmplitudeVSpinner.ValueChangedFcn = createCallbackFcn(app, @AWGValueChanged, true);
            app.AmplitudeVSpinner.Position = [124 5 70 22];
            app.AmplitudeVSpinner.Value = 2;

            % Create AcquisitionPanel
            app.AcquisitionPanel = uipanel(app.AcuireUltrasoundGUI);
            app.AcquisitionPanel.Title = 'Acquisition';
            app.AcquisitionPanel.BackgroundColor = [0.902 0.902 0.902];
            app.AcquisitionPanel.FontWeight = 'bold';
            app.AcquisitionPanel.Position = [9 355 248 206];

            % Create AcuisitionTabGroup
            app.AcuisitionTabGroup = uitabgroup(app.AcquisitionPanel);
            app.AcuisitionTabGroup.Position = [4 2 236 184];

            % Create VerticalTab
            app.VerticalTab = uitab(app.AcuisitionTabGroup);
            app.VerticalTab.Title = 'Vertical';
            app.VerticalTab.BackgroundColor = [0.902 0.902 0.902];

            % Create ChADropDown
            app.ChADropDown = uidropdown(app.VerticalTab);
            app.ChADropDown.Items = {'10 mV', '20 mV', '50 mV', '100 mV', '200 mV', '500 mV', '1 V', '2 V', '5 V', '10 V'};
            app.ChADropDown.ItemsData = {'10e-3', '20e-3', '50e-3', '100e-3', '200e-3', '500e-3', '1', '2', '5', '10'};
            app.ChADropDown.ValueChangedFcn = createCallbackFcn(app, @DSOValueChanged, true);
            app.ChADropDown.BackgroundColor = [0.902 0.902 0.902];
            app.ChADropDown.Position = [71 102 74 22];
            app.ChADropDown.Value = '2';

            % Create ChBDropDown
            app.ChBDropDown = uidropdown(app.VerticalTab);
            app.ChBDropDown.Items = {'10 mV', '20 mV', '50 mV', '100 mV', '200 mV', '500 mV', '1 V', '2 V', '5 V', '10 V'};
            app.ChBDropDown.ItemsData = {'10e-3', '20e-3', '50e-3', '100e-3', '200e-3', '500e-3', '1', '2', '5', '10'};
            app.ChBDropDown.ValueChangedFcn = createCallbackFcn(app, @DSOValueChanged, true);
            app.ChBDropDown.BackgroundColor = [0.902 0.902 0.902];
            app.ChBDropDown.Position = [153 101 74 22];
            app.ChBDropDown.Value = '200e-3';

            % Create EnableAButton
            app.EnableAButton = uibutton(app.VerticalTab, 'state');
            app.EnableAButton.ValueChangedFcn = createCallbackFcn(app, @DSOValueChanged, true);
            app.EnableAButton.Text = 'Ch A';
            app.EnableAButton.BackgroundColor = [0 0.4471 0.7412];
            app.EnableAButton.FontColor = [1 1 1];
            app.EnableAButton.Position = [78 123 60 28];
            app.EnableAButton.Value = true;

            % Create CouplingADownDropDown
            app.CouplingADownDropDown = uidropdown(app.VerticalTab);
            app.CouplingADownDropDown.Items = {'AC', 'DC'};
            app.CouplingADownDropDown.ItemsData = {'0', '1'};
            app.CouplingADownDropDown.ValueChangedFcn = createCallbackFcn(app, @DSOValueChanged, true);
            app.CouplingADownDropDown.BackgroundColor = [0.902 0.902 0.902];
            app.CouplingADownDropDown.Position = [71 81 74 22];
            app.CouplingADownDropDown.Value = '1';

            % Create EnableBButton
            app.EnableBButton = uibutton(app.VerticalTab, 'state');
            app.EnableBButton.ValueChangedFcn = createCallbackFcn(app, @DSOValueChanged, true);
            app.EnableBButton.Text = 'Ch B';
            app.EnableBButton.BackgroundColor = [0.851 0.3255 0.098];
            app.EnableBButton.FontColor = [1 1 1];
            app.EnableBButton.Position = [160 122 60 28];
            app.EnableBButton.Value = true;

            % Create CouplingBDownDropDown
            app.CouplingBDownDropDown = uidropdown(app.VerticalTab);
            app.CouplingBDownDropDown.Items = {'AC', 'DC'};
            app.CouplingBDownDropDown.ItemsData = {'0', '1'};
            app.CouplingBDownDropDown.ValueChangedFcn = createCallbackFcn(app, @DSOValueChanged, true);
            app.CouplingBDownDropDown.BackgroundColor = [0.902 0.902 0.902];
            app.CouplingBDownDropDown.Position = [153 81 74 22];
            app.CouplingBDownDropDown.Value = '1';

            % Create OffsetBSpinner
            app.OffsetBSpinner = uispinner(app.VerticalTab);
            app.OffsetBSpinner.Step = 0.1;
            app.OffsetBSpinner.Limits = [-1 1];
            app.OffsetBSpinner.ValueChangedFcn = createCallbackFcn(app, @DSOValueChanged, true);
            app.OffsetBSpinner.Position = [153 60 74 22];

            % Create OffsetVSpinnerLabel
            app.OffsetVSpinnerLabel = uilabel(app.VerticalTab);
            app.OffsetVSpinnerLabel.HorizontalAlignment = 'right';
            app.OffsetVSpinnerLabel.Position = [9 60 63 22];
            app.OffsetVSpinnerLabel.Text = 'Offset [V] ';

            % Create OffsetASpinner
            app.OffsetASpinner = uispinner(app.VerticalTab);
            app.OffsetASpinner.Step = 0.1;
            app.OffsetASpinner.Limits = [-10 10];
            app.OffsetASpinner.ValueChangedFcn = createCallbackFcn(app, @DSOValueChanged, true);
            app.OffsetASpinner.Position = [71 60 74 22];

            % Create CouplingLabel
            app.CouplingLabel = uilabel(app.VerticalTab);
            app.CouplingLabel.HorizontalAlignment = 'right';
            app.CouplingLabel.Position = [1 81 71 22];
            app.CouplingLabel.Text = 'Coupling [V] ';

            % Create RangeLabel
            app.RangeLabel = uilabel(app.VerticalTab);
            app.RangeLabel.HorizontalAlignment = 'right';
            app.RangeLabel.Position = [9 102 63 22];
            app.RangeLabel.Text = 'Range [V] ';

            % Create BWlimitDropDownLabel
            app.BWlimitDropDownLabel = uilabel(app.VerticalTab);
            app.BWlimitDropDownLabel.HorizontalAlignment = 'right';
            app.BWlimitDropDownLabel.Position = [14 38 56 22];
            app.BWlimitDropDownLabel.Text = 'BW limit ';

            % Create BWlimitADropDown
            app.BWlimitADropDown = uidropdown(app.VerticalTab);
            app.BWlimitADropDown.Items = {'None', '20 MHz'};
            app.BWlimitADropDown.ItemsData = {'0', '1'};
            app.BWlimitADropDown.ValueChangedFcn = createCallbackFcn(app, @BandwidthValueChanged, true);
            app.BWlimitADropDown.Position = [71 38 74 22];
            app.BWlimitADropDown.Value = '1';

            % Create BWlimitbDropDown
            app.BWlimitbDropDown = uidropdown(app.VerticalTab);
            app.BWlimitbDropDown.Items = {'None', '20 MHz'};
            app.BWlimitbDropDown.ItemsData = {'0', '1'};
            app.BWlimitbDropDown.ValueChangedFcn = createCallbackFcn(app, @BandwidthValueChanged, true);
            app.BWlimitbDropDown.Position = [153 38 74 22];
            app.BWlimitbDropDown.Value = '1';

            % Create TriggerTab
            app.TriggerTab = uitab(app.AcuisitionTabGroup);
            app.TriggerTab.Title = 'Trigger';
            app.TriggerTab.BackgroundColor = [0.902 0.902 0.902];

            % Create TriggerModeDropDown
            app.TriggerModeDropDown = uidropdown(app.TriggerTab);
            app.TriggerModeDropDown.Items = {'Rising', 'Falling'};
            app.TriggerModeDropDown.ItemsData = {'2', '3'};
            app.TriggerModeDropDown.ValueChangedFcn = createCallbackFcn(app, @TriggerValueChanged, true);
            app.TriggerModeDropDown.BackgroundColor = [0.902 0.902 0.902];
            app.TriggerModeDropDown.Position = [130 88 74 22];
            app.TriggerModeDropDown.Value = '2';

            % Create TriggerSourceDropDown
            app.TriggerSourceDropDown = uidropdown(app.TriggerTab);
            app.TriggerSourceDropDown.Items = {'Ch A', 'Ch B', 'EXT', 'Internal'};
            app.TriggerSourceDropDown.ItemsData = {'0', '1', '4', '-1'};
            app.TriggerSourceDropDown.ValueChangedFcn = createCallbackFcn(app, @TriggerValueChanged, true);
            app.TriggerSourceDropDown.BackgroundColor = [0.902 0.902 0.902];
            app.TriggerSourceDropDown.Position = [130 131 74 22];
            app.TriggerSourceDropDown.Value = '-1';

            % Create SourceLabel
            app.SourceLabel = uilabel(app.TriggerTab);
            app.SourceLabel.HorizontalAlignment = 'right';
            app.SourceLabel.Position = [84 131 47 22];
            app.SourceLabel.Text = 'Source ';

            % Create ModeLabel
            app.ModeLabel = uilabel(app.TriggerTab);
            app.ModeLabel.HorizontalAlignment = 'right';
            app.ModeLabel.Position = [92 88 39 22];
            app.ModeLabel.Text = 'Mode ';

            % Create LevelVSpinnerLabel
            app.LevelVSpinnerLabel = uilabel(app.TriggerTab);
            app.LevelVSpinnerLabel.HorizontalAlignment = 'right';
            app.LevelVSpinnerLabel.Position = [67 45 62 22];
            app.LevelVSpinnerLabel.Text = 'Level [V] ';

            % Create TriggerLevelSpinner
            app.TriggerLevelSpinner = uispinner(app.TriggerTab);
            app.TriggerLevelSpinner.Step = 0.1;
            app.TriggerLevelSpinner.ValueDisplayFormat = '%4.2f';
            app.TriggerLevelSpinner.ValueChangedFcn = createCallbackFcn(app, @TriggerValueChanged, true);
            app.TriggerLevelSpinner.Position = [130 45 74 22];
            app.TriggerLevelSpinner.Value = 1;

            % Create PositionSpinnerLabel
            app.PositionSpinnerLabel = uilabel(app.TriggerTab);
            app.PositionSpinnerLabel.HorizontalAlignment = 'right';
            app.PositionSpinnerLabel.Position = [55 109 76 22];
            app.PositionSpinnerLabel.Text = 'Position [%] ';

            % Create TriggerPositionSpinner
            app.TriggerPositionSpinner = uispinner(app.TriggerTab);
            app.TriggerPositionSpinner.Limits = [-50 50];
            app.TriggerPositionSpinner.ValueChangedFcn = createCallbackFcn(app, @TriggerValueChanged, true);
            app.TriggerPositionSpinner.Position = [130 109 75 22];
            app.TriggerPositionSpinner.Value = 10;

            % Create DelaysSpinnerLabel
            app.DelaysSpinnerLabel = uilabel(app.TriggerTab);
            app.DelaysSpinnerLabel.HorizontalAlignment = 'right';
            app.DelaysSpinnerLabel.Position = [69 67 62 22];
            app.DelaysSpinnerLabel.Text = 'Delay [µs] ';

            % Create TriggerDelaySpinner
            app.TriggerDelaySpinner = uispinner(app.TriggerTab);
            app.TriggerDelaySpinner.Limits = [0 200];
            app.TriggerDelaySpinner.ValueChangedFcn = createCallbackFcn(app, @TriggerValueChanged, true);
            app.TriggerDelaySpinner.Position = [130 67 74 22];

            % Create AutodelaymsLabel
            app.AutodelaymsLabel = uilabel(app.TriggerTab);
            app.AutodelaymsLabel.HorizontalAlignment = 'right';
            app.AutodelaymsLabel.Position = [39 24 92 22];
            app.AutodelaymsLabel.Text = 'Auto delay [ms] ';

            % Create TriggerAutoDelaySpinner
            app.TriggerAutoDelaySpinner = uispinner(app.TriggerTab);
            app.TriggerAutoDelaySpinner.Step = 100;
            app.TriggerAutoDelaySpinner.Limits = [0 10000];
            app.TriggerAutoDelaySpinner.ValueChangedFcn = createCallbackFcn(app, @TriggerValueChanged, true);
            app.TriggerAutoDelaySpinner.Position = [130 24 74 22];
            app.TriggerAutoDelaySpinner.Value = 1000;

            % Create InternalTriggermsLabel
            app.InternalTriggermsLabel = uilabel(app.TriggerTab);
            app.InternalTriggermsLabel.HorizontalAlignment = 'right';
            app.InternalTriggermsLabel.Position = [15 3 116 22];
            app.InternalTriggermsLabel.Text = 'Internal Trigger [ms] ';

            % Create InternalTriggerSpinner
            app.InternalTriggerSpinner = uispinner(app.TriggerTab);
            app.InternalTriggerSpinner.Step = 100;
            app.InternalTriggerSpinner.Limits = [0 10000];
            app.InternalTriggerSpinner.Position = [130 3 74 22];
            app.InternalTriggerSpinner.Value = 100;

            % Create SamplingTab
            app.SamplingTab = uitab(app.AcuisitionTabGroup);
            app.SamplingTab.Title = 'Sampling';
            app.SamplingTab.BackgroundColor = [0.902 0.902 0.902];

            % Create SampleRateMSsEditFieldLabel
            app.SampleRateMSsEditFieldLabel = uilabel(app.SamplingTab);
            app.SampleRateMSsEditFieldLabel.HorizontalAlignment = 'right';
            app.SampleRateMSsEditFieldLabel.Position = [23 123 115 22];
            app.SampleRateMSsEditFieldLabel.Text = 'Sample Rate [MS/s] ';

            % Create SampleRateMSsEditField
            app.SampleRateMSsEditField = uieditfield(app.SamplingTab, 'numeric');
            app.SampleRateMSsEditField.Limits = [0.1 250];
            app.SampleRateMSsEditField.ValueChangedFcn = createCallbackFcn(app, @TriggerValueChanged, true);
            app.SampleRateMSsEditField.Position = [137 123 45 22];
            app.SampleRateMSsEditField.Value = 100;

            % Create NoofsampleskptsSpinnerLabel
            app.NoofsampleskptsSpinnerLabel = uilabel(app.SamplingTab);
            app.NoofsampleskptsSpinnerLabel.HorizontalAlignment = 'right';
            app.NoofsampleskptsSpinnerLabel.Position = [0 101 135 22];
            app.NoofsampleskptsSpinnerLabel.Text = 'No. of samples [kpts] ';

            % Create NoofsampleskptsSpinner
            app.NoofsampleskptsSpinner = uispinner(app.SamplingTab);
            app.NoofsampleskptsSpinner.Limits = [1 100];
            app.NoofsampleskptsSpinner.ValueChangedFcn = createCallbackFcn(app, @TriggerValueChanged, true);
            app.NoofsampleskptsSpinner.Position = [137 101 60 22];
            app.NoofsampleskptsSpinner.Value = 20;

            % Create FilterTab
            app.FilterTab = uitab(app.AcuisitionTabGroup);
            app.FilterTab.Title = 'Filter';

            % Create LowerlimitMHzLabel
            app.LowerlimitMHzLabel = uilabel(app.FilterTab);
            app.LowerlimitMHzLabel.HorizontalAlignment = 'right';
            app.LowerlimitMHzLabel.Position = [37 72 101 22];
            app.LowerlimitMHzLabel.Text = 'Lower limit [MHz] ';

            % Create FilterFLSpinner
            app.FilterFLSpinner = uispinner(app.FilterTab);
            app.FilterFLSpinner.Limits = [0 50];
            app.FilterFLSpinner.ValueDisplayFormat = '%11.1f';
            app.FilterFLSpinner.ValueChangedFcn = createCallbackFcn(app, @FilterValueChanged, true);
            app.FilterFLSpinner.Position = [137 72 60 22];
            app.FilterFLSpinner.Value = 0.5;

            % Create UpperlimitMHzLabel
            app.UpperlimitMHzLabel = uilabel(app.FilterTab);
            app.UpperlimitMHzLabel.HorizontalAlignment = 'right';
            app.UpperlimitMHzLabel.Position = [37 51 101 22];
            app.UpperlimitMHzLabel.Text = 'Upper limit [MHz] ';

            % Create FilterFHSpinner
            app.FilterFHSpinner = uispinner(app.FilterTab);
            app.FilterFHSpinner.Limits = [0 50];
            app.FilterFHSpinner.ValueDisplayFormat = '%11.1f';
            app.FilterFHSpinner.ValueChangedFcn = createCallbackFcn(app, @FilterValueChanged, true);
            app.FilterFHSpinner.Position = [137 51 60 22];
            app.FilterFHSpinner.Value = 10;

            % Create OrderLabel
            app.OrderLabel = uilabel(app.FilterTab);
            app.OrderLabel.HorizontalAlignment = 'right';
            app.OrderLabel.Position = [92 30 43 22];
            app.OrderLabel.Text = 'Order ';

            % Create FilterOrderSpinner
            app.FilterOrderSpinner = uispinner(app.FilterTab);
            app.FilterOrderSpinner.Limits = [-50 50];
            app.FilterOrderSpinner.ValueDisplayFormat = '%3d';
            app.FilterOrderSpinner.ValueChangedFcn = createCallbackFcn(app, @FilterValueChanged, true);
            app.FilterOrderSpinner.Position = [137 30 60 22];
            app.FilterOrderSpinner.Value = 2;

            % Create FilterDropDown
            app.FilterDropDown = uidropdown(app.FilterTab);
            app.FilterDropDown.Items = {'No Filter', 'AC', 'Bandpass'};
            app.FilterDropDown.ItemsData = {'none', 'ac', 'bandpass'};
            app.FilterDropDown.ValueChangedFcn = createCallbackFcn(app, @FilterDropDownValueChanged, true);
            app.FilterDropDown.Position = [92 101 101 22];
            app.FilterDropDown.Value = 'none';

            % Create SavingPanel
            app.SavingPanel = uipanel(app.AcuireUltrasoundGUI);
            app.SavingPanel.Title = 'Saving';
            app.SavingPanel.BackgroundColor = [0.902 0.902 0.902];
            app.SavingPanel.FontWeight = 'bold';
            app.SavingPanel.Position = [9 29 248 150];

            % Create TabGroup
            app.TabGroup = uitabgroup(app.SavingPanel);
            app.TabGroup.Position = [5 9 235 116];

            % Create FileTab
            app.FileTab = uitab(app.TabGroup);
            app.FileTab.Title = 'File';
            app.FileTab.BackgroundColor = [0.902 0.902 0.902];

            % Create CounterEditFieldLabel
            app.CounterEditFieldLabel = uilabel(app.FileTab);
            app.CounterEditFieldLabel.HorizontalAlignment = 'right';
            app.CounterEditFieldLabel.Position = [8 57 56 22];
            app.CounterEditFieldLabel.Text = 'Counter ';

            % Create CounterEditField
            app.CounterEditField = uieditfield(app.FileTab, 'numeric');
            app.CounterEditField.BackgroundColor = [0.9412 0.9412 0.9412];
            app.CounterEditField.Position = [65 57 43 22];

            % Create SaveButton
            app.SaveButton = uibutton(app.FileTab, 'push');
            app.SaveButton.ButtonPushedFcn = createCallbackFcn(app, @SaveButtonPushed, true);
            app.SaveButton.BackgroundColor = [0.302 0.4392 0.1176];
            app.SaveButton.FontWeight = 'bold';
            app.SaveButton.FontColor = [1 1 1];
            app.SaveButton.Position = [110 54 60 28];
            app.SaveButton.Text = 'Save';

            % Create ResultFileEditField
            app.ResultFileEditField = uieditfield(app.FileTab, 'text');
            app.ResultFileEditField.BackgroundColor = [0.9412 0.9412 0.9412];
            app.ResultFileEditField.Position = [4 24 224 23];

            % Create PathTab
            app.PathTab = uitab(app.TabGroup);
            app.PathTab.Title = 'Path';
            app.PathTab.BackgroundColor = [0.902 0.902 0.902];

            % Create ResultpathTextArea
            app.ResultpathTextArea = uitextarea(app.PathTab);
            app.ResultpathTextArea.BackgroundColor = [0.9412 0.9412 0.9412];
            app.ResultpathTextArea.Position = [2 13 226 73];

            % Create TransmitButton
            app.TransmitButton = uibutton(app.AcuireUltrasoundGUI, 'state');
            app.TransmitButton.ValueChangedFcn = createCallbackFcn(app, @AWGValueChanged, true);
            app.TransmitButton.Text = 'Transmit';
            app.TransmitButton.BackgroundColor = [0.502 0.502 0.502];
            app.TransmitButton.FontWeight = 'bold';
            app.TransmitButton.FontColor = [1 1 1];
            app.TransmitButton.Position = [353 195 60 28];

            % Create StatusLabel
            app.StatusLabel = uilabel(app.AcuireUltrasoundGUI);
            app.StatusLabel.BackgroundColor = [0.902 0.902 0.902];
            app.StatusLabel.HorizontalAlignment = 'center';
            app.StatusLabel.FontWeight = 'bold';
            app.StatusLabel.FontColor = [1 1 1];
            app.StatusLabel.Position = [395 111 92 43];
            app.StatusLabel.Text = 'Status';

            % Show the figure after all components are created
            app.AcuireUltrasoundGUI.Visible = 'on';
        end
    end

    % App creation and deletion
    methods (Access = public)

        % Construct app
        function app = AcquirePulses_Picoscope5000a_exported

            % Create UIFigure and components
            createComponents(app)

            % Register the app with App Designer
            registerApp(app, app.AcuireUltrasoundGUI)

            % Execute the startup function
            runStartupFcn(app, @startupFcn)

            if nargout == 0
                clear app
            end
        end

        % Code that executes before app deletion
        function delete(app)

            % Delete UIFigure when app is deleted
            delete(app.AcuireUltrasoundGUI)
        end
    end
end