#!/usr/bin/env python3
"""
Advanced Python Terminal
A fully functioning terminal with file operations, AI queries, and system monitoring.
"""

import os
import sys
import subprocess
import shutil
import psutil
import json
import readline
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime
import threading
import time

class Terminal:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.command_history = []
        self.history_file = "terminal_history.json"
        self.load_history()
        
        # Initialize readline for command history and auto-completion
        readline.set_history_length(1000)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.complete_command)
        
    def load_history(self):
        """Load command history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.command_history = json.load(f)
                # Add to readline history
                for cmd in self.command_history[-50:]:  # Load last 50 commands
                    readline.add_history(cmd)
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
    
    def save_history(self):
        """Save command history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.command_history, f)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def complete_command(self, text, state):
        """Auto-completion for commands"""
        commands = [
            'ls', 'cd', 'pwd', 'mkdir', 'rm', 'rmdir', 'cp', 'mv', 'cat', 'echo',
            'ps', 'top', 'mem', 'cpu', 'df', 'du', 'find', 'grep',
            'history', 'clear', 'exit', 'help', 'ai'
        ]
        
        matches = [cmd for cmd in commands if cmd.startswith(text)]
        if state < len(matches):
            return matches[state]
        return None
    
    def execute_command(self, command: str) -> str:
        """Execute a command and return the output"""
        try:
            # Add to history
            if command.strip() and command not in self.command_history[-1:]:
                self.command_history.append(command)
                readline.add_history(command)
            
            # Handle command chaining with &&
            if ' && ' in command:
                commands = command.split(' && ')
                results = []
                for cmd in commands:
                    result = self.execute_command(cmd.strip())
                    results.append(result)
                    # If any command fails, stop execution
                    if "Error:" in result:
                        break
                return '\n'.join(results)
            
            # Parse command
            parts = command.strip().split()
            if not parts:
                return ""
            
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Handle built-in commands
            if cmd == 'cd':
                return self.cmd_cd(args)
            elif cmd == 'ls':
                return self.cmd_ls(args)
            elif cmd == 'pwd':
                return self.cmd_pwd()
            elif cmd == 'mkdir':
                return self.cmd_mkdir(args)
            elif cmd == 'rm':
                return self.cmd_rm(args)
            elif cmd == 'rmdir':
                return self.cmd_rmdir(args)
            elif cmd == 'cp':
                return self.cmd_cp(args)
            elif cmd == 'mv':
                return self.cmd_mv(args)
            elif cmd == 'cat':
                return self.cmd_cat(args)
            elif cmd == 'echo':
                return self.cmd_echo(args)
            elif cmd == 'ps':
                return self.cmd_ps(args)
            elif cmd == 'top':
                return self.cmd_top()
            elif cmd == 'mem':
                return self.cmd_mem()
            elif cmd == 'cpu':
                return self.cmd_cpu()
            elif cmd == 'df':
                return self.cmd_df()
            elif cmd == 'du':
                return self.cmd_du(args)
            elif cmd == 'find':
                return self.cmd_find(args)
            elif cmd == 'grep':
                return self.cmd_grep(args)
            elif cmd == 'history':
                return self.cmd_history()
            elif cmd == 'clear':
                return self.cmd_clear()
            elif cmd == 'help':
                return self.cmd_help()
            elif cmd == 'ai':
                return self.cmd_ai(args)
            elif cmd == 'exit':
                self.save_history()
                sys.exit(0)
            else:
                # Check if it's a natural language command (no traditional command found)
                if self.is_natural_language_command(command):
                    return self.process_natural_language(command)
                else:
                    # Try to execute as system command
                    return self.execute_system_command(command)
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_cd(self, args: List[str]) -> str:
        """Change directory command"""
        if not args:
            # Go to home directory
            new_dir = os.path.expanduser("~")
        else:
            new_dir = args[0]
        
        # Handle relative paths
        if not os.path.isabs(new_dir):
            new_dir = os.path.join(self.current_dir, new_dir)
        
        new_dir = os.path.abspath(new_dir)
        
        if os.path.isdir(new_dir):
            self.current_dir = new_dir
            os.chdir(new_dir)
            return f"Changed to: {self.current_dir}"
        else:
            return f"Error: Directory '{new_dir}' not found"
    
    def cmd_ls(self, args: List[str]) -> str:
        """List directory contents"""
        try:
            # Parse arguments
            show_hidden = '-a' in args or '--all' in args
            long_format = '-l' in args or '--long' in args
            human_readable = '-h' in args or '--human-readable' in args
            
            # Determine target directory
            target_dir = self.current_dir
            for arg in args:
                if not arg.startswith('-') and os.path.isdir(arg):
                    target_dir = arg
                    break
            
            items = []
            try:
                for item in os.listdir(target_dir):
                    if not show_hidden and item.startswith('.'):
                        continue
                    items.append(item)
            except PermissionError:
                return f"Error: Permission denied accessing '{target_dir}'"
            
            items.sort()
            
            if long_format:
                result = []
                for item in items:
                    item_path = os.path.join(target_dir, item)
                    try:
                        stat = os.stat(item_path)
                        size = stat.st_size
                        if human_readable:
                            size = self.format_size(size)
                        mode = 'd' if os.path.isdir(item_path) else '-'
                        result.append(f"{mode} {size:>8} {item}")
                    except OSError:
                        result.append(f"? {'?':>8} {item}")
                return '\n'.join(result)
            else:
                # Simple format - organize in columns
                if not items:
                    return "Directory is empty"
                
                # Calculate column width
                max_width = max(len(item) for item in items) + 2
                terminal_width = shutil.get_terminal_size().columns
                cols = max(1, terminal_width // max_width)
                
                result = []
                for i in range(0, len(items), cols):
                    row_items = items[i:i+cols]
                    row = ""
                    for item in row_items:
                        row += item.ljust(max_width)
                    result.append(row.rstrip())
                
                return '\n'.join(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_pwd(self) -> str:
        """Print working directory"""
        return self.current_dir
    
    def cmd_mkdir(self, args: List[str]) -> str:
        """Create directory"""
        if not args:
            return "Error: mkdir requires directory name"
        
        results = []
        for dir_name in args:
            try:
                os.makedirs(dir_name, exist_ok=True)
                results.append(f"Created directory: {dir_name}")
            except Exception as e:
                results.append(f"Error creating '{dir_name}': {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_rm(self, args: List[str]) -> str:
        """Remove files or directories"""
        if not args:
            return "Error: rm requires file or directory name"
        
        recursive = '-r' in args or '--recursive' in args
        force = '-f' in args or '--force' in args
        
        # Filter out flags
        targets = [arg for arg in args if not arg.startswith('-')]
        
        if not targets:
            return "Error: No files or directories specified"
        
        results = []
        for target in targets:
            try:
                if os.path.isdir(target):
                    if recursive:
                        shutil.rmtree(target)
                        results.append(f"Removed directory: {target}")
                    else:
                        results.append(f"Error: '{target}' is a directory (use -r for recursive)")
                elif os.path.isfile(target):
                    os.remove(target)
                    results.append(f"Removed file: {target}")
                else:
                    if not force:
                        results.append(f"Error: '{target}' not found")
            except Exception as e:
                results.append(f"Error removing '{target}': {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_rmdir(self, args: List[str]) -> str:
        """Remove empty directories"""
        if not args:
            return "Error: rmdir requires directory name"
        
        results = []
        for dir_name in args:
            try:
                if os.path.isdir(dir_name):
                    # Check if directory is empty
                    if not os.listdir(dir_name):
                        os.rmdir(dir_name)
                        results.append(f"Removed directory: {dir_name}")
                    else:
                        results.append(f"Error: Directory '{dir_name}' is not empty (use 'rm -r' to remove non-empty directories)")
                else:
                    results.append(f"Error: '{dir_name}' is not a directory")
            except Exception as e:
                results.append(f"Error removing directory '{dir_name}': {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_cp(self, args: List[str]) -> str:
        """Copy files or directories"""
        if len(args) < 2:
            return "Error: cp requires source and destination"
        
        recursive = '-r' in args or '--recursive' in args
        
        # Filter out flags
        filtered_args = [arg for arg in args if not arg.startswith('-')]
        if len(filtered_args) < 2:
            return "Error: cp requires source and destination"
        
        source = filtered_args[0]
        dest = filtered_args[1]
        
        try:
            if os.path.isdir(source):
                if recursive:
                    shutil.copytree(source, dest)
                    return f"Copied directory '{source}' to '{dest}'"
                else:
                    return "Error: Cannot copy directory without -r flag"
            else:
                shutil.copy2(source, dest)
                return f"Copied file '{source}' to '{dest}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_mv(self, args: List[str]) -> str:
        """Move or rename files or directories"""
        if len(args) < 2:
            return "Error: mv requires source and destination"
        
        source = args[0]
        dest = args[1]
        
        try:
            shutil.move(source, dest)
            return f"Moved '{source}' to '{dest}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_cat(self, args: List[str]) -> str:
        """Display file contents"""
        if not args:
            return "Error: cat requires filename"
        
        results = []
        for filename in args:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    results.append(f.read())
            except Exception as e:
                results.append(f"Error reading '{filename}': {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_echo(self, args: List[str]) -> str:
        """Echo text"""
        if not args:
            return ""
        
        # Handle redirection
        if '>>' in ' '.join(args):
            # Append mode
            parts = ' '.join(args).split('>>')
            if len(parts) == 2:
                text = parts[0].strip()
                filename = parts[1].strip()
                try:
                    with open(filename, 'a', encoding='utf-8') as f:
                        f.write(text + '\n')
                    return f"Appended to {filename}"
                except Exception as e:
                    return f"Error appending to {filename}: {str(e)}"
        elif '>' in args:
            # Write mode
            try:
                redirect_idx = args.index('>')
                text = ' '.join(args[:redirect_idx])
                filename = args[redirect_idx + 1]
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text + '\n')
                return f"Written to {filename}"
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return ' '.join(args)
    
    def cmd_ps(self, args: List[str]) -> str:
        """List running processes"""
        try:
            processes = []
            python_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    process_line = f"{pinfo['pid']:>6} {pinfo['name']:<20} {pinfo['cpu_percent']:>6.1f}% {pinfo['memory_percent']:>6.1f}%"
                    
                    # Prioritize Python processes
                    if 'python' in pinfo['name'].lower():
                        python_processes.append(process_line)
                    else:
                        processes.append(process_line)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Show Python processes first, then others
            all_processes = python_processes + processes
            
            if not all_processes:
                return "No processes found"
            
            header = f"{'PID':>6} {'NAME':<20} {'CPU%':>6} {'MEM%':>6}"
            return header + '\n' + '\n'.join(all_processes[:20])  # Show top 20 processes
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_top(self) -> str:
        """Show top processes by CPU usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 0:  # Only show processes using CPU
                        processes.append((pinfo['cpu_percent'], pinfo['pid'], pinfo['name'], pinfo['memory_percent']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(reverse=True)
            
            header = f"{'PID':>6} {'NAME':<20} {'CPU%':>6} {'MEM%':>6}"
            result = [header]
            for cpu, pid, name, mem in processes[:10]:  # Top 10
                result.append(f"{pid:>6} {name:<20} {cpu:>6.1f}% {mem:>6.1f}%")
            
            return '\n'.join(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_mem(self) -> str:
        """Show memory usage"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            result = [
                "Memory Usage:",
                f"  Total: {self.format_size(memory.total)}",
                f"  Available: {self.format_size(memory.available)}",
                f"  Used: {self.format_size(memory.used)} ({memory.percent:.1f}%)",
                f"  Free: {self.format_size(memory.free)}",
                "",
                "Swap Usage:",
                f"  Total: {self.format_size(swap.total)}",
                f"  Used: {self.format_size(swap.used)} ({swap.percent:.1f}%)",
                f"  Free: {self.format_size(swap.free)}"
            ]
            return '\n'.join(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_cpu(self) -> str:
        """Show CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            result = [
                f"CPU Usage: {cpu_percent:.1f}%",
                f"CPU Cores: {cpu_count}",
                f"CPU Frequency: {cpu_freq.current:.0f} MHz" if cpu_freq else "CPU Frequency: N/A"
            ]
            return '\n'.join(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_df(self) -> str:
        """Show disk usage"""
        try:
            result = ["Filesystem Usage:"]
            for partition in psutil.disk_partitions():
                try:
                    # Use shutil.disk_usage instead of psutil.disk_usage for Windows compatibility
                    import shutil
                    usage = shutil.disk_usage(partition.mountpoint)
                    device = partition.device.replace('\\', '/')
                    total = self.format_size(usage.total)
                    used = self.format_size(usage.used)
                    free = self.format_size(usage.free)
                    percent = str(round((usage.used / usage.total) * 100, 1)) + "%"
                    mountpoint = partition.mountpoint.replace('\\', '/')
                    
                    # Simple string concatenation
                    line = "  " + device.ljust(20) + " " + total.rjust(8) + " " + used.rjust(8) + " " + free.rjust(8) + " " + percent.rjust(5) + " " + mountpoint
                    result.append(line)
                except (PermissionError, OSError):
                    pass
            return '\n'.join(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_du(self, args: List[str]) -> str:
        """Show directory usage"""
        if not args:
            target = "."
        else:
            target = args[0]
        
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(target):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except OSError:
                        pass
            
            return f"Total size of '{target}': {self.format_size(total_size)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_find(self, args: List[str]) -> str:
        """Find files"""
        if not args:
            return "Error: find requires search pattern"
        
        pattern = args[0]
        directory = args[1] if len(args) > 1 else "."
        
        try:
            import glob
            matches = []
            
            # Handle glob patterns
            if '*' in pattern or '?' in pattern:
                search_pattern = os.path.join(directory, pattern)
                matches = glob.glob(search_pattern, recursive=True)
            else:
                # Simple string matching
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if pattern in file:
                            matches.append(os.path.join(root, file))
            
            return '\n'.join(matches) if matches else f"No files found matching '{pattern}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_grep(self, args: List[str]) -> str:
        """Search for text in files"""
        if len(args) < 2:
            return "Error: grep requires pattern and filename"
        
        pattern = args[0]
        filename = args[1]
        
        try:
            matches = []
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern in line:
                        matches.append(f"{filename}:{line_num}:{line.rstrip()}")
            
            return '\n'.join(matches) if matches else f"No matches found for '{pattern}' in '{filename}'"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def cmd_history(self) -> str:
        """Show command history"""
        if not self.command_history:
            return "No command history"
        
        result = []
        for i, cmd in enumerate(self.command_history[-20:], 1):  # Show last 20 commands
            result.append(f"{i:>3}  {cmd}")
        
        return '\n'.join(result)
    
    def cmd_clear(self) -> str:
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return ""
    
    def cmd_help(self) -> str:
        """Show help information"""
        help_text = """
Available Commands:
  File Operations:
    ls [options] [dir]     - List directory contents (-a: show hidden, -l: long format)
    cd [dir]               - Change directory
    pwd                    - Print working directory
    mkdir <dir>            - Create directory
    rm [options] <file>    - Remove file/directory (-r: recursive, -f: force)
    rmdir <dir>            - Remove empty directory
    cp [options] <src> <dest> - Copy file/directory (-r: recursive)
    mv <src> <dest>        - Move/rename file/directory
    cat <file>             - Display file contents
    echo <text>            - Echo text
    
  System Monitoring:
    ps                     - List running processes
    top                    - Show top processes by CPU usage
    mem                    - Show memory usage
    cpu                    - Show CPU usage
    df                     - Show disk usage
    du [dir]               - Show directory usage
    
  Search:
    find <pattern> [dir]   - Find files by name
    grep <pattern> <file>  - Search text in files
    
  Utilities:
    history                - Show command history
    clear                  - Clear screen
    help                   - Show this help
    exit                   - Exit terminal
    
  Natural Language Commands (no 'ai' prefix needed):
    create folder <name>   - Create a directory
    create file <name>     - Create a file
    move <file> to <folder> - Move file to folder
    copy <file> to <folder> - Copy file to folder
    show files             - List files
    show memory            - Display memory usage
    show processes         - List running processes
    show cpu               - Display CPU usage
    delete <file>          - Delete a file
    read <file>            - Read file contents
    what can you do        - Show available commands
        """
        return help_text.strip()
    
    def is_natural_language_command(self, command: str) -> bool:
        """Check if the command is a natural language command"""
        command_lower = command.lower()
        
        # Keywords that indicate natural language commands
        nlp_keywords = [
            'create', 'make', 'new', 'folder', 'directory', 'file',
            'move', 'copy', 'transfer', 'to', 'into', 'in',
            'list', 'show', 'display', 'see', 'files', 'contents',
            'delete', 'remove', 'rm',
            'read', 'open', 'view',
            'memory', 'ram', 'cpu', 'processor', 'processes', 'running',
            'disk', 'space', 'storage', 'help', 'what', 'can'
        ]
        
        # Check if command contains NLP keywords and doesn't start with a traditional command
        traditional_commands = ['ls', 'cd', 'pwd', 'mkdir', 'rm', 'cp', 'mv', 'cat', 'echo', 
                               'ps', 'top', 'mem', 'cpu', 'df', 'du', 'find', 'grep', 
                               'history', 'clear', 'help', 'exit', 'ai']
        
        first_word = command.split()[0].lower() if command.split() else ""
        
        # If it starts with a traditional command, it's not NLP
        if first_word in traditional_commands:
            return False
        
        # If it's a single word that's not a traditional command and not an NLP keyword, 
        # it's likely a system command, not NLP
        if len(command.split()) == 1 and first_word not in nlp_keywords:
            return False
        
        # If it contains NLP keywords, it's likely a natural language command
        return any(keyword in command_lower for keyword in nlp_keywords)
    
    def process_natural_language(self, command: str) -> str:
        """Process natural language commands directly"""
        return self.cmd_ai([command])
    
    def cmd_ai(self, args: List[str]) -> str:
        """AI-powered natural language command processing"""
        if not args:
            return "Error: AI command requires a query"
        
        query = ' '.join(args).lower()
        words = query.split()
        
        # Enhanced AI command processing with more patterns
        try:
            # CREATE operations
            if any(word in query for word in ['create', 'make', 'new']):
                if any(word in query for word in ['folder', 'directory', 'dir']):
                    # Extract folder name - look for words after 'folder', 'directory', 'dir'
                    folder_name = None
                    for i, word in enumerate(words):
                        if word in ['folder', 'directory', 'dir'] and i + 1 < len(words):
                            folder_name = words[i + 1]
                            break
                    
                    if folder_name:
                        return self.cmd_mkdir([folder_name])
                    else:
                        return "AI: Please specify a folder name. Example: 'ai create folder my_folder'"
                
                elif any(word in query for word in ['file']):
                    # Extract file name and content
                    file_name = None
                    content = "New file created by AI"
                    
                    for i, word in enumerate(words):
                        if word == 'file' and i + 1 < len(words):
                            file_name = words[i + 1]
                            # Look for content after 'with' or 'containing'
                            if i + 2 < len(words) and words[i + 2] in ['with', 'containing']:
                                content = ' '.join(words[i + 3:]) if len(words) > i + 3 else content
                            break
                    
                    if file_name:
                        try:
                            with open(file_name, 'w') as f:
                                f.write(content)
                            return f"AI: Created file '{file_name}' with content: {content}"
                        except Exception as e:
                            return f"AI: Error creating file: {str(e)}"
                    else:
                        return "AI: Please specify a file name. Example: 'ai create file test.txt with hello world'"
            
            # MOVE/COPY operations
            elif any(word in query for word in ['move', 'copy', 'transfer']):
                file_name = None
                dest_name = None
                
                # Find file name
                for i, word in enumerate(words):
                    if word in ['file'] and i + 1 < len(words):
                        file_name = words[i + 1]
                        break
                    elif word.endswith('.txt') or word.endswith('.py') or word.endswith('.md'):
                        file_name = word
                        break
                
                # Find destination
                for i, word in enumerate(words):
                    if word in ['to', 'into', 'in'] and i + 1 < len(words):
                        dest_name = words[i + 1]
                        break
                
                if file_name and dest_name:
                    if 'move' in query:
                        return self.cmd_mv([file_name, dest_name])
                    else:
                        return self.cmd_cp([file_name, dest_name])
                else:
                    return "AI: Please specify file and destination. Example: 'ai move file.txt to folder'"
            
            # LIST/SHOW operations
            elif any(word in query for word in ['list', 'show', 'display', 'see']):
                if any(word in query for word in ['files', 'file', 'directory', 'folder', 'contents']):
                    return self.cmd_ls([])
                elif any(word in query for word in ['memory', 'ram']):
                    return self.cmd_mem()
                elif any(word in query for word in ['cpu', 'processor']):
                    return self.cmd_cpu()
                elif any(word in query for word in ['processes', 'process', 'running', 'programs']):
                    return self.cmd_ps([])
                elif any(word in query for word in ['disk', 'space', 'storage']):
                    return self.cmd_df()
                else:
                    return self.cmd_ls([])  # Default to listing files
            
            # DELETE operations
            elif any(word in query for word in ['delete', 'remove', 'rm']):
                target = None
                for word in words:
                    if word.endswith('.txt') or word.endswith('.py') or word.endswith('.md') or word.endswith('.json'):
                        target = word
                        break
                    elif word not in ['delete', 'remove', 'rm', 'the', 'a', 'an']:
                        target = word
                        break
                
                if target:
                    return self.cmd_rm([target])
                else:
                    return "AI: Please specify what to delete. Example: 'ai delete file.txt'"
            
            # READ operations
            elif any(word in query for word in ['read', 'open', 'view', 'display']):
                file_name = None
                for word in words:
                    if word.endswith('.txt') or word.endswith('.py') or word.endswith('.md') or word.endswith('.json'):
                        file_name = word
                        break
                
                if file_name:
                    return self.cmd_cat([file_name])
                else:
                    return "AI: Please specify a file to read. Example: 'ai read file.txt'"
            
            # SYSTEM INFO
            elif any(word in query for word in ['memory', 'ram']):
                return self.cmd_mem()
            elif any(word in query for word in ['cpu', 'processor']):
                return self.cmd_cpu()
            elif any(word in query for word in ['processes', 'process', 'running']):
                return self.cmd_ps([])
            elif any(word in query for word in ['disk', 'space', 'storage']):
                return self.cmd_df()
            
            # HELP
            elif any(word in query for word in ['help', 'commands', 'what', 'can']):
                return self.cmd_help()
            
            else:
                # Try to provide helpful suggestions
                suggestions = []
                if 'create' in query:
                    suggestions.append("'ai create folder <name>' or 'ai create file <name>'")
                if 'move' in query or 'copy' in query:
                    suggestions.append("'ai move <file> to <folder>' or 'ai copy <file> to <folder>'")
                if 'show' in query or 'list' in query:
                    suggestions.append("'ai show files', 'ai show memory', 'ai show processes'")
                if 'delete' in query:
                    suggestions.append("'ai delete <file>'")
                
                suggestion_text = " Try: " + ", ".join(suggestions) if suggestions else ""
                return f"AI: I don't understand '{query}'.{suggestion_text} Available commands: create, move, copy, show, delete, read, and system info."
        
        except Exception as e:
            return f"AI: Error processing command: {str(e)}"
    
    def execute_system_command(self, command: str) -> str:
        """Execute system command using subprocess"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nError: {result.stderr}"
            
            return output if output else "Command executed successfully"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def run(self):
        """Main terminal loop"""
        print("Advanced Python Terminal")
        print("Type 'help' for available commands or 'exit' to quit")
        print("=" * 50)
        
        while True:
            try:
                # Get user input with current directory prompt
                prompt = f"{os.path.basename(self.current_dir)}> "
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                # Execute command
                output = self.execute_command(command)
                
                if output:
                    print(output)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Advanced Python Terminal')
    parser.add_argument('--web', action='store_true', help='Start web interface')
    args = parser.parse_args()
    
    if args.web:
        # Start web interface
        import web_interface
        port = int(os.environ.get('PORT', 5000))
        web_interface.app.run(debug=False, host='0.0.0.0', port=port)
    else:
        # Start CLI interface
        terminal = Terminal()
        terminal.run()

if __name__ == "__main__":
    main()
