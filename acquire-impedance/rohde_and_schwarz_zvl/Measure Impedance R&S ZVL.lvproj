<?xml version='1.0' encoding='UTF-8'?>
<Project Type="Project" LVVersion="16008000">
	<Item Name="My Computer" Type="My Computer">
		<Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.tcp.enabled" Type="Bool">false</Property>
		<Property Name="server.tcp.port" Type="Int">0</Property>
		<Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
		<Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="Measure Impedance R&amp;S ZVL" Type="Folder" URL="..">
			<Property Name="NI.DISK" Type="Bool">true</Property>
		</Item>
		<Item Name="Dependencies" Type="Dependencies">
			<Item Name="instr.lib" Type="Folder">
				<Item Name="_rszvl Coercing Warning.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/_rszvl Coercing Warning.vi"/>
				<Item Name="_rszvl Default Instrument Setup.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/_rszvl Default Instrument Setup.vi"/>
				<Item Name="_rszvl Get Trace Data.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/_rszvl Get Trace Data.vi"/>
				<Item Name="_rszvl Initialize Clean Up.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/_rszvl Initialize Clean Up.vi"/>
				<Item Name="_rszvl Read Long Data.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/_rszvl Read Long Data.vi"/>
				<Item Name="_rszvl_core_repcap_channel.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/_rszvl_core_repcap_channel.vi"/>
				<Item Name="Agilent 87XX Series.lvlib" Type="Library" URL="/&lt;instrlib&gt;/Agilent 87XX Series/Agilent 87XX Series.lvlib"/>
				<Item Name="rszvl Channel Add.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Network Analyzer/Channels/Channel Select/rszvl Channel Add.vi"/>
				<Item Name="rszvl Close.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/rszvl Close.vi"/>
				<Item Name="rszvl Configure Acquisition.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Network Analyzer/Channels/rszvl Configure Acquisition.vi"/>
				<Item Name="rszvl Configure Display Update.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Network Analyzer/Display Control/rszvl Configure Display Update.vi"/>
				<Item Name="rszvl Configure Frequency Start Stop.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Network Analyzer/Channels/Stimulus/rszvl Configure Frequency Start Stop.vi"/>
				<Item Name="rszvl Configure S-Parameters.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Network Analyzer/Measurement/Measurement Parameter/rszvl Configure S-Parameters.vi"/>
				<Item Name="rszvl Configure Sweep Points.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Network Analyzer/Channels/rszvl Configure Sweep Points.vi"/>
				<Item Name="rszvl Error Query.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Utility/rszvl Error Query.vi"/>
				<Item Name="rszvl Get OPC Timeout.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Utility/rszvl Get OPC Timeout.vi"/>
				<Item Name="rszvl Get Trace Response Single Sweep Data.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Network Analyzer/Measurement/rszvl Get Trace Response Single Sweep Data.vi"/>
				<Item Name="rszvl Initialize.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/rszvl Initialize.vi"/>
				<Item Name="rszvl Instrument Options.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Utility/rszvl Instrument Options.vi"/>
				<Item Name="rszvl Reset.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Utility/rszvl Reset.vi"/>
				<Item Name="rszvl SAN Initiate.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Spectrum Analyzer/Measurement/Low-Level Measurement/rszvl SAN Initiate.vi"/>
				<Item Name="rszvl Set OPC Timeout.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Utility/rszvl Set OPC Timeout.vi"/>
				<Item Name="rszvl Trace List.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/Network Analyzer/Channels/Traces/rszvl Trace List.vi"/>
				<Item Name="rszvl_core_attribute_read_boolean.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_read_boolean.vi"/>
				<Item Name="rszvl_core_attribute_read_int.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_read_int.vi"/>
				<Item Name="rszvl_core_attribute_read_real.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_read_real.vi"/>
				<Item Name="rszvl_core_attribute_read_string.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_read_string.vi"/>
				<Item Name="rszvl_core_attribute_write_boolean.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_write_boolean.vi"/>
				<Item Name="rszvl_core_attribute_write_int.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_write_int.vi"/>
				<Item Name="rszvl_core_attribute_write_none.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_write_none.vi"/>
				<Item Name="rszvl_core_attribute_write_real.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_write_real.vi"/>
				<Item Name="rszvl_core_attribute_write_string.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_attribute_write_string.vi"/>
				<Item Name="rszvl_core_call_check_callback.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_call_check_callback.vi"/>
				<Item Name="rszvl_core_call_range_callback.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_call_range_callback.vi"/>
				<Item Name="rszvl_core_call_rngtable_callback.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_call_rngtable_callback.vi"/>
				<Item Name="rszvl_core_check_attribute.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_check_attribute.vi"/>
				<Item Name="rszvl_core_check_error.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_check_error.vi"/>
				<Item Name="rszvl_core_check_instr_version.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_check_instr_version.vi"/>
				<Item Name="rszvl_core_check_option.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_check_option.vi"/>
				<Item Name="rszvl_core_get_attribute_index.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_get_attribute_index.vi"/>
				<Item Name="rszvl_core_get_enum_value.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_get_enum_value.vi"/>
				<Item Name="rszvl_core_get_rng_table_index.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_get_rng_table_index.vi"/>
				<Item Name="rszvl_core_global.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_global.vi"/>
				<Item Name="rszvl_core_range.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_range.vi"/>
				<Item Name="rszvl_core_repcap.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_repcap.vi"/>
				<Item Name="rszvl_core_session_globals.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_session_globals.vi"/>
				<Item Name="rszvl_core_waitOPC.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_waitOPC.vi"/>
				<Item Name="rszvl_core_write.vi" Type="VI" URL="/&lt;instrlib&gt;/rszvl/_utility/rszvl_core/rszvl_core_write.vi"/>
			</Item>
			<Item Name="user.lib" Type="Folder">
				<Item Name="subrszvl_core_attribute_express.vi" Type="VI" URL="/&lt;userlib&gt;/_express/rszvl/rszvl_core_attribute_expressSource.llb/subrszvl_core_attribute_express.vi"/>
			</Item>
			<Item Name="vi.lib" Type="Folder">
				<Item Name="BuildHelpPath.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/BuildHelpPath.vi"/>
				<Item Name="Check if File or Folder Exists.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/libraryn.llb/Check if File or Folder Exists.vi"/>
				<Item Name="Check Special Tags.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Check Special Tags.vi"/>
				<Item Name="Clear Errors.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Clear Errors.vi"/>
				<Item Name="Close File+.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/file.llb/Close File+.vi"/>
				<Item Name="compatCalcOffset.vi" Type="VI" URL="/&lt;vilib&gt;/_oldvers/_oldvers.llb/compatCalcOffset.vi"/>
				<Item Name="compatFileDialog.vi" Type="VI" URL="/&lt;vilib&gt;/_oldvers/_oldvers.llb/compatFileDialog.vi"/>
				<Item Name="compatOpenFileOperation.vi" Type="VI" URL="/&lt;vilib&gt;/_oldvers/_oldvers.llb/compatOpenFileOperation.vi"/>
				<Item Name="compatReadText.vi" Type="VI" URL="/&lt;vilib&gt;/_oldvers/_oldvers.llb/compatReadText.vi"/>
				<Item Name="compatWriteText.vi" Type="VI" URL="/&lt;vilib&gt;/_oldvers/_oldvers.llb/compatWriteText.vi"/>
				<Item Name="Convert property node font to graphics font.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Convert property node font to graphics font.vi"/>
				<Item Name="Details Display Dialog.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Details Display Dialog.vi"/>
				<Item Name="DialogType.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/DialogType.ctl"/>
				<Item Name="DialogTypeEnum.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/DialogTypeEnum.ctl"/>
				<Item Name="Error Cluster From Error Code.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Error Cluster From Error Code.vi"/>
				<Item Name="Error Code Database.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Error Code Database.vi"/>
				<Item Name="ErrWarn.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/ErrWarn.ctl"/>
				<Item Name="eventvkey.ctl" Type="VI" URL="/&lt;vilib&gt;/event_ctls.llb/eventvkey.ctl"/>
				<Item Name="Find First Error.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Find First Error.vi"/>
				<Item Name="Find Tag.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Find Tag.vi"/>
				<Item Name="Format Message String.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Format Message String.vi"/>
				<Item Name="General Error Handler Core CORE.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/General Error Handler Core CORE.vi"/>
				<Item Name="General Error Handler.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/General Error Handler.vi"/>
				<Item Name="Get String Text Bounds.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Get String Text Bounds.vi"/>
				<Item Name="Get Text Rect.vi" Type="VI" URL="/&lt;vilib&gt;/picture/picture.llb/Get Text Rect.vi"/>
				<Item Name="GetHelpDir.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/GetHelpDir.vi"/>
				<Item Name="GetRTHostConnectedProp.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/GetRTHostConnectedProp.vi"/>
				<Item Name="Longest Line Length in Pixels.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Longest Line Length in Pixels.vi"/>
				<Item Name="LVBoundsTypeDef.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/miscctls.llb/LVBoundsTypeDef.ctl"/>
				<Item Name="LVRectTypeDef.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/miscctls.llb/LVRectTypeDef.ctl"/>
				<Item Name="NI_AALBase.lvlib" Type="Library" URL="/&lt;vilib&gt;/Analysis/NI_AALBase.lvlib"/>
				<Item Name="NI_FileType.lvlib" Type="Library" URL="/&lt;vilib&gt;/Utility/lvfile.llb/NI_FileType.lvlib"/>
				<Item Name="NI_PackedLibraryUtility.lvlib" Type="Library" URL="/&lt;vilib&gt;/Utility/LVLibp/NI_PackedLibraryUtility.lvlib"/>
				<Item Name="Not Found Dialog.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Not Found Dialog.vi"/>
				<Item Name="Open File+.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/file.llb/Open File+.vi"/>
				<Item Name="Open_Create_Replace File.vi" Type="VI" URL="/&lt;vilib&gt;/_oldvers/_oldvers.llb/Open_Create_Replace File.vi"/>
				<Item Name="Read Characters From File.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/file.llb/Read Characters From File.vi"/>
				<Item Name="Read File+ (string).vi" Type="VI" URL="/&lt;vilib&gt;/Utility/file.llb/Read File+ (string).vi"/>
				<Item Name="Search and Replace Pattern.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Search and Replace Pattern.vi"/>
				<Item Name="Set Bold Text.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Set Bold Text.vi"/>
				<Item Name="Set String Value.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Set String Value.vi"/>
				<Item Name="TagReturnType.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/TagReturnType.ctl"/>
				<Item Name="Three Button Dialog CORE.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Three Button Dialog CORE.vi"/>
				<Item Name="Three Button Dialog.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Three Button Dialog.vi"/>
				<Item Name="Trim Whitespace.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Trim Whitespace.vi"/>
				<Item Name="whitespace.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/whitespace.ctl"/>
				<Item Name="Write Characters To File.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/file.llb/Write Characters To File.vi"/>
				<Item Name="Write File+ (string).vi" Type="VI" URL="/&lt;vilib&gt;/Utility/file.llb/Write File+ (string).vi"/>
			</Item>
			<Item Name="Test stream wfm to file.vi" Type="VI" URL="../Save Trace/Test stream wfm to file.vi"/>
		</Item>
		<Item Name="Build Specifications" Type="Build"/>
	</Item>
</Project>
