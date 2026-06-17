# Wireshark: The 80/20 Guide for Kerberos Analysis
## Master the 20% That Gives You 80% of the Value

**Author:** Emerson  
**Focus:** Analyzing Kerberos attacks for security research  
**Time to Competence:** 45 minutes  

---

## 🎯 Core Concept

**Wireshark** analyzes packet captures. For your Kerberos project, you need to:
1. Open pcap files from tcpdump
2. Find attack patterns
3. Extract evidence
4. Create screenshots for portfolio

**That's it. Everything else is bonus.**

---

## 🚀 Quick Start: Open Your First Capture

### Step 1: Launch Wireshark

```bash
wireshark bruteforce_attack.pcap &
```

**What you see:**
- Packet list (top) - every packet
- Packet details (middle) - decoded structure
- Packet bytes (bottom) - raw data

---

### Step 2: Apply Kerberos Filter

**In the filter bar, type:**
```
kerberos
```

**Press Enter.**

**Result:** Only Kerberos packets shown

---

## 🎓 The 5 Essential Filters

These cover 95% of Kerberos attack analysis:

### Filter 1: Show All Kerberos
```
kerberos
```

### Filter 2: Show Failed Authentications
```
kerberos.error_code == 24
```
**24 = KDC_ERR_PREAUTH_FAILED (wrong password)**

### Filter 3: Show Successful Authentications
```
kerberos.msg_type == 11 && !kerberos.error_code
```
**11 = AS-REP (authentication response) without error**

### Filter 4: Show AS-REQ (initial auth)
```
kerberos.msg_type == 10
```

### Filter 5: Show TGS-REQ (service tickets)
```
kerberos.msg_type == 12
```

---

## 📊 Analyzing Your Attack Captures

### Attack 1: Brute Force Analysis

**Open your brute force capture:**
```bash
wireshark bruteforce_capture.pcap
```

**Step 1: Apply error filter:**
```
kerberos.error_code == 24
```

**What to look for:**
- Multiple packets from same IP
- Same username (cname)
- Regular timing pattern

**Step 2: Count failed attempts:**
- Statistics > Protocol Hierarchy
- Look at "Kerberos" line
- Note packet count

**Step 3: Find source IP:**
```
kerberos.error_code == 24
```
- Right-click any packet
- Follow > TCP Stream
- Note source IP in top

**Step 4: Check if attack succeeded:**
```
kerberos.msg_type == 11 && !kerberos.error_code && ip.src == 192.168.88.10
```
Replace with actual attacker IP

**Evidence to capture:**
- Screenshot of repeated failures
- Statistics showing count
- Timeline of attack
- Successful auth (if any)

---

### Attack 2: AS-REP Roasting Analysis

**Open your AS-REP roasting capture:**
```bash
wireshark asrep_roasting.pcap
```

**Step 1: Find AS-REP without pre-auth:**
```
kerberos.msg_type == 11
```

**Step 2: Look for multiple different usernames:**
- Click on packets
- Expand: Kerberos > as-rep > cname
- Note different usernames being tested

**Step 3: Find successful roasts:**
- Look for AS-REP responses (msg_type 11)
- These contain encrypted hashes
- Without error codes = roastable account found

**Evidence to capture:**
- Multiple AS-REP responses
- Different usernames tested
- Hash in encrypted portion (expand enc-part)

**Key indicator:**
```
kerberos.msg_type == 11 && !kerberos.pa_data
```
**AS-REP without pre-auth data = VULNERABLE**

---

### Attack 3: Kerberoasting Analysis

**Open your Kerberoasting capture:**
```bash
wireshark kerberoasting.pcap
```

**Step 1: Show service ticket requests:**
```
kerberos.msg_type == 12
```

**Step 2: Count unique services:**
- Statistics > Conversations
- TCP tab
- Note multiple connections

**Step 3: Extract service names:**
- Filter: `kerberos.msg_type == 12`
- Expand: Kerberos > tgs-req > sname
- Note each service being requested

**Evidence to capture:**
- Multiple TGS-REQ packets
- Different service names
- Same source IP
- Short time window

**Attack signature:**
```
kerberos.msg_type == 12
```
Look for 10+ requests in short time from one IP

---

## 🔍 Essential Analysis Techniques

### Technique 1: Follow TCP Stream

**Purpose:** See entire conversation

**How:**
1. Right-click any packet
2. Follow > TCP Stream
3. See full exchange

**Use case:** Understand attack sequence

---

### Technique 2: Statistics > Conversations

**Purpose:** Find high-traffic sources

**How:**
1. Statistics > Conversations
2. TCP tab
3. Sort by "Packets" column

**Use case:** Identify attacker IP quickly

---

### Technique 3: Time Analysis

**Purpose:** Calculate attack rate

**How:**
1. View > Time Display Format > Seconds Since Previous Packet
2. Look at time between packets

**Use case:** Measure brute force speed

---

### Technique 4: Expert Information

**Purpose:** Find problems automatically

**How:**
1. Analyze > Expert Information
2. Look for warnings/errors

**Use case:** Quick anomaly detection

---

### Technique 5: Protocol Hierarchy

**Purpose:** Understand traffic composition

**How:**
1. Statistics > Protocol Hierarchy
2. See breakdown of protocols

**Use case:** Verify capture contains expected traffic

---

## 📋 Wireshark Display Filters Cheat Sheet

### Kerberos Message Types
```
kerberos.msg_type == 10    # AS-REQ (initial authentication request)
kerberos.msg_type == 11    # AS-REP (authentication response)
kerberos.msg_type == 12    # TGS-REQ (service ticket request)
kerberos.msg_type == 13    # TGS-REP (service ticket response)
kerberos.msg_type == 30    # KRB-ERROR (error message)
```

### Error Codes
```
kerberos.error_code == 6   # Client unknown (user doesn't exist)
kerberos.error_code == 24  # Pre-auth failed (wrong password)
kerberos.error_code == 25  # Pre-auth required (checking if needed)
```

### Specific Users
```
kerberos.cname contains "admin"     # Client name contains "admin"
kerberos.sname contains "http"      # Service name contains "http"
```

### Combinations
```
# Failed brute force attempts
kerberos.error_code == 24 && kerberos.cname contains "admin"

# Successful authentication
kerberos.msg_type == 11 && !kerberos.error_code

# Service ticket requests for HTTP
kerberos.msg_type == 12 && kerberos.sname contains "http"

# From specific IP
kerberos && ip.src == 192.168.88.10

# To specific IP (KDC)
kerberos && ip.dst == 192.168.88.20
```

---

## 🎨 Creating Portfolio Screenshots

### Screenshot 1: Attack Overview

**Purpose:** Show scale of attack

**Setup:**
1. Apply filter: `kerberos.error_code == 24`
2. Statistics > Protocol Hierarchy
3. Screenshot showing packet count

**Annotation:**
```
"247 failed authentication attempts from 192.168.88.10
Target: admin@LAB.LOCAL
Duration: 3 minutes 45 seconds"
```

---

### Screenshot 2: Attack Timeline

**Purpose:** Show attack pattern

**Setup:**
1. Filter: `kerberos.error_code == 24`
2. View > Time Display Format > Time of Day
3. Sort by time
4. Screenshot showing pattern

**Annotation:**
```
"Regular timing pattern indicates automated attack
Average: 1.1 attempts per second"
```

---

### Screenshot 3: Successful Compromise

**Purpose:** Show attack succeeded

**Setup:**
1. Filter: `kerberos.msg_type == 11 && !kerberos.error_code && ip.src == ATTACKER_IP`
2. Expand first success packet
3. Show enc-part (encrypted ticket)

**Annotation:**
```
"Attack successful after 234 attempts
Ticket issued: 2025-02-07 10:25:47
Valid for: 10 hours"
```

---

### Screenshot 4: Attack Comparison

**Purpose:** Show before/after

**Setup:**
1. Open two Wireshark windows
2. Left: Normal traffic
3. Right: Attack traffic

**Annotation:**
```
"Normal: 10-20 packets/minute
Attack: 247 packets in 3 minutes"
```

---

## 🔧 Essential Menu Actions

### File Menu
```
File > Open           # Open pcap file
File > Export Packet Dissections > As Plain Text
                      # Export to text for reports
File > Export Specified Packets
                      # Save filtered packets to new pcap
```

### Edit Menu
```
Edit > Find Packet    # Search for specific data
Edit > Find Next      # Continue search
```

### View Menu
```
View > Time Display Format > Time of Day
                      # Human-readable timestamps
View > Coloring Rules # Highlight packet types
View > Expand All     # See all packet details
```

### Statistics Menu
```
Statistics > Protocol Hierarchy
                      # Traffic breakdown
Statistics > Conversations
                      # Connection pairs
Statistics > Endpoints
                      # Individual hosts
Statistics > I/O Graph
                      # Traffic over time
```

### Analyze Menu
```
Analyze > Expert Information
                      # Automatic anomaly detection
Analyze > Follow > TCP Stream
                      # Full conversation
```

---

## 💡 Pro Tips for Your Project

### Tip 1: Color Failed Auths Red

**Setup coloring rule:**
1. View > Coloring Rules
2. New rule: "Kerberos Failed Auth"
3. Filter: `kerberos.error_code == 24`
4. Foreground: White, Background: Red
5. Apply

