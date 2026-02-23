#define AppName "RE:mind"
#define AppExeName "remind.exe"
#define AppPublisher "fLtS"
#define AppURL "https://example.com"
#define AppVersion "{APP_VERSION}"

[Setup]
AppId={{8D6A2D8C-7B3A-4F1A-9C9D-REPLACE-ME}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

OutputDir=dist_installer
OutputBaseFilename=REmind_Setup_{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; TU icono real
SetupIconFile=assets\app.ico

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
; MODO CARPETA
Source: "dist\remind\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent