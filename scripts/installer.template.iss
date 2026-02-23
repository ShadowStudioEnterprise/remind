#define AppName "RE:mind"
#define AppExeName "remind.exe"
#define AppPublisher "Shadow Studio Enterprise"
#define AppURL "https://github.com/ShadowStudioEnterprise/remind"
#define AppVersion "{APP_VERSION}"

; IMPORTANTE:
; Usa un GUID REAL y FIJO para siempre (no lo cambies entre versiones)
; Puedes generar uno con PowerShell: [guid]::NewGuid()
#define AppId "{{8D6A2D8C-7B3A-4F1A-9C9D-REPLACE-ME}}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Per-user (sin admin). Instala en LocalAppData
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Carpeta por usuario (limpia para auto-update sin UAC)
DefaultDirName={localappdata}\REmind
UsePreviousAppDir=yes

; Accesos directos
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; Evita pantallas innecesarias y “cosas raras”
DisableDirPage=yes
DisableReadyMemo=yes
DisableReadyPage=yes

; 64-bit mode si el sistema es 64-bit (no obliga, pero evita rutas raras)
ArchitecturesAllowed=x64 arm64
ArchitecturesInstallIn64BitMode=x64 arm64

; Output: lo queremos en dist/ (como dijiste)
OutputDir=dist
OutputBaseFilename=REmind-Setup-v{#AppVersion}

Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; Icono del instalador + desinstalador “bonito”
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\{#AppExeName}

; Auto-update / reinstalación robusta
CloseApplications=yes
RestartApplications=yes

; Recomendado: evita ejecutar varias instancias durante instalación
AppMutex=REmind_Mutex

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
; Copia todo lo empaquetado por PyInstaller
Source: "dist\remind\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; En installs normales, lanzar. En modo silent (auto-update), NO lanzar.
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent