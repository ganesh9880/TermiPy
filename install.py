#!/usr/bin/env python3
"""
Installation script for Advanced Python Terminal
This script helps set up the terminal with all required dependencies.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = ["templates", "logs"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        except Exception as e:
            print(f"✗ Error creating directory {directory}: {e}")
            return False
    
    return True

def test_installation():
    """Test if the installation works"""
    print("Testing installation...")
    
    try:
        # Test importing the terminal
        from main import Terminal
        
        # Create a test terminal instance
        terminal = Terminal()
        
        # Test a simple command
        result = terminal.execute_command("echo 'Installation test successful'")
        
        if "Installation test successful" in result:
            print("✓ Installation test passed")
            return True
        else:
            print("✗ Installation test failed")
            return False
            
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return False

def create_launcher_scripts():
    """Create launcher scripts for different platforms"""
    print("Creating launcher scripts...")
    
    # Windows batch file
    if platform.system() == "Windows":
        batch_content = """@echo off
echo Starting Advanced Python Terminal...
python main.py
pause
"""
        try:
            with open("start_terminal.bat", "w") as f:
                f.write(batch_content)
            print("✓ Created start_terminal.bat")
        except Exception as e:
            print(f"✗ Error creating batch file: {e}")
    
    # Unix shell script
    shell_content = """#!/bin/bash
echo "Starting Advanced Python Terminal..."
python3 main.py
"""
    try:
        with open("start_terminal.sh", "w") as f:
            f.write(shell_content)
        os.chmod("start_terminal.sh", 0o755)
        print("✓ Created start_terminal.sh")
    except Exception as e:
        print(f"✗ Error creating shell script: {e}")

def main():
    """Main installation function"""
    print("=" * 60)
    print("ADVANCED PYTHON TERMINAL - INSTALLATION")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version}")
    print(f"✓ Platform: {platform.system()} {platform.release()}")
    print()
    
    # Install dependencies
    if not install_dependencies():
        print("Installation failed: Could not install dependencies")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("Installation failed: Could not create directories")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("Installation failed: Test failed")
        sys.exit(1)
    
    # Create launcher scripts
    create_launcher_scripts()
    
    print()
    print("=" * 60)
    print("INSTALLATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Usage:")
    print("  CLI Terminal:    python main.py")
    print("  Web Interface:   python main.py --web")
    print("  Demo:           python demo.py")
    print()
    
    if platform.system() == "Windows":
        print("  Windows:        start_terminal.bat")
    else:
        print("  Unix/Linux:     ./start_terminal.sh")
    
    print()
    print("For help: python main.py --help")
    print("For web interface: python main.py --web")
    print("Then open: http://localhost:5000")

if __name__ == "__main__":
    main()
