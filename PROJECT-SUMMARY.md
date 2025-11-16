# Wire-Py Network Security Scanner - Complete Project Summary

## 📁 Project Structure

```
wire-py/
├── rapid-scan.py              # Main network scanner with advanced firewall bypass
├── quick-scan.py              # Fast ARP-only scanner
├── advanced-scanner.py        # Advanced scanner with traffic analysis
├── wire.ps1                   # Automated Windows setup script
├── config.json                # Default scanner configuration
├── config_stealth.json        # Original stealth mode configuration
├── config_ultra_stealth.json  # NEW: Ultra stealth preset (maximum evasion)
├── config_balanced.json       # NEW: Balanced preset (speed vs stealth)
├── config_aggressive.json     # NEW: Aggressive preset (maximum speed)
├── requirements.txt           # Standard dependencies
├── requirements-advanced.txt  # Advanced scanner dependencies
├── ADVANCED-GUIDE.md          # Complete usage guide
├── FIREWALL-BYPASS-GUIDE.md   # NEW: Firewall evasion techniques guide
├── users.txt                  # Brute-force username wordlist
├── pass.txt                   # Brute-force password wordlist
├── scan_outputs/              # Scan results (JSON, CSV)
├── traffic_captures/          # Packet captures (PCAP files)
└── analysis_results/          # Analysis reports
```

## 🎯 Three Scanner Tools Included

### 1. rapid-scan.py - Comprehensive Network Scanner with Advanced Firewall Bypass
**Features:**
- ✅ ARP network discovery
- ✅ Multi-threaded Nmap scanning
- ✅ Vulnerability detection (CVE extraction)
- ✅ Service version fingerprinting
- ✅ OS detection
- ✅ Brute-force credential testing
- ✅ Web directory enumeration
- ✅ **ADVANCED FIREWALL BYPASS** with:
  - Source port manipulation (DNS-53, HTTP-80, HTTPS-443)
  - Packet fragmentation (Linux only)
  - Decoy IPs to confuse IDS/IPS systems
  - MTU size manipulation
  - Data length randomization
  - Timing and rate control
  - TTL manipulation
  - MAC address spoofing (Linux only)
  - Bad checksum testing
- ✅ **MULTIPLE SCAN TECHNIQUES**:
  - SYN scan (default)
  - FIN scan (stealth)
  - NULL scan (stealth)
  - XMAS scan (stealth)
- ✅ **ADAPTIVE RETRY LOGIC**:
  - Automatic retry with different techniques
  - Multiple fallback methods
  - IPv6 fallback support
  - Intelligent source port rotation
- ✅ Stores ARP data even when Nmap fails
- ✅ JSON and CSV export

**Usage:**
```bash
# Basic scan
python rapid-scan.py

# Scan specific network
python rapid-scan.py 192.168.1.0/24

# Scan single host
python rapid-scan.py 192.168.1.1
```

### 2. quick-scan.py - Fast Discovery Tool
**Features:**
- ✅ Lightning-fast ARP scanning only
- ✅ MAC vendor lookup
- ✅ Hostname resolution
- ✅ Works even with firewalls
- ✅ No admin privileges needed
- ✅ JSON output

**Usage:**
```bash
python quick-scan.py
```

### 3. advanced-scanner.py - Traffic Analysis Integration
**NEW Advanced Features:**

#### 🔍 1. Automated Captive Portal Detection
- Scans for HTTP/HTTPS services
- Captures traffic automatically
- Detects redirect-based portals
- Identifies authentication pages

#### 🛡️ 2. Vulnerability Assessment with Protocol Deep Dive
- Service version detection
- Runs Nmap vulnerability scripts
- Captures traffic on vulnerable services
- Protocol-specific analysis (HTTP, FTP, SMB, etc.)
- Saves detailed protocol breakdowns

#### 📊 3. Real-Time Anomaly Detection
- Continuous packet capture
- Periodic network scans (every 60s)
- Detects new hosts appearing
- Detects hosts disappearing
- Baseline comparison

#### 🔗 4. Correlated Nmap-Wireshark Analysis
- Full network scan
- Network-wide traffic capture
- Per-host packet correlation
- Creates separate PCAP per host
- Links scan results with traffic patterns

#### 🎯 5. Integrated Threat Hunting
- Combines all data sources
- Correlates vulnerabilities with traffic
- Identifies suspicious patterns
- Exports for SIEM integration

**Usage:**
```bash
# Captive portal detection
python advanced-scanner.py 192.168.100.0/24 --mode captive

# Vulnerability assessment
python advanced-scanner.py 192.168.100.0/24 --mode vuln

# Real-time monitoring (5 min)
python advanced-scanner.py 192.168.100.0/24 --mode realtime

# Full correlation
python advanced-scanner.py 192.168.100.0/24 --mode correlate

# All modes
python advanced-scanner.py 192.168.100.0/24 --mode all
```

## 🔧 Technologies Used

### Python Libraries
- **python-nmap**: Nmap integration
- **scapy**: Low-level packet manipulation and ARP scanning
- **mac-vendor-lookup**: MAC address vendor identification
- **tqdm**: Progress bars
- **lxml**: XML parsing for Nmap results
- **pandas**: Data analysis (optional)

