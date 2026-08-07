#define MyAppName "Quill"
#define MyAppPublisher "isyuricunha"
#define MyAppURL "https://github.com/isyuricunha/Quill"

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId=isyuricunha.Quill
AppName={#MyAppName}
AppVersion={#AppVersion}
AppVerName={#MyAppName} {#AppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\Programs\Quill
DefaultGroupName=Quill
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=installer-output
OutputBaseFilename=Quill-v{#AppVersion}-setup-windows-x64
SetupIconFile=resources\icon.ico
UninstallDisplayIcon={app}\Quill.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Quill AI Writing Assistant
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#AppVersion}

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Quill\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Quill"; Filename: "{app}\Quill.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Quill"; Filename: "{app}\Quill.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\Quill.exe"; Description: "{cm:LaunchProgram,Quill}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent
