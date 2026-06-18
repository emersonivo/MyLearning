# tcpdump + Wireshark: Combined Quick Reference
## Your One-Page Cheat Sheet for Kerberos Traffic Analysis

**Print this. Laminate it. Keep it by your keyboard.**

---

## 🎯 Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. CAPTURE (tcpdump) → 2. ANALYZE (Wireshark) → 3. REPORT  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📥 CAPTURE (tcpdump)

### Basic Capture Template
```bash
sudo tcpdump -i any -nn -tttt port 88 -w capture_name.pcap
```

### Quick Captures by Scenario

**Brute Force:**
```bash
sudo tcpdump -i any port 88 -w bruteforce_$(date +%Y%m%d_%H%M%S).pcap
```

**AS-REP Roasting:**
```bash
sudo tcpdump -i any port 88 -w asrep_$(date +%Y%m%d_%H%M%S).pcap
```

**Kerberoasting:**
```bash
sudo tcpdump -i any port 88 -w kerberoast_$(date +%Y%m%d_%H%M%S).pcap
```

**Specific Attacker:**
```bash
sudo tcpdump -i any port 88 and host 192.168.88.10 -w attacker.pcap
```

### Stop Capture
```
Ctrl+C
```

### Verify Capture
```bash
tcpdump -r capture.pcap | wc -l      # Count packets
tcpdump -r capture.pcap -c 5         # Preview first 5
```

---

## 🔍 ANALYZE (Wireshark)

### Open Capture
```bash
wireshark capture.pcap &
```

### Essential Filters

| Purpose | Filter |
|---------|--------|
| All Kerberos | `kerberos` |
| Failed Auth | `kerberos.error_code == 24` |
| Successful Auth | `kerberos.msg_type == 11 && !kerberos.error_code` |
| AS-REQ | `kerberos.msg_type == 10` |
| TGS-REQ | `kerberos.msg_type == 12` |
| From Attacker | `kerberos && ip.src == 192.168.88.10` |

### Quick Analysis Steps

**1. Find Attacker IP:**
```
Statistics > Conversations > TCP tab > Sort by Packets
```

**2. Count Attack Packets:**
```
Apply filter → Note packet count at bottom
```

**3. Follow Attack:**
```
Right-click packet → Follow > TCP Stream
```

**4. Extract Evidence:**
```
File > Export Packet Dissections > As Plain Text
```

---

## 📊 ATTACK SIGNATURES

### Brute Force
**tcpdump capture:**
```bash
sudo tcpdump -i any port 88 -w bruteforce.pcap
# Run attack script
# Ctrl+C
```

**Wireshark analysis:**
```
1. Filter: kerberos.error_code == 24
2. Count packets (failed attempts)
3. Statistics > Conversations (find attacker IP)
4. Check success: kerberos.msg_type == 11 && !kerberos.error_code
```

**Signature:**
- Many error_code 24 from single IP
- Same username (cname)
- Regular timing (1-5 per second)

---

### AS-REP Roasting
**tcpdump capture:**
```bash
sudo tcpdump -i any port 88 -w asrep.pcap
# Run AS-REP roast
# Ctrl+C
```

**Wireshark analysis:**
```
1. Filter: kerberos.msg_type == 11
2. Look for: !kerberos.pa_data (no pre-auth)
3. Count unique usernames tested
4. Find roastable accounts
```

**Signature:**
- Multiple AS-REP without pre-auth data
- Different usernames from same IP
- Short time window

---

### Kerberoasting
**tcpdump capture:**
```bash
sudo tcpdump -i any port 88 -w kerberoast.pcap
# Run Kerberoasting
# Ctrl+C
```

**Wireshark analysis:**
```
1. Filter: kerberos.msg_type == 12
2. Count TGS-REQ packets
3. List unique service names (sname)
4. Check timing pattern
```

**Signature:**
- Many TGS-REQ from single IP
- Different service principals
- Rapid succession (10+ requests in <1 minute)

---

## 📋 One-Liner Commands

### Capture + Count
```bash
sudo tcpdump -i any port 88 -w test.pcap -c 100  # Capture exactly 100 packets
```

### Capture + Display
```bash
sudo tcpdump -i any port 88 -w test.pcap -l | tee test.log  # See + save
```

### Capture with Auto-Rotate
```bash
sudo tcpdump -i any port 88 -w capture.pcap -C 100 -W 5  # 100MB files, keep 5
```

### Quick Analysis
```bash
tcpdump -r capture.pcap -nn | grep "error"  # Find errors quickly
```

---

## 🎯 Attack Analysis Checklist

For each capture, document:

**[ ] Basic Info**
- Date/time:
- Capture file:
- Total packets:

**[ ] Attack Details**
- Type: (brute force / AS-REP / Kerberoast / other)
- Source IP:
- Target: (user/service)
- Duration:

**[ ] Metrics**
- Total attempts:
- Failed:
- Successful:
- Rate (per second):

**[ ] Evidence**
- Screenshot location:
- Exported text location:
- Key findings:

---

## 🔧 Common Wireshark Menu Actions

| Action | Menu Path |
|--------|-----------|
| Open File | File > Open |
| Export Text | File > Export Packet Dissections > As Plain Text |
| Find Packet | Edit > Find Packet |
| Follow Stream | Right-click > Follow > TCP Stream |
| Conversations | Statistics > Conversations |
| Protocol Stats | Statistics > Protocol Hierarchy |
| Time Format | View > Time Display Format > Time of Day |
| Expert Info | Analyze > Expert Information |

