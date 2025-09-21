#!/usr/bin/env python3
"""
Quick Start Script for CmdMate Terminal
This script provides an easy way to start the terminal with different options.
"""

import sys
import os
import subprocess
import webbrowser
import time

def print_banner():
    """Print the CmdMate banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CmdMate Terminal                          ║
    ║              Advanced Python Terminal with NLP               ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import psutil
        import flask
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run: pip install -r requirements.txt")
            return False

def start_cli():
    """Start CLI terminal"""
    print("🚀 Starting CmdMate CLI Terminal...")
    print("Type 'help' for available commands or 'exit' to quit")
    print("=" * 60)
    subprocess.run([sys.executable, "main.py"])

def start_web():
    """Start web interface"""
    print("🌐 Starting CmdMate Web Interface...")
    print("The web interface will open in your browser automatically")
    print("If it doesn't open, go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        subprocess.run([sys.executable, "main.py", "--web"])
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")

def show_help():
    """Show help information"""
    help_text = """
    🎯 CmdMate Terminal - Quick Start Options:
    
    1. CLI Terminal     - Command line interface
    2. Web Interface    - Modern web-based interface
    3. Help            - Show this help
    4. Exit            - Exit the program
    
    🌟 Features:
    • Natural Language Commands (no 'ai' prefix needed!)
    • File Operations (ls, cd, mkdir, rm, etc.)
    • System Monitoring (CPU, memory, processes)
    • Web Interface with real-time monitoring
    • Cross-platform support (Windows, macOS, Linux)
    
    💡 Examples:
    • create folder my_project
    • show files
    • show memory
    • what can you do
    
    📚 Documentation:
    • README.md - Complete documentation
    • DEPLOYMENT.md - Deployment guide
    • FEATURES.md - Feature list
    """
    print(help_text)

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    while True:
        print("\n" + "=" * 60)
        print("🎯 CmdMate Terminal - Quick Start")
        print("=" * 60)
        print("1. 🖥️  CLI Terminal")
        print("2. 🌐 Web Interface")
        print("3. ❓ Help")
        print("4. 🚪 Exit")
        
        try:
            choice = input("\nSelect an option (1-4): ").strip()
            
            if choice == "1":
                start_cli()
            elif choice == "2":
                start_web()
            elif choice == "3":
                show_help()
            elif choice == "4":
                print("👋 Goodbye! Thanks for using CmdMate Terminal!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for using CmdMate Terminal!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
