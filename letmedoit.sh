#!/usr/bin/env bash

# This is an example shell script to launch LetMeDoIt AI and have selected text as default entry.

# Install xsel to work with this script
# > sudo apt install xsel

# Usage, e.g. on Ubuntu:
# 1. Save this script as ~/letmedoit.sh
# 2. Run "chmod +x ~/letmedoit.sh"
# 3. Launch "Settubgs"
# 4. Go to "Keyboard" > "Keyboard Shortcuts" > "View and Customise Shortcuts" > "Custom Shortcuts"
# 5. Select "+" to add a custom shortcut
# Name: LetMeDoIt AI
# Command: /usr/bin/gnome-terminal --command ~/letmedoit.sh
# Shortcut: Ctrl + Alt + L

# get selected text with escaped double quotation marks, if any
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
# launch LetMeDoIt AI with selected text as default entry
~/apps/letmedoit/bin/python3 ~/apps/letmedoit/lib/python3.10/site-packages/letmedoit/main.py "$selected_text"
# Remarks: replace python path and letmedoit path in you case.
