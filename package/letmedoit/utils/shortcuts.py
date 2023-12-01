from letmedoit import config
from pathlib import Path
import platform, os, sys, ctypes, subprocess, re
import shutil

def createShortcuts():
    thisOS = platform.system()
    appName = config.letMeDoItName.split()[0]
    # Windows icon
    if thisOS == "Windows":
        myappid = "letmedoit.ai"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        windowsIconPath = os.path.abspath(os.path.join(sys.path[0], "icons", f"{appName}.ico"))
        if not os.path.isfile(windowsIconPath):
            windowsIconPath = os.path.abspath(os.path.join(sys.path[0], "icons", "LetMeDoIt.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(windowsIconPath)

    # Desktop shortcut
    # on Windows
    if thisOS == "Windows":
        desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
        shortcutBat1 = os.path.join(config.letMeDoItAIFolder, f"{appName}.bat")
        shortcutCommand1 = f'''powershell.exe -NoExit -Command "{sys.executable} '{config.letMeDoItFile} -f %1'"'''
        # Create .bat for application shortcuts
        if not os.path.exists(shortcutBat1):
            try:
                print("creating shortcut ...")
                with open(shortcutBat1, "w") as fileObj:
                    fileObj.write(shortcutCommand1)
                print(f"Created: {shortcutBat1}")
                shutil.copy(shortcutBat1, desktopPath) # overwrites older version
                print("Copied to Desktop!")
            except:
                pass
    # on macOS
    # on iOS a-Shell app, ~/Desktop/ is invalid
    elif thisOS == "Darwin":
        desktopPath = os.path.expanduser("~/Desktop")
        if os.path.isdir(desktopPath):
            shortcut_file = os.path.join(config.letMeDoItAIFolder, f"{appName}.command")
            if not os.path.isfile(shortcut_file):
                print("creating shortcut ...")
                with open(shortcut_file, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write(f"cd {config.letMeDoItAIFolder}\n")
                    f.write(f"{sys.executable} {config.letMeDoItFile}\n")
                os.chmod(shortcut_file, 0o755)
                print(f"Created: {shortcut_file}")
                shutil.copy(shortcut_file, desktopPath) # overwrites older version
                print("Copied to Desktop!")

    # additional shortcuts on Linux
    elif thisOS == "Linux":
        def desktopFileContent():
            iconPath = os.path.join(config.letMeDoItAIFolder, "icons", f"{appName}.png")
            if not os.path.isfile(iconPath):
                iconPath = os.path.join(config.letMeDoItAIFolder, "icons", "LetMeDoIt.png")
            return """#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Path={0}
Exec={1} {2}
Icon={3}
Name={4}
""".format(config.letMeDoItAIFolder, sys.executable, config.letMeDoItFile, iconPath, config.letMeDoItName)

        linuxDesktopFile = os.path.join(config.letMeDoItAIFolder, f"{appName}.desktop")
        if not os.path.exists(linuxDesktopFile):
            print("creating shortcut ...")
            # Create .desktop shortcut
            with open(linuxDesktopFile, "w") as fileObj:
                fileObj.write(desktopFileContent())
            print(f"Created: {linuxDesktopFile}")
            try:
                # Try to copy the newly created .desktop file to:
                from pathlib import Path
                # ~/.local/share/applications
                userAppDir = os.path.join(str(Path.home()), ".local", "share", "applications")
                Path(userAppDir).mkdir(parents=True, exist_ok=True)
                shutil.copy(linuxDesktopFile, userAppDir) # overwrites older version
                print(f"Copied to '{userAppDir}'!")
                # ~/Desktop
                desktopPath = os.path.expanduser("~/Desktop")
                if os.path.isdir(desktopPath):
                    shutil.copy(linuxDesktopFile, desktopPath) # overwrites older version
                    print("Copied to Desktop!")
            except:
                pass
    createUtilities()
    #createAppAlias()

def createUtilities():
    first_name = config.letMeDoItName.split()[0]
    storage = os.path.join(os.path.expanduser('~'), first_name.lower())
    try:
        Path(storage).mkdir(parents=True, exist_ok=True)
    except:
        pass

    thisOS = platform.system()
    if thisOS == "Windows":
        work_with_text_script = f'''param (
    [string]$selected_text
)
Start-Process "{sys.executable} {config.letMeDoItFile} $selected_text"'''
        work_with_text_script_path = os.path.join(storage, f"{first_name}.ps1")
        with open(work_with_text_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
    elif thisOS == "Linux":
        # work with text selection
        # To use this script, users need to:
        # 1. Launch "Settings"
        # 2. Go to "Keyboard" > "Keyboard Shortcuts" > "View and Customise Shortcuts" > "Custom Shortcuts"
        # 3. Select "+" to add a custom shortcut and enter the following information, e.g.:
        # Name: LetMeDoIt AI
        # Command: /usr/bin/gnome-terminal --command ~/letmedoit/letmedoit.sh
        # Shortcut: Ctrl + Alt + L
        work_with_text_script = f'''#!/usr/bin/env bash
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
{sys.executable} {config.letMeDoItFile} "$selected_text"'''
        work_with_text_script_path = os.path.join(storage, first_name)
        with open(work_with_text_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
        # work with files or folders selection via NAUTILUS; right-click > scripts > LetMeDoIt
        work_with_files_script = f'''#!/usr/bin/env bash
mkdir -p {storage}
# Get the selected file or folder path
path="$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS"
echo "$path" > {storage}/selected_files.txt
/usr/bin/gnome-terminal --command "{sys.executable} {config.letMeDoItFile} -f {storage}/selected_files.txt"'''
        work_with_files_script_path = os.path.expanduser(f"~/.local/share/nautilus/scripts/{first_name}")
        with open(work_with_files_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_files_script)
        # make script files executable
        for i in (work_with_text_script_path, work_with_files_script_path):
            os.chmod(i, 0o755)
    elif thisOS == "Darwin":
        file1 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Text_workflow/Contents/document.wflow")
        file2 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Files_workflow/Contents/document.wflow")
        for i in (file1, file2):
            with open(i, "r", encoding="utf-8") as fileObj:
                content = fileObj.read()
            search_replace = (
                ("~/letmedoit", storage),
                ("\[LETMEDOIT_PATH\]", f"{sys.executable} {config.letMeDoItFile}"),
            )
            for search, replace in search_replace:
                content = re.sub(search, replace, content)
            with open(i, "w", encoding="utf-8") as fileObj:
                fileObj.write(content)
        file1 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Files_workflow/Contents/Info.plist")
        file2 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Text_workflow/Contents/Info.plist")
        for i in (file1, file2):
            with open(i, "r", encoding="utf-8") as fileObj:
                content = fileObj.read()
            content = re.sub("LetMeDoIt", first_name, content)
            with open(i, "w", encoding="utf-8") as fileObj:
                fileObj.write(content)
        folder1 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Files_workflow")
        folder1_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Files.workflow")
        if os.path.isdir(folder1_dest):
            shutil.rmtree(folder1_dest, ignore_errors=True)
        shutil.copytree(folder1, folder1_dest)
        folder2 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Text_workflow")
        folder2_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Text.workflow")
        if os.path.isdir(folder2_dest):
            shutil.rmtree(folder2_dest, ignore_errors=True)
        shutil.copytree(folder2, folder2_dest)
        folder3 = os.path.join(config.letMeDoItAIFolder, "icons")
        folder3_dest = os.path.join(storage, "icons")
        shutil.copytree(folder3, folder3_dest)

def createAppAlias():
    with open(os.path.join(config.letMeDoItAIFolder, "package_name.txt"), "r", encoding="utf-8") as fileObj:
        package = fileObj.read()
    alias = package
    target = f"{sys.executable} {config.letMeDoItFile}"

    findAlias = "/bin/bash -ic 'alias letmedoit'" # -c alone does not work
    aliasOutput, *_ = subprocess.Popen(findAlias, shell=True, stdout=subprocess.PIPE, text=True).communicate()

    if not aliasOutput.strip() == f"""alias letmedoit='{target}'""":
        print("creating alias ...")
        def addAliasToLoginProfile(profile, content):
            if os.path.isfile(profile):
                content = f"\r\n{content}" if config.thisPlatform == "Windows" else f"\n{content}"
            try:
                with open(profile, "a", encoding="utf-8") as fileObj:
                    fileObj.write(content)
            except:
                pass
        home = os.path.expanduser("~")
        if config.thisPlatform == "Windows":
            """# command prompt
            profile = os.path.join(home, "AutoRun.bat")
            content = f'''doskey {alias}="{target}"'''
            addAliasToLoginProfile(profile, content)
            # powershell
            profile = os.path.join(home, "Documents", "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1")
            content = f'''Set-Alias -Name {alias} -Value "{target}"'''
            addAliasToLoginProfile(profile, content)"""
            pass
        else:
            content = f"""alias {alias}='{target}'"""
            try:
                for profile in (".bash_profile", ".zprofile", ".bashrc", ".zshrc"):
                    addAliasToLoginProfile(os.path.join(home, profile), content)
                print(content)
            except:
                pass