#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Lifecycle Manager
Manages Ollama daemon startup/shutdown based on configuration
"""

import subprocess
import sys
import os
import time
import signal
from typing import Optional

class OllamaManager:
    """Manages Ollama daemon lifecycle"""

    def __init__(self, config_dir: str = None):
        """Initialize Ollama manager"""
        self.config_dir = config_dir or os.path.expanduser("~/.aichat")
        self.pid_file = os.path.join(self.config_dir, "ollama.pid")
        self.always_on = self._get_config_option("OLLAMA_ALWAYS_ON", "false") == "true"

    def _get_config_option(self, key: str, default: str = "") -> str:
        """Read config option from config file"""
        config_file = os.path.join(self.config_dir, "config")
        if not os.path.exists(config_file):
            return default

        try:
            with open(config_file, 'r') as f:
                for line in f:
                    if line.startswith(f"{key}="):
                        value = line.split('=', 1)[1].strip().strip('"')
                        return value
        except Exception:
            pass

        return default

    def is_ollama_running(self) -> bool:
        """
        Check if Ollama daemon is running

        Returns:
            True if Ollama is running and responding
        """
        try:
            # Try to list models - if this works, Ollama is running
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def start_ollama(self) -> bool:
        """
        Start Ollama daemon in background

        Returns:
            True if Ollama started successfully or was already running
        """
        # If always-on mode, don't manage Ollama
        if self.always_on:
            print("⚙️  Ollama always-on mode - not managing lifecycle", file=sys.stderr)
            return self.is_ollama_running()

        # Check if already running
        if self.is_ollama_running():
            print("✓ Ollama already running", file=sys.stderr)
            return True

        # Check if ollama command exists
        try:
            subprocess.run(['which', 'ollama'], capture_output=True, check=True, timeout=2)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print("❌ Ollama not installed! Install from: https://ollama.ai/download", file=sys.stderr)
            return False

        try:
            print("🚀 Starting Ollama daemon...", file=sys.stderr)

            # Start Ollama in background with stderr redirected to /dev/null
            process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent process
            )

            # Save PID for later shutdown
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))

            # Wait for Ollama to be ready (max 5 seconds)
            for i in range(10):
                time.sleep(0.5)
                if self.is_ollama_running():
                    print("✅ Ollama started successfully", file=sys.stderr)
                    return True

            print("⚠️  Ollama started but not responding yet", file=sys.stderr)
            return False

        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}", file=sys.stderr)
            return False

    def stop_ollama(self) -> bool:
        """
        Stop Ollama daemon gracefully

        Returns:
            True if Ollama stopped successfully
        """
        # If always-on mode, don't stop Ollama
        if self.always_on:
            print("⚙️  Ollama always-on mode - not stopping", file=sys.stderr)
            return True

        # Check if we have a PID file
        if not os.path.exists(self.pid_file):
            # No PID file - Ollama might not be running or wasn't started by us
            if not self.is_ollama_running():
                return True  # Already stopped

            # Running but not started by us - don't stop it
            print("⚠️  Ollama running but not managed by us - not stopping", file=sys.stderr)
            return True

        try:
            # Read PID
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Send SIGTERM for graceful shutdown
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"🛑 Stopping Ollama (PID {pid})...", file=sys.stderr)

                # Wait for process to terminate (max 5 seconds)
                for i in range(10):
                    time.sleep(0.5)
                    try:
                        # Check if process still exists
                        os.kill(pid, 0)
                    except OSError:
                        # Process terminated
                        print("✅ Ollama stopped successfully", file=sys.stderr)
                        os.remove(self.pid_file)
                        return True

                # Still running - force kill
                print("⚠️  Forcing Ollama shutdown...", file=sys.stderr)
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)

            except ProcessLookupError:
                # Process already dead
                pass

            # Clean up PID file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)

            return True

        except Exception as e:
            print(f"⚠️  Error stopping Ollama: {e}", file=sys.stderr)
            # Clean up PID file anyway
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            return False

    def ensure_ollama_running(self) -> bool:
        """
        Ensure Ollama is running, start if needed

        Returns:
            True if Ollama is running after this call
        """
        if self.is_ollama_running():
            return True

        return self.start_ollama()


# CLI interface for testing
if __name__ == '__main__':
    manager = OllamaManager()

    if len(sys.argv) < 2:
        print("Usage: ollama_manager.py [start|stop|status|ensure]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        success = manager.start_ollama()
        sys.exit(0 if success else 1)

    elif command == "stop":
        success = manager.stop_ollama()
        sys.exit(0 if success else 1)

    elif command == "status":
        running = manager.is_ollama_running()
        print(f"Ollama: {'running' if running else 'stopped'}")
        print(f"Always-on mode: {'enabled' if manager.always_on else 'disabled'}")
        sys.exit(0 if running else 1)

    elif command == "ensure":
        success = manager.ensure_ollama_running()
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
