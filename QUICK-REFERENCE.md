# 🚀 Wire-Py Quick Reference Card

## Installation (Windows - Admin Required)
```powershell
.\wire.ps1  # Automated setup - installs everything
```

## Three Scanners - Choose Your Tool

### 1️⃣ Quick Scan (Fast, No Admin Needed)
```bash
python quick-scan.py
```
**Best for:** Quick device discovery, works with firewalls

### 2️⃣ Comprehensive Scan (Detailed Security Assessment)
```bash
python rapid-scan.py                    # Scan local network
python rapid-scan.py 192.168.1.0/24    # Scan specific network
python rapid-scan.py 10.0.0.5          # Scan single host
```
**Best for:** Full security audits, vulnerability detection

### 3️⃣ Advanced Scan (Traffic Analysis + Nmap)
```bash
# Detect captive portals
python advanced-scanner.py 192.168.100.0/24 --mode captive

# Find vulnerabilities + capture traffic
python advanced-scanner.py 192.168.100.0/24 --mode vuln

# Real-time monitoring (5 min)
python advanced-scanner.py 192.168.100.0/24 --mode realtime

# Full correlation
python advanced-scanner.py 192.168.100.0/24 --mode correlate

# Everything
python advanced-scanner.py 192.168.100.0/24 --mode all
```
**Best for:** Deep protocol analysis, anomaly detection, threat hunting

## Configuration Files

### config.json - Standard Mode
```json
{
  "nmap_scan_mode": "aggressive",
  "enable_brute_force": true,
  "max_nmap_threads": 5
}
```

### config_stealth.json - Stealth Mode
```json
{
  "nmap_scan_mode": "stealth",
  "use_decoys": true,
  "fragment_packets": true,
  "randomize_hosts": true
}
```

## Output Locations
```
📁 scan_outputs/          → JSON/CSV scan results
📁 traffic_captures/      → PCAP files (Wireshark)
📁 analysis_results/      → Analysis reports
📄 network_scanner_advanced.log  → Detailed logs
```

## Analyzing Results

### View JSON Results
```bash
cat scan_outputs/network_scan_results_*.json | python -m json.tool
```

### Open in Wireshark
```bash
wireshark traffic_captures/capture_192.168.100.1_80_*.pcap
```

### Command-Line Analysis
```bash
# HTTP traffic
tshark -r capture.pcap -Y "http.request"

# Count packets per host
tshark -r capture.pcap -q -z ip_hosts,tree
```

## Common Use Cases

### 🔍 Network Discovery
```bash
python quick-scan.py  # Fastest
```

### 🛡️ Security Audit
```bash
python rapid-scan.py 192.168.1.0/24
# Check: scan_outputs/*.json for vulnerabilities
```

### 🚨 Detect Rogue Devices
```bash
python advanced-scanner.py 192.168.1.0/24 --mode realtime
# Monitors for new devices appearing
```

### 🕵️ Investigate Suspicious Host
```bash
python advanced-scanner.py 192.168.1.50/32 --mode correlate
# Deep dive on single host
```

### 📡 Find Captive Portals
```bash
python advanced-scanner.py 192.168.1.0/24 --mode captive
```

## Troubleshooting

### ❌ "nmap not found"
```bash
$env:PATH += ";C:\Program Files (x86)\Nmap"
```

### ❌ "Permission denied" (packet capture)
```
Run PowerShell as Administrator
```

### ❌ "No data found"
```
Hosts have firewalls - use quick-scan.py instead
```

### ❌ "tshark not found"
```bash
# Install Wireshark (includes tshark)
winget install WiresharkFoundation.Wireshark
```

## Stealth Tips

✅ **More stealthy:**
- Use `-T2` timing (slower)
- Enable decoys
- Scan during business hours
- Randomize host order

❌ **Less stealthy:**
- `-T4` or `-T5` timing (fast)
- Full `-A` aggressive scan
- Scanning all 65535 ports
- Brute-force attacks

## Legal Reminders

⚠️ **ONLY scan networks you own or have written permission to test**

✅ Legal:
- Your home network
- Company network (with authorization)
- Lab environments
- Bug bounty programs (within scope)

❌ Illegal:
- Public WiFi networks
- Neighbor's network
- Corporate networks (without permission)
- Any network you don't own

## Quick Cheat Sheet

| Task | Command |
|------|---------|
| Fast discovery | `python quick-scan.py` |
| Full scan | `python rapid-scan.py` |
| Stealth scan | Edit config.json → set mode to "stealth" |
| Capture traffic | `python advanced-scanner.py <target> --mode vuln` |
| Monitor network | `python advanced-scanner.py <target> --mode realtime` |
| Find portals | `python advanced-scanner.py <target> --mode captive` |

## Need Help?

📖 Full documentation: `ADVANCED-GUIDE.md`
📊 Project overview: `PROJECT-SUMMARY.md`
🔧 Configuration: Edit `config.json`

---
**Remember:** With great power comes great responsibility! 🕷️
