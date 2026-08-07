#define MyAppName "Bragi"
#define MyAppPublisher "isyuricunha"
#define MyAppURL "https://github.com/isyuricunha/Quill"

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
; Keep the historical AppId so Bragi upgrades existing Quill installations
; instead of creating a second installed product.
AppId=isyuricunha.Quill
AppName={#MyAppName}
AppVersion={#AppVersion}
AppVerName={#MyAppName} {#AppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\Programs\Bragi
DefaultGroupName=Bragi
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=installer-output
OutputBaseFilename=Bragi-v{#AppVersion}-setup-windows-x64
; build.py materializes a classic DIB-backed ICO for Inno Setup. The app
; itself continues to use resources\icon.ico with the selected Bragi artwork.
SetupIconFile=build\setup_icon.ico
UninstallDisplayIcon={app}\Bragi.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Bragi AI Writing Assistant
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#AppVersion}

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Bragi\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
Type: files; Name: "{app}\Quill.exe"
Type: files; Name: "{autoprograms}\Quill.lnk"
Type: files; Name: "{autodesktop}\Quill.lnk"

[Icons]
Name: "{autoprograms}\Bragi"; Filename: "{app}\Bragi.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Bragi"; Filename: "{app}\Bragi.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\Bragi.exe"; Description: "{cm:LaunchProgram,Bragi}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent

[Code]
const
  RunKey = 'Software\Microsoft\Windows\CurrentVersion\Run';

procedure MigrateLegacyStartupEntry;
var
  LegacyValue: String;
  BragiCommand: String;
begin
  if RegQueryStringValue(HKCU, RunKey, 'Quill', LegacyValue) then
  begin
    BragiCommand := '"' + ExpandConstant('{app}\Bragi.exe') + '"';
    RegWriteStringValue(HKCU, RunKey, 'Bragi', BragiCommand);
    RegDeleteValue(HKCU, RunKey, 'Quill');
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    MigrateLegacyStartupEntry;
end;
