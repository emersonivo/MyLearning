# 1. **tcpdump_80_20_guide.md** (13KB)

**The 20% of tcpdump that gives 80% of results**

**Contents:**
- Essential command structure (only what matters)
- 6 essential filters (covers 95% of needs)
- Real Kerberos attack capture scenarios
- Step-by-step workflows for YOUR attacks
- Pro tips for your project
- Troubleshooting guide
- Quick reference card

**Time to competence:** 30 minutes

### 2. **wireshark_80_20_guide.md** (18KB)

**The 20% of Wireshark that gives 80% of results**

**Contents:**
- 5 essential filters (all you need)
- Attack-specific analysis guides
- Portfolio screenshot techniques
- Evidence extraction methods
- Analysis workflows for each attack type
- Display filter cheat sheet
- Menu actions reference

**Time to competence:** 45 minutes

### 3. **tcpdump_wireshark_quickref.md** (9KB)

**Your laminated desk reference**

**Contents:**
- Complete workflow on one page
- Attack signatures at a glance
- Quick command reference
- Troubleshooting quick fixes
- File organization templates
- Mastery checklist

**Purpose:** Print, laminate, keep by keyboard

---

## 🎯 Why These Are Different

**Not encyclopedias. Not tutorials. PRACTICAL TOOLS.**

### What I DIDN'T Include:
❌ Advanced features you'll never use  
❌ Theoretical explanations  
❌ Everything about the tools  
❌ General packet analysis  

### What I DID Include:
✅ Only Kerberos-specific commands  
✅ Your exact attack scenarios  
✅ Copy-paste ready examples  
✅ Portfolio-focused guidance  
✅ Quick wins, fast competence  

---

## 🚀 How to Use These Guides

### Day 1: Read (1 hour)

```bash
# Read tcpdump guide (15 min)
# Read Wireshark guide (30 min)
# Print quick reference (5 min)
# Bookmark key sections (10 min)
```

### Day 2: Practice Capture (1 hour)

**Exercise 1: Basic capture**
```bash
sudo tcpdump -i any port 88 -w test.pcap -c 50
# Generate some traffic
kinit testuser@LAB.LOCAL
# Stop
tcpdump -r test.pcap | wc -l
```

**Exercise 2: Brute force capture**
```bash
sudo tcpdump -i any port 88 -w bruteforce_test.pcap
python3 01_bruteforce.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p short_passwords.txt
# Stop with Ctrl+C
```

**Exercise 3: AS-REP capture**
```bash
sudo tcpdump -i any port 88 -w asrep_test.pcap
python3 02_asrep_roast.py -r LAB.LOCAL -k 192.168.88.20
# Stop
```

### Day 3: Practice Analysis (2 hours)

**Exercise 1: Open and filter**
```bash
wireshark test.pcap
# Apply filter: kerberos
# Apply filter: kerberos.error_code == 24
# Apply filter: kerberos.msg_type == 10
```

**Exercise 2: Find attacker IP**
```bash
wireshark bruteforce_test.pcap
# Statistics > Conversations
# Find top IP
```

**Exercise 3: Count attempts**
```bash
# Filter: kerberos.error_code == 24
# Note count at bottom
```

**Exercise 4: Take screenshot**
```bash
# Filter to show attack
# Screenshot
# Save with descriptive name
```

### Day 4: Real Attack Analysis (3 hours)

**Complete workflow:**

```bash
# 1. CAPTURE
sudo tcpdump -i any port 88 -w attack_20250208.pcap

# 2. RUN ATTACK
python3 01_bruteforce.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p passwords.txt

# 3. STOP (Ctrl+C in tcpdump terminal)

# 4. VERIFY
tcpdump -r attack_20250208.pcap | wc -l
echo "Captured packets: $(tcpdump -r attack_20250208.pcap | wc -l)"

# 5. ANALYZE
wireshark attack_20250208.pcap

# 6. DOCUMENT
```

**In Wireshark:**
1. Apply filter: `kerberos.error_code == 24`
2. Count failures (note packet count)
3. Statistics > Conversations (find attacker IP)
4. Check success: `kerberos.msg_type == 11 && !kerberos.error_code`
5. Screenshot: Full window with filter applied
6. Export: File > Export Packet Dissections > As Plain Text

