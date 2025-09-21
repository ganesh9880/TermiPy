#!/usr/bin/env python3
"""Create desktop shortcuts for CmdMate Terminal"""

import os
import sys

def create_shortcuts():
    current_dir = os.getcwd()
    
    # CLI Terminal shortcut
    cli_content = f"""@echo off
cd /d "{current_dir}"
python main.py
pause
"""
    
    cli_file = os.path.join(current_dir, "CmdMate.bat")
    with open(cli_file, 'w') as f:
        f.write(cli_content)
    print(f"✓ CLI Terminal shortcut: {cli_file}")
    
    # Web Interface shortcut
    web_content = f"""@echo off
cd /d "{current_dir}"
python main.py --web
pause
"""
    
    web_file = os.path.join(current_dir, "CmdMate_Web.bat")
    with open(web_file, 'w') as f:
        f.write(web_content)
    print(f"✓ Web Interface shortcut: {web_file}")
    
    print("\nShortcuts created successfully!")
    print("You can now double-click the shortcuts to run CmdMate")
    print("Copy these files to your desktop for easy access")

if __name__ == "__main__":
    create_shortcuts()
