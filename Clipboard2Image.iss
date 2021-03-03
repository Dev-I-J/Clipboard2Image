#define AppName "Clipboard2Image"
#define AppVersion "0.0.1-alpha"
#define AppPublisher "Clipboard2Image"
#define AppURL "https://github.com/Dev-I-J/Clipboard2Image"
#define AppExeName "Clipboard2Image.exe"

[Setup]
AppId={{AB3708AA-053E-4EA6-99B6-534D87034472}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={commonpf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=dist\Setup
OutputBaseFilename={#AppName}_{#AppVersion}_Installer
SetupIconFile=src\icons\appicon.ico
Compression=lzma
SolidCompression=yes
DisableStartupPrompt=no
DisableWelcomePage=no
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=6.2.9200

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Clipboard2Image\Clipboard2Image.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Clipboard2Image\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