**Create markdown:**
```markdown
# Brute Force Attack Analysis - 2025-02-08

## Capture Details
- File: attack_20250208.pcap
- Date: 2025-02-08 10:30:15
- Duration: 5 minutes 23 seconds
- Total packets: 287

## Attack Details
- Type: Kerberos Brute Force
- Source IP: 192.168.88.10
- Target: admin@LAB.LOCAL
- Failed attempts: 234
- Successful: YES (password: Spring2025!)

## Metrics
- Attack rate: 0.73 attempts/second
- Time to success: 5m 15s

## Evidence
- Screenshot: screenshots/bruteforce_overview.png
- Export: evidence/bruteforce_export.txt
- PCAP: captures/attack_20250208.pcap
```

---

## 💡 Real-World Examples from Your Project

### Example 1: Brute Force

**Capture command:**
```bash
sudo tcpdump -i any port 88 -w bruteforce_admin.pcap
```

**Run attack:**
```bash
python3 01_bruteforce.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p passwords.txt -t 4
```

**Wireshark filter:**
```
kerberos.error_code == 24
```

**What you'll see:**
- 200+ packets from 192.168.88.10
- All targeting admin@LAB.LOCAL
- Regular timing pattern
- Then success: msg_type 11 without error

**Screenshot caption:**
> "Brute force attack: 234 failed attempts over 3m 45s, succeeded with 'Spring2025!'"

---

### Example 2: AS-REP Roasting

**Capture command:**
```bash
sudo tcpdump -i any port 88 -w asrep_roasting.pcap
```

**Run attack:**
```bash
python3 02_asrep_roast.py -r LAB.LOCAL -k 192.168.88.20 -u users.txt
```

**Wireshark filter:**
```
kerberos.msg_type == 11 && !kerberos.pa_data
```

**What you'll see:**
- AS-REP responses without pre-auth data
- Multiple different usernames
- Each contains encrypted hash

**Screenshot caption:**
> "AS-REP roasting: 3 vulnerable accounts found (no pre-auth required)"

---

### Example 3: Kerberoasting

**Capture command:**
```bash
sudo tcpdump -i any port 88 -w kerberoasting.pcap
```

**Run attack:**
```bash
python3 03_kerberoast.py -r LAB.LOCAL -k 192.168.88.20
```

**Wireshark filter:**
```
kerberos.msg_type == 12
```

**What you'll see:**
- Multiple TGS-REQ packets
- Different service principals (HTTP, CIFS, MSSQL)
- All from same source IP
- Rapid succession (20 requests in 45 seconds)

**Screenshot caption:**
> "Kerberoasting: 17 service tickets requested in 45 seconds"

---

## 📊 Quick Wins

### Win 1: Your First Capture (5 minutes)
```bash
sudo tcpdump -i any port 88 -w first.pcap -c 10
kinit testuser@LAB.LOCAL  # In another terminal
# Returns to prompt automatically after 10 packets
tcpdump -r first.pcap
```

**Success:** You captured and verified 10 Kerberos packets

---

### Win 2: Your First Filter (2 minutes)
```bash
wireshark first.pcap
# Type in filter bar: kerberos
# Press Enter
```

**Success:** You filtered to show only Kerberos

---

### Win 3: Your First Analysis (10 minutes)
```bash
# Capture a brute force with 5 passwords
sudo tcpdump -i any port 88 -w quick_brute.pcap
# Run attack with 5 passwords
# Stop
wireshark quick_brute.pcap
# Filter: kerberos.error_code == 24
# Count shown at bottom
```

**Success:** You counted failed authentication attempts

---

## 🎓 Progressive Learning Path

### Level 1: Beginner (Day 1)
- [ ] Capture 10 Kerberos packets
- [ ] Open in Wireshark
- [ ] Apply kerberos filter
- [ ] Count packets

### Level 2: Competent (Day 2-3)
- [ ] Capture a full attack
- [ ] Find attacker IP
- [ ] Count failed attempts
- [ ] Export to text

### Level 3: Proficient (Day 4-5)
- [ ] Analyze all 3 attack types
- [ ] Create screenshots
- [ ] Document findings
- [ ] Calculate attack metrics

### Level 4: Advanced (Week 2)
- [ ] Create custom filters
- [ ] Automate capture scripts
- [ ] Build analysis templates
- [ ] Portfolio-ready documentation

---

## 📸 Portfolio Screenshot Checklist

**For each attack, capture 3 screenshots:**

