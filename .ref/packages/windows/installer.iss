; Inno Setup script for the Vidsaver Windows installer.
; Compiled in CI with:
;   ISCC.exe /DAppExe=<exe name> /DAppVersion=<x.y.z> /DAppArch=<x64|arm64> installer.iss
; AppExe is detected dynamically because flet names the executable
; after the project slug. AppArch matches the architecture the app was
; built for (the runner's CPU) and drives the installer's arch gating.

#ifndef AppExe
  #define AppExe "vidsaver.exe"
#endif
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef AppArch
  #define AppArch "x64"
#endif

#define AppName "Vidsaver"
#define AppPublisher "NextInPK"
#define AppURL "https://github.com/fazi-gondal/vidsaver"

[Setup]
AppId=com.nextinpk.vidsaver
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf64}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
; Output goes into build/ so CI can pick it up with a single path
OutputDir=..\..\build
OutputBaseFilename=Vidsaver-windows-{#AppArch}-setup
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
#if AppArch == "arm64"
; arm64 binaries only run on Windows 11 ARM devices
ArchitecturesAllowed=arm64
ArchitecturesInstallIn64BitMode=arm64
#else
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
#endif
UninstallDisplayIcon={app}\{#AppExe}
; Allow the user to elevate during install if they want to install for all users
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0.17763

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Recursively bundle everything flet placed in build/windows
Source: "..\..\build\windows\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