### External Tools
- **Nmap**: Port scanning and service detection
- **Npcap/WinPcap**: Windows packet capture driver
- **Wireshark/tshark**: Packet capture and analysis
- **tcpdump**: Packet capture (Linux)

## 🚀 Setup & Installation

### Automated Setup (Windows)
```powershell
# Run PowerShell as Administrator
.\wire.ps1
```

This automatically:
1. Installs Python 3
2. Installs Nmap + Npcap
3. Creates virtual environment
4. Installs all dependencies
5. Runs the scanner

### Manual Setup
```bash
# Install system tools
winget install Nmap.Nmap
winget install WiresharkFoundation.Wireshark

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-advanced.txt  # For advanced scanner
```

## 📊 Output Examples

### JSON Output (rapid-scan.py)
```json
{
  "ip": "192.168.100.1",
  "mac": "fc:73:fb:68:e3:75",
  "vendor": "Huawei Technologies",
  "hostname": "router.local",
  "state": "up",
  "os": "Linux 3.x",
  "scan_result": "success",
  "ports": [
    {
      "port": 80,
      "protocol": "tcp",
      "state": "open",
      "service": "http",
      "product": "nginx",
      "version": "1.18.0"
    }
  ],
  "vulnerabilities": [
    {
      "port": 80,
      "script": "http-vuln-cve2021-12345",
      "cve_ids": ["CVE-2021-12345"],
      "severity": "High",
      "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-12345"]
    }
  ]
}
```

### Traffic Capture Files
```
traffic_captures/
├── capture_192.168.100.1_80_20251104_203015.pcap
├── capture_192.168.100.100_443_20251104_203045.pcap
├── realtime_20251104_203000.pcap
└── correlated_192.168.100.1.pcap
```

## 🎨 Key Features Summary

### Stealth Capabilities
- ✅ SYN scans (half-open connections)
- ✅ Decoy scanning (confuses IDS/IPS)
- ✅ Slow timing to avoid detection
- ✅ Packet fragmentation (Linux)
- ✅ Randomized scan order
- ✅ Fallback to simple scans

### Discovery & Enumeration
- ✅ ARP-based host discovery
- ✅ Port scanning (TCP/UDP)
- ✅ Service version detection
- ✅ OS fingerprinting
- ✅ MAC vendor lookup
- ✅ Hostname resolution

### Vulnerability Assessment
- ✅ CVE detection via NSE scripts
- ✅ Weak credential testing
- ✅ Web vulnerability scanning
- ✅ Service-specific exploits
- ✅ Protocol analysis
- ✅ Traffic pattern analysis

### Traffic Analysis
- ✅ Automated packet capture
- ✅ Protocol deep dives
- ✅ Captive portal detection
- ✅ Anomaly detection
- ✅ Real-time monitoring
- ✅ Traffic correlation

### Reporting
- ✅ JSON export (machine-readable)
- ✅ CSV export (spreadsheet)
- ✅ PCAP files (Wireshark compatible)
- ✅ Detailed logs
- ✅ Per-host reports
- ✅ Vulnerability summaries

## ⚠️ Security & Legal

### ⚡ Requirements
- **Administrator/Root privileges** for packet capture
- **Written authorization** to scan target networks
- **Network ownership** or explicit permission

### 🔐 Warnings
- Unauthorized scanning is **ILLEGAL** in most jurisdictions
- Can trigger intrusion detection systems
- May impact network performance
- Captures may contain sensitive data

### ✅ Ethical Use
- Penetration testing (authorized)
- Network asset management
- Security auditing
- Compliance verification
- Educational purposes (own lab)

## 📈 Improvements Made

### Original Issues Fixed
1. ❌ "Host data not found" errors
   - ✅ Now detects firewall blocking
   - ✅ Stores ARP data even when Nmap fails
   - ✅ Falls back to simple scans
   
2. ❌ config.json UTF-8 BOM encoding error
   - ✅ Recreated with proper UTF-8 encoding
   - ✅ Added stealth configuration template

3. ❌ Packet fragmentation errors on Windows
   - ✅ Platform detection
   - ✅ Only uses fragmentation on Linux/BSD

4. ❌ No traffic analysis
   - ✅ Full Wireshark integration
   - ✅ Automated capture workflows
   - ✅ Protocol-specific analysis

## 🎓 Learning Outcomes

By using these tools, you can learn:
- Network reconnaissance techniques
- Service fingerprinting
- Vulnerability assessment methodologies
- Packet analysis with Wireshark
- Stealth scanning techniques
- Anomaly detection
- Traffic correlation
- Protocol analysis
- Threat hunting workflows

## 🔮 Future Enhancements

Potential additions:
- Web GUI dashboard
- Database backend for historical data
- Machine learning for anomaly detection
- Integration with vulnerability databases
- Automated exploit testing (Metasploit)
- Report generation with charts
- Email/Slack alerts
- SIEM integration (Splunk, ELK)

## 📚 References

- Nmap: https://nmap.org/book/
- Wireshark: https://www.wireshark.org/docs/
- Scapy: https://scapy.readthedocs.io/
- MITRE ATT&CK: https://attack.mitre.org/
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/

## 🏆 Credits

Built with:
- Python 3.14
- Nmap 7.95
- Wireshark/tshark
- Scapy
- Love for network security 💙
