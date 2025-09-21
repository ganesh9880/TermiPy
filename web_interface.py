#!/usr/bin/env python3
"""
Web Interface for Advanced Python Terminal
A web-based terminal interface using Flask.
"""

from flask import Flask, render_template, request, jsonify, session
import os
import json
from main import Terminal
import threading
import uuid

app = Flask(__name__)
app.secret_key = 'terminal_secret_key_2024'

# Store terminal instances per session
terminals = {}

def get_terminal():
    """Get or create terminal instance for current session"""
    session_id = session.get('terminal_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['terminal_id'] = session_id
    
    if session_id not in terminals:
        terminals[session_id] = Terminal()
    
    return terminals[session_id]

@app.route('/')
def index():
    """Main terminal page"""
    return render_template('terminal.html')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'service': 'CmdMate Terminal',
        'version': '1.0.0'
    }), 200

@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute a command and return the output"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'output': '', 'current_dir': ''})
        
        terminal = get_terminal()
        output = terminal.execute_command(command)
        current_dir = terminal.current_dir
        
        return jsonify({
            'output': output,
            'current_dir': current_dir,
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'output': f'Error: {str(e)}',
            'current_dir': '',
            'success': False
        })

@app.route('/history')
def get_history():
    """Get command history"""
    try:
        terminal = get_terminal()
        return jsonify({
            'history': terminal.command_history[-50:],  # Last 50 commands
            'success': True
        })
    except Exception as e:
        return jsonify({
            'history': [],
            'success': False,
            'error': str(e)
        })

