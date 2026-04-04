[Setup]
AppName=DMP
AppVersion={#APP_VERSION}
DefaultDirName={autopf}\DMP
DefaultGroupName=DMP
OutputDir=installer
OutputBaseFilename=dmp-windows-x64-setup
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\dmp.exe

[Files]
Source: "dist\dmp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DMP"; Filename: "{app}\dmp.exe"
Name: "{group}\Uninstall DMP"; Filename: "{uninstallexe}"
Name: "{commondesktop}\DMP"; Filename: "{app}\dmp.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\dmp.exe"; Description: "Launch DMP"; Flags: nowait postinstall skipifsilent
