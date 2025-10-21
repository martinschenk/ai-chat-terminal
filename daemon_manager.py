#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daemon Manager
Manages both Chat and Ollama daemon lifecycle
"""

import subprocess
import sys
import os
import time
import socket
import signal
import json
from typing import Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ollama_manager import OllamaManager

class DaemonManager:
    """Manages Chat and Ollama daemons together"""

    def __init__(self, config_dir: str = None):
        """Initialize daemon manager"""
        self.config_dir = config_dir or os.path.expanduser("~/.aichat")
        self.chat_pid_file = os.path.join(self.config_dir, "chat_daemon.pid")
        self.chat_port = 5555
        self.script_dir = config_dir or os.path.expanduser("~/.aichat")

        # Ollama manager
        self.ollama_manager = OllamaManager(config_dir=self.config_dir)

    def is_chat_daemon_running(self) -> bool:
        """
        Check if chat daemon is running

        Returns:
            True if chat daemon is running and responding
        """
        try:
            # Try to connect to the socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect(('127.0.0.1', self.chat_port))

            # Send ping request
            request = {
                'action': 'ping'
            }
            sock.sendall(json.dumps(request).encode('utf-8') + b'\n\n')

            # Receive response
            response = sock.recv(4096).decode('utf-8').strip()
            sock.close()

            # Parse response
            response_data = json.loads(response)
            return response_data.get('success', False)

        except (socket.error, socket.timeout, Exception):
            return False

    def start_daemons(self, show_loading: bool = True) -> bool:
        """
        Start both Chat and Ollama daemons

        Args:
            show_loading: Show loading indicator

        Returns:
            True if both daemons started successfully
        """
        if show_loading:
            print("🚀 Starting AI Chat Terminal daemons...", file=sys.stderr)

        # Step 1: Start Ollama (if managed mode)
        if not self.ollama_manager.ensure_ollama_running():
            print("❌ Failed to start Ollama daemon", file=sys.stderr)
            return False

        # Step 2: Check if chat daemon already running
        if self.is_chat_daemon_running():
            if show_loading:
                print("✓ Chat daemon already running", file=sys.stderr)
            return True

        # Step 3: Start chat daemon
        try:
            if show_loading:
                print("🔄 Loading chat system...", file=sys.stderr)

            # Find chat_daemon.py
            daemon_script = os.path.join(self.script_dir, "chat_daemon.py")
            if not os.path.exists(daemon_script):
                print(f"❌ Chat daemon script not found: {daemon_script}", file=sys.stderr)
                return False

            # Start daemon in background
            process = subprocess.Popen(
                ['python3', daemon_script, str(self.chat_port)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Save PID
            with open(self.chat_pid_file, 'w') as f:
                f.write(str(process.pid))

            # Wait for daemon to be ready (max 10 seconds)
            for i in range(20):
                time.sleep(0.5)
                if self.is_chat_daemon_running():
                    if show_loading:
                        print("✅ Chat daemon started successfully", file=sys.stderr)
                    return True

            print("⚠️  Chat daemon started but not responding", file=sys.stderr)
            return False

        except Exception as e:
            print(f"❌ Failed to start chat daemon: {e}", file=sys.stderr)
            return False

    def stop_daemons(self, graceful: bool = True) -> bool:
        """
        Stop both Chat and Ollama daemons

        Args:
            graceful: Try graceful shutdown first

        Returns:
            True if daemons stopped successfully
        """
        success = True

        # Step 1: Stop chat daemon
        if graceful and self.is_chat_daemon_running():
            try:
                # Send shutdown request
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect(('127.0.0.1', self.chat_port))

                import json
                request = {
                    'action': 'shutdown'
                }
                sock.sendall(json.dumps(request).encode('utf-8') + b'\n\n')
                sock.recv(4096)  # Wait for response
                sock.close()

                print("🛑 Chat daemon shutdown requested", file=sys.stderr)

                # Wait for shutdown (max 3 seconds)
                for i in range(6):
                    time.sleep(0.5)
                    if not self.is_chat_daemon_running():
                        break

            except Exception as e:
                print(f"⚠️  Graceful shutdown failed: {e}", file=sys.stderr)

        # Force kill if still running
        if os.path.exists(self.chat_pid_file):
            try:
                with open(self.chat_pid_file, 'r') as f:
                    pid = int(f.read().strip())

                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.5)

                    # Check if still alive
                    try:
                        os.kill(pid, 0)
                        # Still alive - force kill
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass  # Process dead

                except ProcessLookupError:
                    pass  # Already dead

                os.remove(self.chat_pid_file)

            except Exception as e:
                print(f"⚠️  Error stopping chat daemon: {e}", file=sys.stderr)
                success = False

        # Step 2: Stop Ollama (if managed mode)
        if not self.ollama_manager.stop_ollama():
            success = False

        if success:
            print("✅ Daemons stopped successfully", file=sys.stderr)

        return success

    def cleanup_chat_history(self) -> bool:
        """
        Request chat daemon to delete chat history (v11.6.0 - Privacy First!)

        WHY: User exits chat → history should be deleted
        REASON: Privacy by default - no persistent conversations

        Returns:
            True if cleanup successful
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect(('127.0.0.1', self.chat_port))

            request = {
                'action': 'cleanup_history'
            }
            sock.sendall(json.dumps(request).encode('utf-8') + b'\n\n')

            response = sock.recv(4096).decode('utf-8').strip()
            sock.close()

            response_data = json.loads(response)
            return response_data.get('success', False)

        except Exception as e:
            # Daemon might not be running - that's OK
            return False

    def ensure_daemons_running(self) -> bool:
        """
        Ensure both daemons are running, start if needed

        Returns:
            True if both daemons are running
        """
        if self.is_chat_daemon_running() and self.ollama_manager.is_ollama_running():
            return True

        return self.start_daemons(show_loading=False)

    def send_message(self, session_id: str, message: str, system_prompt: str = "") -> Optional[str]:
        """
        Send message to chat daemon

        Args:
            session_id: Chat session ID
            message: User message
            system_prompt: Optional system prompt

        Returns:
            AI response or None if failed
        """
        # Ensure daemons running
        if not self.ensure_daemons_running():
            return None

        try:
            # Connect to chat daemon
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(60.0)  # 60 second timeout for AI response
            sock.connect(('127.0.0.1', self.chat_port))

            # Send request
            import json
            request = {
                'action': 'send_message',
                'session_id': session_id,
                'message': message,
                'system_prompt': system_prompt
            }
            sock.sendall(json.dumps(request).encode('utf-8') + b'\n\n')

            # Receive response
            response_data = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b'\n' in response_data:
                    break

            sock.close()

            # Parse response
            response = json.loads(response_data.decode('utf-8'))

            if response.get('success'):
                return response.get('response', '')
            else:
                print(f"❌ Chat daemon error: {response.get('error')}", file=sys.stderr)
                return None

        except socket.timeout:
            print("⚠️  Chat daemon timeout - response took too long", file=sys.stderr)
            return None
        except Exception as e:
            print(f"❌ Failed to communicate with chat daemon: {e}", file=sys.stderr)
            return None


