# Kerberos Attack Detection Signatures

## 1. Brute Force
**Pattern:** Multiple AS-REQ with KDC_ERR_PREAUTH_FAILED (error 24) from same source.
- Threshold: > 10 failures in 5 min → 90% confidence
- Filter: `ip.src == ATTACKER and kerberos.error_code == 24`

## 2. AS-REP Roasting
**Pattern:** AS-REQ without PA-DATA (no pre-authentication).
- Any AS-REQ without padata → 70% confidence
- Multiple usernames in < 3s → 85% confidence

## 3. Kerberoasting
**Pattern:** Rapid TGS-REQ for multiple different service SPNs.
- > 5 services in 60s → 80% confidence

## 4. Golden Ticket
**Pattern:** TGS-REQ without corresponding prior AS-REQ.
- Any occurrence → 60% confidence
- Ticket lifetime > 10 years → 95% confidence

## 5. Pass-the-Ticket
**Pattern:** Ticket used from different IP than issuance.
- IP mismatch → 75% confidence

## 6. Lateral Movement
**Pattern:** Sequential auth to 3+ hosts in 10 min.
- > 3 hosts in 10 min → 85% confidence
