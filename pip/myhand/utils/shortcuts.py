from myhand import config
import platform, os, sys, ctypes, subprocess
import shutil

def createShortcuts():
    thisOS = platform.system()
    appName = "MyHand"
    # Windows icon
    if thisOS == "Windows":
        myappid = "myhand.bot"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        windowsIconPath = os.path.abspath(os.path.join(sys.path[0], "icons", f"{appName}.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(windowsIconPath)

    # Desktop shortcut
    # on Windows
    if thisOS == "Windows":
        desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
        shortcutBat1 = os.path.join(config.myHandAIFolder, f"{appName}.bat")
        shortcutCommand1 = f'''powershell.exe -NoExit -Command "python '{config.myHandFile}'"'''
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
            shortcut_file = os.path.join(config.myHandAIFolder, f"{appName}.command")
            if not os.path.isfile(shortcut_file):
                print("creating shortcut ...")
                with open(shortcut_file, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write(f"cd {config.myHandAIFolder}\n")
                    f.write(f"{sys.executable} {config.myHandFile}\n")
                os.chmod(shortcut_file, 0o755)
                print(f"Created: {shortcut_file}")
                shutil.copy(shortcut_file, desktopPath) # overwrites older version
                print("Copied to Desktop!")

    # additional shortcuts on Linux
    elif thisOS == "Linux":
        def desktopFileContent():
            iconPath = os.path.join(config.myHandAIFolder, "icons", "myHandAI.png")
            return """#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Path={0}
Exec={1} {2}
Icon={3}
Name=MyHand Bot
""".format(config.myHandAIFolder, sys.executable, config.myHandFile, iconPath)

        linuxDesktopFile = os.path.join(config.myHandAIFolder, f"{appName}.desktop")
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
    #createAppAlias()

def createAppAlias():
    alias = "myhand"
    target = f"{sys.executable} {config.myHandFile}"

    findAlias = "/bin/bash -ic 'alias myhand'" # -c alone does not work
    aliasOutput, *_ = subprocess.Popen(findAlias, shell=True, stdout=subprocess.PIPE, text=True).communicate()

    if not aliasOutput.strip() == f"""alias myhand='{target}'""":
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