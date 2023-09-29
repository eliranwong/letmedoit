import platform, os, config, sys, ctypes
from shutil import copyfile
cwd = os.path.dirname(config.myHandFile)
if os.getcwd() != cwd:
    os.chdir(cwd)
config.myHandAIFolder = cwd

def createShortcuts():
    thisOS = platform.system()
    appName = "myHand"
    # Windows icon
    if thisOS == "Windows":
        myappid = "myHand.ai"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        windowsIconPath = os.path.abspath(os.path.join(sys.path[0], "icons", f"{appName}.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(windowsIconPath)

    # Desktop shortcut
    # on Windows
    if thisOS == "Windows":
        desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop')
        shortcutDir = desktopPath if os.path.isdir(desktopPath) else cwd
        shortcutBat1 = os.path.join(shortcutDir, f"{appName}.bat")
        shortcutCommand1 = f'''powershell.exe -NoExit -Command "python '{config.myHandFile}'"'''
        # Create .bat for application shortcuts
        if not os.path.exists(shortcutBat1):
            try:
                with open(shortcutBat1, "w") as fileObj:
                    fileObj.write(shortcutCommand1)
            except:
                pass
    # on macOS
    # on iOS a-Shell app, ~/Desktop/ is invalid
    elif thisOS == "Darwin" and os.path.isdir("~/Desktop/"):
        shortcut_file = os.path.expanduser(f"~/Desktop/{appName}.command")
        if not os.path.isfile(shortcut_file):
            with open(shortcut_file, "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"cd {cwd}\n")
                f.write(f"{sys.executable} {config.myHandFile}\n")
            os.chmod(shortcut_file, 0o755)
    # additional shortcuts on Linux
    elif thisOS == "Linux":
        def desktopFileContent():
            iconPath = os.path.join(cwd, "icons", "myHandAI.png")
            return """#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Path={0}
Exec={1} {2}
Icon={3}
Name=myHand AI
""".format(cwd, sys.executable, config.myHandFile, iconPath)

        linuxDesktopFile = os.path.join(cwd, f"{appName}.desktop")
        if not os.path.exists(linuxDesktopFile):
            # Create .desktop shortcut
            with open(linuxDesktopFile, "w") as fileObj:
                fileObj.write(desktopFileContent())
            try:
                # Try to copy the newly created .desktop file to:
                from pathlib import Path
                # ~/.local/share/applications
                userAppDir = os.path.join(str(Path.home()), ".local", "share", "applications")
                userAppDirShortcut = os.path.join(userAppDir, f"{appName}.desktop")
                if not os.path.exists(userAppDirShortcut):
                    Path(userAppDir).mkdir(parents=True, exist_ok=True)
                    copyfile(linuxDesktopFile, userAppDirShortcut)
                # ~/Desktop
                homeDir = os.environ["HOME"]
                desktopPath = f"{homeDir}/Desktop"
                desktopPathShortcut = os.path.join(desktopPath, f"{appName}.desktop")
                if os.path.isfile(desktopPath) and not os.path.isfile(desktopPathShortcut):
                    copyfile(linuxDesktopFile, desktopPathShortcut)
            except:
                pass
