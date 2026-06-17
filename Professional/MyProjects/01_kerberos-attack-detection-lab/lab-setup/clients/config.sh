#!/bin/bash
# Client VM Setup Script — run on Client VMs (.30, .31)
# Usage: sudo bash config.sh

set -e
echo "[*] Installing Kerberos client..."
apt update -qq
apt install -y krb5-user libpam-krb5 ssh

cat > /etc/krb5.conf << 'KRBEOF'
[libdefaults]
    default_realm = LAB.LOCAL
    clockskew = 300
[realms]
    LAB.LOCAL = {
        kdc = 192.168.88.20
        admin_server = 192.168.88.20
    }
[domain_realm]
    .lab.local = LAB.LOCAL
KRBEOF

echo "[*] Enabling SSH GSSAPI..."
echo "GSSAPIAuthentication yes" >> /etc/ssh/sshd_config
echo "GSSAPICleanupCredentials yes" >> /etc/ssh/sshd_config
service ssh restart

echo "[+] Done. Test: kinit admin@LAB.LOCAL"
