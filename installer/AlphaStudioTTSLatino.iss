#define AppName "Alpha Studio TTS Latino"
#define AppVersion "0.2.0"
#define AppPublisher "Alpha Ecuador"
#define AppExeName "AlphaStudioTTSLatino.exe"

[Setup]
AppId={{D28D0B82-3A3D-4F90-86D7-8A0E751DF2F8}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Alpha Studio TTS Latino
DefaultGroupName={#AppName}
OutputDir=..\dist\installer
OutputBaseFilename=AlphaStudioTTSLatino-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "..\dist\AlphaStudioTTSLatino\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; Flags: unchecked

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent
