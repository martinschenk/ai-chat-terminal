#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chat Daemon Server
Keeps ChatSystem loaded in RAM and serves requests via socket
Dramatically reduces response time by avoiding Python restart overhead
"""

import socket
import json
import sys
import os
import threading
import time
import signal
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_system import ChatSystem

class ChatDaemon:
    """Socket-based daemon server for ChatSystem"""

    def __init__(self, host='127.0.0.1', port=5555):
        """Initialize daemon server"""
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.last_request_time = time.time()
        self.idle_timeout = 600  # 10 minutes in seconds

        # Load ChatSystem ONCE - this is the whole point!
        print("🔄 Loading ChatSystem into RAM...", file=sys.stderr)
        start_time = time.time()
        self.chat_system = ChatSystem()
        load_time = (time.time() - start_time) * 1000
        print(f"✅ ChatSystem loaded in {load_time:.0f}ms", file=sys.stderr)

    def start(self):
        """Start the daemon server"""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)  # Allow periodic timeout checks

            self.running = True
            print(f"🚀 Chat daemon listening on {self.host}:{self.port}", file=sys.stderr)

            # Start idle timeout monitor in background
            timeout_thread = threading.Thread(target=self._monitor_idle_timeout, daemon=True)
            timeout_thread.start()

            # Main server loop
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    self.last_request_time = time.time()

                    # Handle request in separate thread for concurrency
                    thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket,),
                        daemon=True
                    )
                    thread.start()

                except socket.timeout:
                    # Normal timeout - just continue loop
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️  Error accepting connection: {e}", file=sys.stderr)

        except Exception as e:
            print(f"❌ Failed to start daemon: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            self.cleanup()

    def _monitor_idle_timeout(self):
        """Monitor idle time and shutdown if exceeded"""
        while self.running:
            time.sleep(10)  # Check every 10 seconds

            idle_time = time.time() - self.last_request_time
            if idle_time > self.idle_timeout:
                print(f"\n⏰ Idle timeout ({self.idle_timeout}s) exceeded - shutting down", file=sys.stderr)
                self.running = False
                break

    def _handle_client(self, client_socket):
        """Handle a single client request"""
        try:
            # Receive request data
            data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'\n\n' in data:  # End marker
                    break

            if not data:
                return

            # Parse JSON request
            try:
                request = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError as e:
                error_response = {
                    'success': False,
                    'error': f'Invalid JSON: {e}'
                }
                client_socket.sendall(json.dumps(error_response).encode('utf-8'))
                return

            # Validate request
            if 'action' not in request:
                error_response = {
                    'success': False,
                    'error': 'Missing "action" field'
                }
                client_socket.sendall(json.dumps(error_response).encode('utf-8'))
                return

            # Process request
            response = self._process_request(request)

            # Send response
            response_json = json.dumps(response) + '\n'
            client_socket.sendall(response_json.encode('utf-8'))

        except Exception as e:
            error_response = {
                'success': False,
                'error': f'Server error: {e}'
            }
            try:
                client_socket.sendall(json.dumps(error_response).encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()

    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a client request

        Request format:
        {
            "action": "send_message",
            "session_id": "chat_session",
            "message": "user input",
            "system_prompt": "optional"
        }

        Response format:
        {
            "success": true/false,
            "response": "AI response",
            "error": "error message if failed"
        }
        """
        action = request['action']

        if action == 'send_message':
            try:
                session_id = request.get('session_id', 'default_session')
                message = request.get('message', '')
                system_prompt = request.get('system_prompt', '')

                if not message:
                    return {
                        'success': False,
                        'error': 'Empty message'
                    }

                # Call ChatSystem (already loaded in RAM!)
                # Returns: Tuple[str, Dict] = (response_text, metadata)
                response_text, metadata = self.chat_system.send_message(
                    session_id=session_id,
                    user_input=message,
                    system_prompt=system_prompt
                )

                return {
                    'success': True,
                    'response': response_text,
                    'metadata': metadata
                }

            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }

        elif action == 'ping':
            # Health check
            return {
                'success': True,
                'response': 'pong'
            }

        elif action == 'shutdown':
            # Graceful shutdown request
            print("🛑 Shutdown requested by client", file=sys.stderr)
            threading.Thread(target=self._delayed_shutdown, daemon=True).start()
            return {
                'success': True,
                'response': 'Shutting down...'
            }

        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}'
            }

    def _delayed_shutdown(self):
        """Shutdown after a short delay to allow response to be sent"""
        time.sleep(0.5)
        self.running = False

    def cleanup(self):
        """Clean up resources"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("👋 Chat daemon stopped", file=sys.stderr)

    def handle_signal(self, signum, frame):
        """Handle termination signals"""
        print(f"\n⚠️  Received signal {signum} - shutting down", file=sys.stderr)
        self.running = False


def main():
    """Main entry point"""
    # Parse command line args
    port = 5555
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)

    # Create and start daemon
    daemon = ChatDaemon(port=port)

    # Register signal handlers
    signal.signal(signal.SIGTERM, daemon.handle_signal)
    signal.signal(signal.SIGINT, daemon.handle_signal)

    # Start server (blocks until shutdown)
    daemon.start()


if __name__ == '__main__':
    main()
