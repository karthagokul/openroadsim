#
# MIT License
# Copyright (c) 2024 Gokul Kartha <kartha.gokul@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import socket
import json
import threading

HOST = '0.0.0.0'
PORT = 9000

def handle_connection(conn, addr):
    print(f"Connection from {addr}")
    with conn:
        try:
            buffer = ""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    print(f"Client {addr} disconnected.")
                    break

                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    try:
                        data = json.loads(line)
                        print(f"Received from {addr}:\n{json.dumps(data, indent=2)}")
                        conn.sendall(b"ACK\n")
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from {addr}: {line}")
        except (ConnectionResetError, BrokenPipeError):
            print(f"Connection reset by {addr}")
        except Exception as e:
            print(f"Server error with {addr}: {e}")

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Mock Firmware Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_connection, args=(conn, addr), daemon=True)
            thread.start()
            print(f"Spawned handler thread for {addr}")

if __name__ == "__main__":
    run_server()
