#!/usr/bin/env python3
"""
Deployment script for CmdMate Terminal
Provides multiple deployment options for the terminal application.
"""

import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = ['psutil', 'flask']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✓ All dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error installing dependencies: {e}")
            return False
    
    return True

def create_desktop_shortcut():
    """Create desktop shortcut for easy access"""
    print("\nCreating desktop shortcut...")
    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    current_dir = os.getcwd()
    
    if platform.system() == "Windows":
        # Create Windows batch file
        batch_content = f"""@echo off
cd /d "{current_dir}"
python main.py
pause
"""
        batch_file = os.path.join(desktop_path, "CmdMate.bat")
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        print(f"✓ Desktop shortcut created: {batch_file}")
        
        # Create web interface shortcut
        web_batch_content = f"""@echo off
cd /d "{current_dir}"
python main.py --web
pause
"""
        web_batch_file = os.path.join(desktop_path, "CmdMate_Web.bat")
        with open(web_batch_file, 'w') as f:
            f.write(web_batch_content)
        print(f"✓ Web interface shortcut created: {web_batch_file}")
    
    else:
        # Create Unix shell script
        shell_content = f"""#!/bin/bash
cd "{current_dir}"
python3 main.py
"""
        shell_file = os.path.join(desktop_path, "CmdMate.sh")
        with open(shell_file, 'w') as f:
            f.write(shell_content)
        os.chmod(shell_file, 0o755)
        print(f"✓ Desktop shortcut created: {shell_file}")

def create_system_service():
    """Create system service for auto-start (Linux/macOS)"""
    if platform.system() == "Windows":
        print("System service creation not supported on Windows")
        return
    
    print("\nCreating system service...")
    current_dir = os.getcwd()
    python_path = sys.executable
    
    service_content = f"""[Unit]
Description=CmdMate Terminal Service
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={current_dir}
ExecStart={python_path} main.py --web
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/etc/systemd/system/cmdmate.service"
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        print(f"✓ System service created: {service_file}")
        print("To enable the service, run: sudo systemctl enable cmdmate.service")
        print("To start the service, run: sudo systemctl start cmdmate.service")
    except PermissionError:
        print("✗ Permission denied. Run with sudo to create system service")

def create_docker_deployment():
    """Create Docker deployment files"""
    print("\nCreating Docker deployment files...")
    
    # Dockerfile
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    procps \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Create non-root user
RUN useradd -m -u 1000 cmdmate && chown -R cmdmate:cmdmate /app
USER cmdmate

# Start the application
CMD ["python", "main.py", "--web", "--host", "0.0.0.0"]
"""
    
    with open("Dockerfile", 'w') as f:
        f.write(dockerfile_content)
    print("✓ Dockerfile created")
    
    # docker-compose.yml
    compose_content = """version: '3.8'

services:
  cmdmate:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
"""
    
    with open("docker-compose.yml", 'w') as f:
        f.write(compose_content)
    print("✓ docker-compose.yml created")
    
    # .dockerignore
    dockerignore_content = """__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.gitignore
README.md
FEATURES.md
deploy.py
install.py
*.log
"""
    
    with open(".dockerignore", 'w') as f:
        f.write(dockerignore_content)
    print("✓ .dockerignore created")
    
    print("\nDocker deployment commands:")
    print("  docker build -t cmdmate .")
    print("  docker run -p 5000:5000 cmdmate")
    print("  # Or use docker-compose:")
    print("  docker-compose up -d")

def create_heroku_deployment():
    """Create Heroku deployment files"""
    print("\nCreating Heroku deployment files...")
    
    # Procfile
    procfile_content = "web: python main.py --web --host 0.0.0.0 --port $PORT"
    with open("Procfile", 'w') as f:
        f.write(procfile_content)
    print("✓ Procfile created")
    
    # runtime.txt
    runtime_content = "python-3.9.18"
    with open("runtime.txt", 'w') as f:
        f.write(runtime_content)
    print("✓ runtime.txt created")
    
    # app.json for Heroku
    app_json_content = """{
  "name": "CmdMate Terminal",
  "description": "Advanced Python Terminal with NLP capabilities",
  "repository": "https://github.com/ganesh9880/CmdMate.git",
  "keywords": ["python", "terminal", "nlp", "flask"],
  "success_url": "/",
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}"""
    
    with open("app.json", 'w') as f:
        f.write(app_json_content)
    print("✓ app.json created")
    
    print("\nHeroku deployment commands:")
    print("  heroku create your-app-name")
    print("  git push heroku main")
    print("  heroku open")

def create_railway_deployment():
    """Create Railway deployment configuration"""
    print("\nCreating Railway deployment files...")
    
    # railway.json
    railway_content = """{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py --web --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}"""
    
    with open("railway.json", 'w') as f:
        f.write(railway_content)
    print("✓ railway.json created")
    
    print("\nRailway deployment:")
    print("  1. Connect your GitHub repository to Railway")
    print("  2. Railway will automatically detect and deploy")
    print("  3. Set PORT environment variable if needed")

def start_local_server():
    """Start the local development server"""
    print("\nStarting local development server...")
    print("Web interface will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "main.py", "--web"])
    except KeyboardInterrupt:
        print("\nServer stopped")

def main():
    """Main deployment function"""
    print("=" * 60)
    print("CMDMATE TERMINAL - DEPLOYMENT OPTIONS")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies first")
        return
    
    print("\nDeployment Options:")
    print("1. Local Development Server")
    print("2. Create Desktop Shortcuts")
    print("3. Create System Service (Linux/macOS)")
    print("4. Docker Deployment")
    print("5. Heroku Deployment")
    print("6. Railway Deployment")
    print("7. All Options")
    
    try:
        choice = input("\nSelect deployment option (1-7): ").strip()
        
        if choice == "1":
            start_local_server()
        elif choice == "2":
            create_desktop_shortcut()
        elif choice == "3":
            create_system_service()
        elif choice == "4":
            create_docker_deployment()
        elif choice == "5":
            create_heroku_deployment()
        elif choice == "6":
            create_railway_deployment()
        elif choice == "7":
            create_desktop_shortcut()
            create_system_service()
            create_docker_deployment()
            create_heroku_deployment()
            create_railway_deployment()
        else:
            print("Invalid choice")
            return
        
        print("\n" + "=" * 60)
        print("DEPLOYMENT COMPLETED!")
        print("=" * 60)
        
        if choice in ["1", "7"]:
            print("\nStarting local server...")
            start_local_server()
    
    except KeyboardInterrupt:
        print("\nDeployment cancelled")
    except Exception as e:
        print(f"Error during deployment: {e}")

if __name__ == "__main__":
    main()