@app.route('/system_info')
def get_system_info():
    """Get system information"""
    try:
        terminal = get_terminal()
        
        # Get memory info
        import psutil
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return jsonify({
            'memory': {
                'total': terminal.format_size(memory.total),
                'used': terminal.format_size(memory.used),
                'percent': memory.percent
            },
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'current_dir': terminal.current_dir,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def create_html_template():
    """Create the HTML template for the web interface"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Python Terminal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background-color: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            overflow: hidden;
        }
        
        .terminal-container {
            display: flex;
            height: 100vh;
        }
        
        .terminal-main {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .terminal-header {
            background-color: #2d2d30;
            padding: 10px 20px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .terminal-title {
            font-weight: bold;
            color: #ffffff;
        }
        
        .system-info {
            display: flex;
            gap: 20px;
            font-size: 12px;
        }
        
        .info-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .info-label {
            color: #888;
            margin-bottom: 2px;
        }
        
        .info-value {
            color: #4fc3f7;
            font-weight: bold;
        }
        
        .terminal-output {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background-color: #1e1e1e;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .terminal-line {
            margin-bottom: 2px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        
        .command-line {
            background-color: #2d2d30;
            padding: 10px 20px;
            border-top: 1px solid #3e3e42;
            display: flex;
            align-items: center;
        }
        
        .prompt {
            color: #4fc3f7;
            margin-right: 10px;
            font-weight: bold;
        }
        
        .command-input {
            flex: 1;
            background: transparent;
            border: none;
            color: #d4d4d4;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            outline: none;
        }
        
        .command-input::placeholder {
            color: #666;
        }
        
        .sidebar {
            width: 300px;
            background-color: #252526;
            border-left: 1px solid #3e3e42;
            padding: 20px;
            overflow-y: auto;
        }
        
        .sidebar-section {
            margin-bottom: 30px;
        }
        
        .sidebar-title {
            color: #ffffff;
            font-weight: bold;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #3e3e42;
        }
        
        .history-item {
            padding: 5px 10px;
            margin-bottom: 2px;
            background-color: #2d2d30;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            transition: background-color 0.2s;
        }
        
        .history-item:hover {
            background-color: #3e3e42;
        }
        
        .help-section {
            font-size: 12px;
            line-height: 1.4;
        }
        
        .help-command {
            color: #4fc3f7;
            font-weight: bold;
        }
        
        .help-description {
            color: #888;
            margin-left: 10px;
        }
        
        .error {
            color: #f48771;
        }
        
        .success {
            color: #4fc3f7;
        }
        
        .loading {
            color: #ffa726;
        }
        
        .ai-command {
            color: #c678dd;
            font-style: italic;
        }
        
        .system-command {
            color: #98c379;
        }
        
        .file-command {
            color: #e06c75;
        }
        
        .directory-command {
            color: #61dafb;
        }
        
        .monitor-command {
            color: #ffd43b;
        }
        
        .status-bar {
            background-color: #2d2d30;
            padding: 5px 20px;
            font-size: 12px;
            color: #888;
            border-top: 1px solid #3e3e42;
            display: flex;
            justify-content: space-between;
        }
        
        .status-left {
            display: flex;
            gap: 20px;
        }
        
        .status-right {
            color: #4fc3f7;
        }
        
        .progress-bar {
            width: 100px;
            height: 4px;
            background-color: #3e3e42;
            border-radius: 2px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background-color: #4fc3f7;
            transition: width 0.3s ease;
        }
        
        @media (max-width: 768px) {
            .terminal-container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                height: 200px;
                border-left: none;
                border-top: 1px solid #3e3e42;
            }
        }
    </style>
</head>
<body>
    <div class="terminal-container">
        <div class="terminal-main">
            <div class="terminal-header">
                <div class="terminal-title">Advanced Python Terminal</div>
                <div class="system-info">
                    <div class="info-item">
                        <div class="info-label">CPU</div>
                        <div class="info-value" id="cpu-usage">--</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Memory</div>
                        <div class="info-value" id="memory-usage">--</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Directory</div>
                        <div class="info-value" id="current-dir">--</div>
                    </div>
                </div>
            </div>
            
            <div class="terminal-output" id="terminal-output">
                <div class="terminal-line success">Advanced Python Terminal - Web Interface</div>
                <div class="terminal-line">Type 'help' for available commands or use the sidebar for quick access</div>
                <div class="terminal-line">AI commands: Try "ai create folder test" or "ai show memory usage"</div>
                <div class="terminal-line">"</div>
            </div>
            
            <div class="command-line">
                <span class="prompt" id="prompt">~></span>
                <input type="text" class="command-input" id="command-input" placeholder="Enter command..." autofocus>
            </div>
            
            <div class="status-bar">
                <div class="status-left">
                    <span>Ready</span>
                    <span id="command-count">0 commands</span>
                </div>
                <div class="status-right">
                    <span id="current-time"></span>
                </div>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-title">Command History</div>
                <div id="history-list">
                    <div class="history-item">No commands yet</div>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">Quick Commands</div>
                <div class="help-section">
                    <div class="help-command">ls -la</div>
                    <div class="help-description">List all files</div>
                    
                    <div class="help-command">ps</div>
                    <div class="help-description">Show processes</div>
                    
                    <div class="help-command">mem</div>
                    <div class="help-description">Memory usage</div>
                    
                    <div class="help-command">ai help</div>
                    <div class="help-description">AI commands</div>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">System Monitor</div>
                <div class="help-section">
                    <div>CPU Usage:</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                    </div>
                    <div>Memory Usage:</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class TerminalWeb {
            constructor() {
                this.commandHistory = [];
                this.historyIndex = -1;
                this.commandCount = 0;
                this.currentDir = '~';
                
                this.initializeElements();
                this.setupEventListeners();
                this.updateSystemInfo();
                this.updateTime();
                this.loadHistory();
                
                // Update system info every 5 seconds
                setInterval(() => this.updateSystemInfo(), 5000);
                setInterval(() => this.updateTime(), 1000);
            }
            
            initializeElements() {
                this.output = document.getElementById('terminal-output');
                this.input = document.getElementById('command-input');
                this.prompt = document.getElementById('prompt');
                this.historyList = document.getElementById('history-list');
                this.commandCountEl = document.getElementById('command-count');
                this.currentDirEl = document.getElementById('current-dir');
                this.cpuUsage = document.getElementById('cpu-usage');
                this.memoryUsage = document.getElementById('memory-usage');
                this.cpuProgress = document.getElementById('cpu-progress');
                this.memoryProgress = document.getElementById('memory-progress');
            }
            
            setupEventListeners() {
                this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
                this.input.addEventListener('input', (e) => this.handleInput(e));
            }
            
            handleKeyDown(e) {
                if (e.key === 'Enter') {
                    this.executeCommand();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.navigateHistory(-1);
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.navigateHistory(1);
                } else if (e.key === 'Tab') {
                    e.preventDefault();
                    this.autoComplete();
                }
            }
            
            handleInput(e) {
                // Real-time command validation or suggestions could go here
            }
            
            async executeCommand() {
                const command = this.input.value.trim();
                if (!command) return;
                
                // Add command to history
                this.commandHistory.push(command);
                this.historyIndex = this.commandHistory.length;
                this.commandCount++;
                this.commandCountEl.textContent = `${this.commandCount} commands`;
                
                // Display command
                this.addOutputLine(`<span class="prompt">${this.prompt.textContent}</span> ${command}`, 'command');
                
                // Clear input
                this.input.value = '';
                
                // Show loading
                const loadingId = this.addOutputLine('Executing...', 'loading');
                
                try {
                    const response = await fetch('/execute', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ command: command })
                    });
                    
                    const data = await response.json();
                    
                    // Remove loading message
                    this.removeOutputLine(loadingId);
                    
                    // Display output
                    if (data.success) {
                        this.addOutputLine(data.output, 'output');
                        this.currentDir = data.current_dir;
                        this.updatePrompt();
                    } else {
                        this.addOutputLine(data.output, 'error');
                    }
                    
                } catch (error) {
                    this.removeOutputLine(loadingId);
                    this.addOutputLine(`Error: ${error.message}`, 'error');
                }
                
                // Update history display
                this.updateHistoryDisplay();
                
                // Scroll to bottom
                this.scrollToBottom();
            }
            
            addOutputLine(content, type = 'output') {
                const line = document.createElement('div');
                line.className = `terminal-line ${type}`;
                line.innerHTML = content;
                
                const id = Date.now() + Math.random();
                line.setAttribute('data-id', id);
                
                this.output.appendChild(line);
                return id;
            }
            
            removeOutputLine(id) {
                const line = document.querySelector(`[data-id="${id}"]`);
                if (line) {
                    line.remove();
                }
            }
            
            navigateHistory(direction) {
                if (this.commandHistory.length === 0) return;
                
                this.historyIndex += direction;
                
                if (this.historyIndex < 0) {
                    this.historyIndex = 0;
                } else if (this.historyIndex >= this.commandHistory.length) {
                    this.historyIndex = this.commandHistory.length;
                    this.input.value = '';
                    return;
                }
                
                this.input.value = this.commandHistory[this.historyIndex] || '';
            }
            
            autoComplete() {
                // Simple auto-completion for common commands
                const commonCommands = ['ls', 'cd', 'pwd', 'mkdir', 'rm', 'cp', 'mv', 'cat', 'echo', 'ps', 'mem', 'cpu', 'help', 'ai'];
                const input = this.input.value.toLowerCase();
                
                const matches = commonCommands.filter(cmd => cmd.startsWith(input));
                if (matches.length === 1) {
                    this.input.value = matches[0];
                } else if (matches.length > 1) {
                    // Show suggestions
                    this.addOutputLine(`Suggestions: ${matches.join(', ')}`, 'help');
                }
            }
            
            updatePrompt() {
                const dirName = this.currentDir.split('/').pop() || '~';
                this.prompt.textContent = `${dirName}>`;
                this.currentDirEl.textContent = this.currentDir;
            }
            
            updateHistoryDisplay() {
                this.historyList.innerHTML = '';
                
                if (this.commandHistory.length === 0) {
                    this.historyList.innerHTML = '<div class="history-item">No commands yet</div>';
                    return;
                }
                
                // Show last 10 commands
                const recentHistory = this.commandHistory.slice(-10).reverse();
                recentHistory.forEach(cmd => {
                    const item = document.createElement('div');
                    item.className = 'history-item';
                    item.textContent = cmd;
                    item.addEventListener('click', () => {
                        this.input.value = cmd;
                        this.input.focus();
                    });
                    this.historyList.appendChild(item);
                });
            }
            
            async loadHistory() {
                try {
                    const response = await fetch('/history');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.commandHistory = data.history;
                        this.historyIndex = this.commandHistory.length;
                        this.updateHistoryDisplay();
                    }
                } catch (error) {
                    console.error('Failed to load history:', error);
                }
            }
            
            async updateSystemInfo() {
                try {
                    const response = await fetch('/system_info');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.cpuUsage.textContent = `${data.cpu.percent.toFixed(1)}%`;
                        this.memoryUsage.textContent = `${data.memory.percent.toFixed(1)}%`;
                        
                        this.cpuProgress.style.width = `${data.cpu.percent}%`;
                        this.memoryProgress.style.width = `${data.memory.percent}%`;
                        
                        if (data.current_dir) {
                            this.currentDir = data.current_dir;
                            this.updatePrompt();
                        }
                    }
                } catch (error) {
                    console.error('Failed to update system info:', error);
                }
            }
            
            updateTime() {
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                document.getElementById('current-time').textContent = timeString;
            }
            
            scrollToBottom() {
                this.output.scrollTop = this.output.scrollHeight;
            }
        }
        
        // Initialize terminal when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new TerminalWeb();
        });
    </script>
</body>
</html>'''
    
    with open('templates/terminal.html', 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    create_html_template()
    
    print("Starting web terminal interface...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