# CLI interface
if __name__ == '__main__':
    import json

    manager = DaemonManager()

    if len(sys.argv) < 2:
        print("Usage: daemon_manager.py [start|stop|status|ensure|message]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        success = manager.start_daemons()
        sys.exit(0 if success else 1)

    elif command == "stop":
        success = manager.stop_daemons()
        sys.exit(0 if success else 1)

    elif command == "status":
        chat_running = manager.is_chat_daemon_running()
        ollama_running = manager.ollama_manager.is_ollama_running()

        print(f"Chat daemon: {'running' if chat_running else 'stopped'}")
        print(f"Ollama daemon: {'running' if ollama_running else 'stopped'}")
        print(f"Ollama mode: {'always-on' if manager.ollama_manager.always_on else 'managed'}")

        sys.exit(0 if (chat_running and ollama_running) else 1)

    elif command == "ensure":
        success = manager.ensure_daemons_running()
        sys.exit(0 if success else 1)

    elif command == "message":
        if len(sys.argv) < 4:
            print("Usage: daemon_manager.py message <session_id> <message>")
            sys.exit(1)

        session_id = sys.argv[2]
        message = sys.argv[3]
        system_prompt = sys.argv[4] if len(sys.argv) > 4 else ""

        response = manager.send_message(session_id, message, system_prompt)
        if response:
            print(response)
            sys.exit(0)
        else:
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