---

## 🎨 Portfolio Screenshot Checklist

**For each attack type, capture:**

**[ ] Overview Screenshot**
- Full Wireshark window
- Filter applied
- Packet count visible
- Annotate: Attack type, count, duration

**[ ] Detail Screenshot**
- Expanded packet showing attack details
- Highlight key fields (error code, username, etc.)
- Annotate: What makes this malicious

**[ ] Statistics Screenshot**
- Conversations or Protocol Hierarchy
- Show attacker IP prominence
- Annotate: Traffic volume comparison

**[ ] Timeline Screenshot**
- Time column visible
- Show pattern over time
- Annotate: Attack rate/timing

---

## 📁 File Organization Template

```
kerberos-captures/
├── 20250207/
│   ├── 01_bruteforce_admin_093042.pcap
│   ├── 01_bruteforce_admin_093042_analysis.txt
│   ├── 01_bruteforce_admin_093042.md
│   ├── 02_asrep_roast_104523.pcap
│   ├── 02_asrep_roast_104523_analysis.txt
│   ├── 02_asrep_roast_104523.md
│   └── screenshots/
│       ├── bruteforce_overview.png
│       ├── bruteforce_detail.png
│       └── bruteforce_stats.png
└── scripts/
    ├── capture_attack.sh
    └── analyze_attack.sh
```

---

## 🚨 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| No packets captured | Check `sudo netstat -tulpn \| grep :88` |
| Permission denied | Use `sudo tcpdump` |
| Can't see Kerberos | Apply filter: `kerberos` |
| Too many packets | Filter by IP: `kerberos && ip.src == X.X.X.X` |
| Time confusing | View > Time Display Format > Time of Day |
| Lost in data | Start: Statistics > Conversations |

---

## ⚡ Speed Tips

**Capture faster:**
```bash
alias kcap='sudo tcpdump -i any port 88 -w'
# Usage: kcap attack.pcap
```

**Analyze faster:**
```bash
alias kshark='wireshark'
# Usage: kshark attack.pcap &
```

**Count faster:**
```bash
alias kcount='tcpdump -r'
# Usage: kcount attack.pcap | wc -l
```

**Add to ~/.bashrc**

---

## 🎓 Mastery Test

**You're competent when you can:**

1. **Capture** Kerberos traffic to a pcap file
2. **Verify** packet count without opening Wireshark
3. **Open** capture in Wireshark
4. **Filter** to show only failed authentications
5. **Find** the attacker's IP address
6. **Count** total attack attempts
7. **Calculate** attack rate (attempts/second)
8. **Extract** evidence to text file
9. **Take** portfolio-quality screenshot
10. **Document** findings in markdown

**Time to competence:** 2-3 hours practice

---

## 📞 Quick Help

**tcpdump man page:**
```bash
man tcpdump
```

**Wireshark help:**
```
Help > Contents
```

**Display filter reference:**
```
Help > Supported Protocols
```

**Online:**
- tcpdump: https://www.tcpdump.org/
- Wireshark: https://www.wireshark.org/docs/

---

## 🎯 Your First Hour Plan

**Minute 0-15: Setup**
- Install tools
- Create directories
- Save this cheat sheet

**Minute 15-30: Capture Practice**
- Run 3 test captures
- Verify each one
- Count packets

**Minute 30-45: Analysis Practice**
- Open each capture
- Apply 5 essential filters
- Take 1 screenshot each

**Minute 45-60: Real Attack**
- Capture a brute force
- Analyze it completely
- Document findings

---

## ✅ Daily Workflow

**Morning: Capture**
```bash
cd ~/kerberos-captures/$(date +%Y%m%d)
sudo tcpdump -i any port 88 -w attack_$(date +%H%M%S).pcap
# Run attack script
# Ctrl+C
```

**Afternoon: Analyze**
```bash
wireshark attack_*.pcap
# Apply filters
# Take screenshots
# Export evidence
```

**Evening: Document**
```markdown
# Analysis: [attack_name]
- Type: [brute force/AS-REP/Kerberoast]
- Source: [IP]
- Findings: [summary]
- Evidence: [screenshots]
```

---

## 🏆 Success Metrics

**After 1 week:**
- [ ] 10+ captures created
- [ ] All attack types analyzed
- [ ] Screenshots for portfolio
- [ ] Documentation complete

**After 2 weeks:**
- [ ] Can capture/analyze in <10 minutes
- [ ] Created custom filters
- [ ] Automated capture scripts
- [ ] Portfolio-ready

---

## 💾 Save This

```bash
# Save to your home directory
cp tcpdump_wireshark_quickref.md ~/
cat ~/tcpdump_wireshark_quickref.md
```

**Or:**
1. Print this page
2. Laminate it
3. Keep by keyboard
4. Reference constantly

---

**You now have everything needed for professional packet analysis.**

**Next:** Capture your first attack and analyze it!

---

**Created by:** Emerson  
**Date:** February 2025  
**Part of:** Enterprise Kerberos Security Project  

---

**🎯 Remember:**
- **Capture:** `sudo tcpdump -i any port 88 -w file.pcap`
- **Analyze:** `wireshark file.pcap`
- **Filter:** `kerberos` + specific filters
- **Document:** Screenshots + notes

**That's it. You're ready.**
