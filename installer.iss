; SafwaanBuddy Ultimate++ v7.0 - Inno Setup Installer Script
; This script creates a Windows installer that includes all dependencies

#define MyAppName "SafwaanBuddy Ultimate++"
#define MyAppVersion "7.0.0"
#define MyAppPublisher "SafwaanBuddy Team"
#define MyAppURL "https://github.com/safwaanbuddy/ultimate-agent"
#define MyAppExeName "SafwaanBuddy.exe"

[Setup]
; Application information
AppId={{8F9A5B2C-1E3D-4A7B-9C6E-2F8D5A3B1C7E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\SafwaanBuddy
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer_output
OutputBaseFilename=SafwaanBuddy-Ultimate-v{#MyAppVersion}-Setup
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable and all distribution files
Source: "dist\SafwaanBuddy\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Configuration files
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
; Data files
Source: "data\profiles\*"; DestDir: "{app}\data\profiles"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "data\templates\*"; DestDir: "{app}\data\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Configuration"; Filename: "{app}\config\config.yaml"
Name: "{group}\README"; Filename: "{app}\README.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
var
  WelcomeLabel: TNewStaticText;
begin
  WelcomeLabel := TNewStaticText.Create(WizardForm);
  WelcomeLabel.Parent := WizardForm.WelcomePage;
  WelcomeLabel.Caption := 'This will install SafwaanBuddy Ultimate++ v7.0 - ' +
    'A comprehensive Windows AI assistant with voice control and automation.';
  WelcomeLabel.AutoSize := True;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  // You can add pre-installation checks here
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Post-installation tasks
    // Create logs directory
    if not DirExists(ExpandConstant('{app}\logs')) then
      CreateDir(ExpandConstant('{app}\logs'));
    
    // Create data directories if they don't exist
    if not DirExists(ExpandConstant('{app}\data\workflows')) then
      CreateDir(ExpandConstant('{app}\data\workflows'));
    
    if not DirExists(ExpandConstant('{app}\data\models\vosk')) then
      ForceDirectories(ExpandConstant('{app}\data\models\vosk'));
    
    if not DirExists(ExpandConstant('{app}\data\cache')) then
      CreateDir(ExpandConstant('{app}\data\cache'));
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\data\cache"
Type: filesandordirs; Name: "{app}\__pycache__"

[Messages]
WelcomeLabel1=Welcome to [name] Setup
WelcomeLabel2=This will install [name/ver] on your computer.%n%nAll required dependencies are included in this installer.%n%nOptional components (Vosk models, Tesseract OCR) can be installed separately for enhanced functionality.