**Result:** Failed attempts jump out visually

---

### Tip 2: Create Custom Columns

**Add "Kerberos User" column:**
1. Right-click packet list header
2. Column Preferences
3. Add new column:
   - Title: "User"
   - Type: Custom
   - Field: kerberos.cname_string
4. Apply

**Result:** See usernames at a glance

---

### Tip 3: Save Display Filters

**Save your common filters:**
1. Apply filter: `kerberos.error_code == 24`
2. Click bookmark icon (next to filter bar)
3. Name it: "Kerberos Failed Auth"
4. Save

**Result:** One-click access to common filters

---

### Tip 4: Export Attack Evidence

**Create attack report:**
1. Filter to show only attack packets
2. File > Export Packet Dissections > As Plain Text
3. Save as: `bruteforce_evidence_20250207.txt`

**Use in:** Portfolio documentation, reports

---

## 📊 Analysis Workflow for Each Attack

### Standard Analysis Process:

**1. Open capture**
```bash
wireshark attack_name.pcap
```

**2. Quick statistics**
```
Statistics > Protocol Hierarchy
```
Note: Total packets, Kerberos percentage

**3. Find conversations**
```
Statistics > Conversations
```
Sort by packets, identify attacker IP

**4. Apply attack-specific filter**
```
# Brute force
kerberos.error_code == 24

# AS-REP roasting
kerberos.msg_type == 11

# Kerberoasting
kerberos.msg_type == 12
```

**5. Analyze timing**
```
View > Time Display Format > Seconds Since Previous Packet
```
Calculate attack rate

**6. Extract evidence**
- Screenshot key findings
- Export filtered packets
- Note findings

**7. Document**
- Attack type
- Source IP
- Target accounts
- Timing/rate
- Success/failure

---

## 🎯 Attack-Specific Analysis Guides

### Brute Force Attack Analysis

**Filter sequence:**
```
1. kerberos.error_code == 24
   → Count failures

2. kerberos.msg_type == 11 && !kerberos.error_code && ip.src == ATTACKER_IP
   → Check if succeeded

3. Statistics > I/O Graph
   → Visualize attack rate over time
```

**Key metrics:**
- Total attempts: (packet count)
- Duration: (first to last packet time)
- Rate: (attempts / duration)
- Target user: (kerberos.cname)
- Success: (yes/no)

---

### AS-REP Roasting Analysis

**Filter sequence:**
```
1. kerberos.msg_type == 10
   → Count AS-REQ

2. kerberos.msg_type == 11
   → Count AS-REP (responses)

3. kerberos.msg_type == 11 && !kerberos.pa_data
   → Find vulnerable responses (no pre-auth)
```

**Key metrics:**
- Users tested: (unique cnames)
- Roastable found: (AS-REP without pa_data)
- Hashes captured: (AS-REP with enc-part)

---

### Kerberoasting Analysis

**Filter sequence:**
```
1. kerberos.msg_type == 12
   → Count TGS-REQ

2. Statistics > Conversations
   → Find source IP

3. kerberos.msg_type == 12 && ip.src == ATTACKER_IP
   → Filter to attacker only

4. Expand each packet, note kerberos.sname
   → List services targeted
```

**Key metrics:**
- Service tickets requested: (TGS-REQ count)
- Unique services: (count distinct snames)
- Time window: (first to last)
- Rate: (requests / duration)

---

## 🐛 Common Issues & Solutions

### Issue: "Too many packets to analyze"

**Solution:**
```
1. Apply kerberos filter first
2. Then add specific filters
3. Or: Export filtered packets to new smaller file
```

---

### Issue: "Can't see Kerberos details"

**Solution:**
```
1. Check packet is UDP port 88 or TCP port 88
2. Expand packet details (click arrow)
3. If encrypted, you won't see inside (normal)
```

---

### Issue: "Time format confusing"

**Solution:**
```
View > Time Display Format > Time of Day
```

---

### Issue: "Lost in the data"

**Solution:**
```
1. Start with Statistics > Protocol Hierarchy
2. Then Statistics > Conversations
3. Identify key IPs
4. Apply simple filters first
5. Add complexity gradually
```

---

## 📚 Learn by Doing: 5 Exercises

### Exercise 1: Count Failed Attempts

**Goal:** Find how many passwords were tried

```
1. Open bruteforce capture
2. Filter: kerberos.error_code == 24
3. Note packet count at bottom
```

**Answer format:** "234 failed attempts"

---

### Exercise 2: Find Attacker IP

**Goal:** Identify source of attack

```
1. Open any attack capture
2. Statistics > Conversations
3. TCP tab
4. Sort by Packets (descending)
5. Top IP with most packets = attacker
```

