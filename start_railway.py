#!/usr/bin/env python3
"""
Railway-specific startup script
This ensures proper production configuration for Railway deployment
"""

import os
import sys
import subprocess

def start_railway():
    """Start the application for Railway deployment"""
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting CmdMate Terminal on port {port}")
    print("Environment: Production")
    print("Server: Gunicorn")
    
    # Use Gunicorn for production
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '1',
        '--timeout', '120',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'wsgi:app'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Gunicorn: {e}")
        print("Falling back to Flask development server...")
        
        # Fallback to Flask if Gunicorn fails
        from web_interface import app
        app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    start_railway()