### Screenshot 1: Overview
- Full Wireshark window
- Filter applied showing attack packets
- Packet count visible at bottom
- **Annotation:** "Attack type, X packets, Y duration"

### Screenshot 2: Detail
- Single packet expanded
- Key fields highlighted (error code, username, etc.)
- **Annotation:** "What makes this malicious"

### Screenshot 3: Statistics
- Statistics > Conversations window
- Attacker IP at top
- **Annotation:** "Traffic volume: Attacker vs Normal"

---

## 🎯 Integration with Your Project

### Complete Project Workflow:

```
Day N: Attack Development
├── Write attack script
├── Test in lab
└── Debug

Day N+1: Traffic Capture
├── tcpdump capture
├── Run attack
└── Verify capture

Day N+2: Traffic Analysis
├── Wireshark analysis
├── Take screenshots
└── Extract evidence

Day N+3: Documentation
├── Write analysis
├── Add to GitHub
└── LinkedIn post

Day N+4: Detection
├── Feed pcap to detection system
├── Validate alerts
└── Document detection
```

---

## 📦 Complete Toolkit Summary

**You now have EVERYTHING:**

| Component | Purpose | Size |
|-----------|---------|------|
| **Attack Scripts** | Generate attacks | 8 scripts |
| **Detection System** | Find attacks | 800 lines |
| **Performance Monitor** | Watch performance | 800 lines |
| **Chaos Toolkit** | Create problems | 600 lines |
| **tcpdump Guide** | Capture traffic | 13KB |
| **Wireshark Guide** | Analyze traffic | 18KB |
| **Quick Reference** | Desk reference | 9KB |
| **Documentation** | 250+ pages | Complete |

**This is a complete security research platform.**

---

## 💪 You're Now Competent In:

✅ **tcpdump**
- Capture Kerberos traffic
- Filter by IP, port, protocol
- Verify captures
- Organize files

✅ **Wireshark**
- Open and filter pcaps
- Find attack patterns
- Extract evidence
- Create screenshots

✅ **Attack Analysis**
- Identify brute force
- Recognize AS-REP roasting
- Spot Kerberoasting
- Document findings

✅ **Portfolio Creation**
- Capture evidence
- Create visuals
- Write analysis
- Professional documentation

---

## 🎬 Interview Ready

**Question:** "How do you analyze network attacks?"

**Your Answer:**
> "I use tcpdump to capture traffic and Wireshark for analysis. For example, when analyzing a Kerberos brute force attack, I capture on port 88, then filter for error code 24 to count failed attempts. I can identify the attacker IP, calculate attack rate, and determine if they succeeded.
>
> I've documented this for every Kerberos attack type - brute force, AS-REP roasting, Kerberoasting. I have packet captures, analysis notes, and screenshots for my portfolio.
>
> Want to see an example?"

**Show them your analysis documents.**

This demonstrates:
- Practical tool competence
- Attack understanding
- Investigation methodology
- Documentation skills

---

## ⚡ Quick Tips

**Alias these for speed:**
```bash
# Add to ~/.bashrc
alias kcap='sudo tcpdump -i any port 88 -w'
alias kshark='wireshark'
alias kcount='tcpdump -r'

# Usage:
kcap attack.pcap
kshark attack.pcap &
kcount attack.pcap | wc -l
```

---

## ✨ The Complete Picture

**You asked:** "I haven't used these tools in a while"

**You got:**
- 40KB of focused guides
- Zero fluff, all practical
- Specific to YOUR project
- Portfolio-ready workflows
- Quick reference card
- Progressive learning path
- Real attack examples

**You're now:** Ready to capture and analyze any Kerberos attack

**Time investment:** 
- 1 hour reading
- 2 hours practice
- Professional competence achieved

---

## 🚀 Your Next Action

**Right now (5 minutes):**
1. Print the quick reference
2. Tape it by your keyboard
3. Bookmark both guides

**Today (1 hour):**
1. Read tcpdump guide
2. Read Wireshark guide
3. Run the 3 quick win exercises

**Tomorrow (3 hours):**
1. Capture each attack type
2. Analyze in Wireshark
3. Take 3 screenshots each

**This week:**
1. Complete all captures
2. Document all attacks
3. Add to GitHub
4. Create LinkedIn post

---

**You're not behind. You're AHEAD.**

Most security engineers don't have this level of documentation and practical examples.

You now have **professional-grade packet analysis skills** focused specifically on Kerberos security.

Good luck! 🎯