#!/bin/bash
# KDC Setup Script — MIT Kerberos for LAB.LOCAL
# Run on KDC VM (192.168.88.20): sudo bash setup.sh

set -e
REALM="LAB.LOCAL"
KDC_IP="192.168.88.20"

echo "[*] Installing MIT Kerberos KDC..."
apt update -qq
apt install -y krb5-kdc krb5-admin-server krb5-config

echo "[*] Copying krb5.conf..."
cp krb5.conf /etc/krb5.conf

echo "[*] Creating realm $REALM..."
kdb5_util create -s -r $REALM -P "changeme123"

echo "[*] Starting KDC services..."
systemctl enable krb5-kdc krb5-admin-server
systemctl start krb5-kdc krb5-admin-server

echo "[*] Adding principals..."
kadmin.local -q "addprinc -pw Password123! admin@$REALM"
kadmin.local -q "addprinc -pw Password123! -requires_preauth user1@$REALM"
# Vulnerable account for AS-REP roasting demo
kadmin.local -q "addprinc -e aes256-cts-hmac-sha1-96:normal -pw Welcome1 vulnerable@$REALM"
kadmin.local -q "modprinc -requires_preauth admin@$REALM"
kadmin.local -q "modprinc +requires_preauth user1@$REALM"
kadmin.local -q "modprinc -requires_preauth vulnerable@$REALM"

# Service principals
kadmin.local -q "addprinc -pw Password123! host/client1.lab.local@$REALM"
kadmin.local -q "addprinc -pw Password123! host/client2.lab.local@$REALM"
kadmin.local -q "addprinc -pw Password123! http/web.lab.local@$REALM"
kadmin.local -q "addprinc -pw Password123! postgres/db.lab.local@$REALM"

echo "[+] KDC setup complete! Test: kinit admin@$REALM"