---

### Exercise 3: Calculate Attack Rate

**Goal:** Measure brute force speed

```
1. Open bruteforce capture
2. Filter: kerberos.error_code == 24
3. Note first packet time
4. Note last packet time
5. Count packets
6. Calculate: packets / (last - first) in seconds
```

**Answer format:** "1.7 attempts per second"

---

### Exercise 4: Find Compromised Accounts

**Goal:** See if attack succeeded

```
1. Open capture
2. Filter: kerberos.msg_type == 11 && !kerberos.error_code
3. Note cname (username)
4. If from attacker IP = compromised
```

---

### Exercise 5: Extract Service List

**Goal:** List all services in Kerberoasting

```
1. Open kerberoasting capture
2. Filter: kerberos.msg_type == 12
3. For each packet, expand:
   Kerberos > tgs-req > sname
4. Note each unique service
```

**Answer format:**
```
Services targeted:
- HTTP/webserver.lab.local
- CIFS/fileserver.lab.local
- MSSQL/dbserver.lab.local
```

---

## 📖 Quick Reference Card

**Print and keep handy:**

```
┌───────────────────────────────────────────────────────────┐
│         Wireshark Kerberos Quick Reference                 │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ESSENTIAL FILTERS:                                        │
│  kerberos                       # All Kerberos            │
│  kerberos.error_code == 24      # Failed auth             │
│  kerberos.msg_type == 10        # AS-REQ                  │
│  kerberos.msg_type == 11        # AS-REP                  │
│  kerberos.msg_type == 12        # TGS-REQ                 │
│                                                            │
│  ESSENTIAL MENUS:                                          │
│  Statistics > Conversations     # Find attacker IP        │
│  Statistics > Protocol Hierarchy # Traffic summary        │
│  Analyze > Follow > TCP Stream  # Full conversation       │
│  File > Export Packet Dissections # Save evidence         │
│                                                            │
│  ATTACK PATTERNS:                                          │
│  Brute Force: Many error_code 24 from one IP             │
│  AS-REP Roast: Multiple msg_type 11 without pa_data      │
│  Kerberoast: Many msg_type 12 from one IP                │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

---

## 🎓 You've Mastered Wireshark When...

**Competency checklist:**

- [ ] Can open a pcap file
- [ ] Can apply basic Kerberos filter
- [ ] Can find failed authentication attempts
- [ ] Can identify attacker IP address
- [ ] Can count packets in a capture
- [ ] Can follow a TCP stream
- [ ] Can export evidence to text
- [ ] Can create screenshots for portfolio
- [ ] Can calculate attack rate
- [ ] Can identify attack type from patterns

**That's the 20% that matters.**

---

## 🚀 Integration with Your Project

### Complete Workflow Example:

**Day 1: Capture Attack**
```bash
sudo tcpdump -i any port 88 -w bruteforce_$(date +%Y%m%d).pcap
python3 01_bruteforce.py [options]
# Stop tcpdump
```

**Day 2: Analyze Attack**
```bash
wireshark bruteforce_20250207.pcap

# Apply filters, take screenshots, export evidence
```

**Day 3: Document Attack**
```markdown
## Brute Force Attack Analysis

**Date:** 2025-02-07
**Capture:** bruteforce_20250207.pcap

**Findings:**
- Attacker IP: 192.168.88.10
- Target: admin@LAB.LOCAL
- Failed attempts: 234
- Duration: 3m 45s
- Rate: 1.04 attempts/second
- Result: SUCCESS (password: Spring2025!)

**Evidence:** [screenshots/]
**PCAP:** [captures/bruteforce_20250207.pcap]
```

---

## 📚 Additional Resources

**Official Wireshark:**
- User Guide: Help > Contents
- Display Filters: https://wiki.wireshark.org/DisplayFilters

**Kerberos-specific:**
- RFC 4120: Kerberos Protocol Specification
- MIT Kerberos Docs: https://web.mit.edu/kerberos/

---

## ✅ Next Steps

1. **Install Wireshark** (if not already)
   ```bash
   sudo apt install wireshark
   ```

2. **Practice with your captures**
   - Open each attack type
   - Apply the filters from this guide
   - Follow the analysis workflows

3. **Create screenshots**
   - Document each attack type
   - Save evidence for portfolio

4. **Integrate with monitoring**
   - Cross-reference with performance metrics
   - Correlate alerts with packet captures

---

**You're now competent in Wireshark for Kerberos security analysis.**

**Time investment:** 45 minutes reading + 2 hours practice = **Professional competence**

---

**Created by:** Emerson  
**Part of:** Enterprise Kerberos Security Project  
**Pairs with:** tcpdump guide  
**Next:** Document your findings!
