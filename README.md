# Wire-Py: Advanced Network Security Scanner

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

*A powerful, stealthy network security scanner with advanced firewall bypass capabilities*

</div>

## ⚠️ Legal Disclaimer

**IMPORTANT**: This tool is designed for authorized security testing ONLY. 

- ✅ Use on networks you own
- ✅ Use with explicit written permission
- ✅ Use in authorized bug bounty programs
- ✅ Use in educational environments
- ❌ Do NOT use on unauthorized networks
- ❌ Do NOT use for malicious purposes
- ❌ Do NOT use to violate privacy or computer crime laws

Unauthorized scanning may violate laws in your jurisdiction. Always obtain proper authorization before testing.

## 🚀 Features

### Core Capabilities
- **ARP Network Discovery**: Fast layer-2 host discovery
- **Multi-threaded Nmap Integration**: Parallel scanning for efficiency
- **Vulnerability Detection**: Automatic CVE identification
- **Service Fingerprinting**: Detailed service version detection
- **OS Detection**: Operating system identification
- **Credential Testing**: Optional brute-force capability

### Advanced Firewall Bypass Techniques 🔥
- **Source Port Manipulation**: Bypass firewalls by using trusted ports (DNS-53, HTTP-80, HTTPS-443)
- **Packet Fragmentation**: Split packets to evade signature detection (Linux only)
- **Decoy Scanning**: Use fake source IPs to confuse IDS/IPS systems
- **Multiple Scan Techniques**: SYN, FIN, NULL, XMAS scans with automatic fallback
- **MTU Manipulation**: Vary packet sizes to avoid pattern detection
- **Data Length Randomization**: Make each packet unique
- **Timing Control**: Adjust scan speed to avoid rate-based detection
- **TTL Manipulation**: Modify Time-To-Live values
- **MAC Spoofing**: Impersonate other devices (Linux only)
- **IPv6 Fallback**: Automatically try IPv6 when IPv4 fails

### Intelligent Features
- **Adaptive Retry Logic**: Automatically retries failed scans with different techniques
- **Configuration Presets**: Pre-configured profiles for different scenarios
- **Comprehensive Logging**: Detailed logs for analysis
- **Multiple Output Formats**: JSON and CSV export
- **Traffic Analysis Integration**: Optional Wireshark/tshark integration

## 📦 Installation

### Quick Start (Linux/macOS)
```bash
# Clone the repository
git clone https://github.com/isa-aldoy/wire-py.git
cd wire-py

# Install dependencies
pip install -r requirements.txt

# Install system requirements
# Ubuntu/Debian
sudo apt-get install nmap

# macOS
brew install nmap

# Run a basic scan (requires root)
sudo python3 rapid-scan.py 192.168.1.0/24
```

### Windows Installation
```powershell
# Run as Administrator
.\wire.ps1
```

This PowerShell script automatically:
1. Installs Python 3
2. Installs Nmap + Npcap
3. Creates virtual environment
4. Installs all dependencies
5. Runs the scanner

### Manual Installation
```bash
# Install Python dependencies
pip install python-nmap scapy mac-vendor-lookup tqdm

# Install Nmap
# Windows: Download from https://nmap.org/download.html
# Linux: sudo apt-get install nmap
# macOS: brew install nmap
```

## 🎯 Quick Start Guide

### 1. Basic Network Scan
```bash
# Scan your local network
sudo python3 rapid-scan.py

# Scan specific network
sudo python3 rapid-scan.py 192.168.1.0/24

# Scan single host
sudo python3 rapid-scan.py 192.168.1.1
```

### 2. Using Configuration Presets

#### Ultra Stealth Mode (Maximum Evasion)
```bash
# Copy ultra stealth configuration
cp config_ultra_stealth.json config.json

# Run scan
sudo python3 rapid-scan.py 192.168.1.0/24
```
**Best for**: Highly secured networks, avoiding IDS/IPS detection

#### Balanced Mode (Speed + Stealth)
```bash
cp config_balanced.json config.json
sudo python3 rapid-scan.py 192.168.1.0/24
```
**Best for**: General security assessments

#### Aggressive Mode (Maximum Speed)
```bash
cp config_aggressive.json config.json
sudo python3 rapid-scan.py 192.168.1.0/24
```
**Best for**: Fast scans on less-secured networks

### 3. Quick Discovery (No root required)
```bash
python3 quick-scan.py
```

### 4. Advanced Traffic Analysis
```bash
# Captive portal detection
sudo python3 advanced-scanner.py 192.168.1.0/24 --mode captive

# Vulnerability assessment
sudo python3 advanced-scanner.py 192.168.1.0/24 --mode vuln

# Real-time monitoring
sudo python3 advanced-scanner.py 192.168.1.0/24 --mode realtime
```

## 📖 Configuration

### Key Configuration Options

#### Firewall Bypass Settings
```json
{
  "source_port": 53,           // Use DNS port (bypass many firewalls)
  "fragment_packets": true,    // Enable packet fragmentation (Linux only)
  "use_decoys": true,          // Use decoy IPs
  "decoy_count": 5,            // Number of decoy IPs
  "scan_techniques": ["syn", "fin", "null", "xmas"],  // Available techniques
  "retry_on_failure": true,    // Retry with different techniques
  "max_retries": 3,            // Maximum retry attempts
  "ipv6_fallback": true        // Try IPv6 if IPv4 fails
}
```

#### Timing and Performance
```json
{
  "scan_delay": 100,           // Delay between packets (ms)
  "max_rate": 50,              // Maximum packets per second
  "nmap_scan_timeout_per_host": 300,  // Timeout per host (seconds)
  "max_nmap_threads": 3        // Parallel scan threads
}
```

#### Advanced Evasion
```json
{
  "mtu_size": 24,              // MTU size for fragmentation
  "data_length": 25,           // Random data length
  "ttl_value": 64,             // TTL value
  "spoof_mac": "random",       // MAC address spoofing (Linux only)
  "badsum": false              // Use bad checksums for testing
}
```

## 📚 Documentation

- **[FIREWALL-BYPASS-GUIDE.md](FIREWALL-BYPASS-GUIDE.md)**: Comprehensive guide to firewall evasion techniques
- **[ADVANCED-GUIDE.md](ADVANCED-GUIDE.md)**: Advanced scanner features and traffic analysis
- **[PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)**: Complete project overview
- **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)**: Quick reference for common tasks

## 🛠️ Tools Included

### 1. rapid-scan.py
Main scanner with full firewall bypass capabilities
- Complete network reconnaissance
- Vulnerability detection
- Multiple scan techniques
- Adaptive retry logic

### 2. quick-scan.py
Fast ARP-based discovery
- No Nmap required
- Works with firewalls
- Quick host enumeration

### 3. advanced-scanner.py
Traffic analysis and correlation
- Packet capture integration
- Captive portal detection
- Real-time monitoring
- Wireshark correlation

## 📊 Output Examples

### Console Output
```
[*] Starting network scan...
[*] Scanning 192.168.1.0/24 for open ports...
  [+] 192.168.1.1:80/tcp (open) http - nginx 1.18.0
  [+] 192.168.1.1:443/tcp (open) https - nginx 1.18.0
  [!] VULNERABLE: 192.168.1.1:80 - http nginx 1.18.0
  [!] Retry 1/3 for 192.168.1.100 using FIN scan...
  [+] Retry successful with FIN scan for 192.168.1.100
```

### JSON Output
```json
{
  "ip": "192.168.1.1",
  "mac": "aa:bb:cc:dd:ee:ff",
  "vendor": "Cisco Systems",
  "hostname": "router.local",
  "state": "up",
  "os": "Linux 5.x",
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

## 🎓 Use Cases

### Penetration Testing
- Authorized security assessments
- Red team operations
- Vulnerability assessments
- Network mapping

### IT Security
- Asset discovery
- Security auditing
- Compliance verification
- Network monitoring

### Education
- Learning network protocols
- Understanding firewall evasion
- Security research
- Cybersecurity training

## ⚙️ System Requirements

- **Python**: 3.8 or higher
- **Nmap**: 7.80 or higher
- **Privileges**: Root/Administrator for packet capture
- **RAM**: 512MB minimum, 2GB recommended
- **Disk**: 100MB for installation, more for logs/captures

### Platform-Specific Features

| Feature | Linux | Windows | macOS |
|---------|-------|---------|-------|
| Packet Fragmentation | ✅ | ❌ | ✅ |
| MAC Spoofing | ✅ | ❌ | ✅ |
| Decoy Scanning | ✅ | ✅ | ✅ |
| Source Port Manipulation | ✅ | ✅ | ✅ |
| IPv6 Fallback | ✅ | ✅ | ✅ |

## 🔧 Troubleshooting

### Permission Denied
```bash
# Linux/macOS: Run with sudo
sudo python3 rapid-scan.py

# Windows: Run PowerShell as Administrator
```

### Nmap Not Found
```bash
# Check if Nmap is installed
nmap --version

# Install if missing
# Linux: sudo apt-get install nmap
# macOS: brew install nmap
# Windows: Download from nmap.org
```

### Slow Scans
- Reduce `scan_delay`
- Increase `max_rate`
- Use fewer decoys
- Disable retries temporarily

### No Results
- Verify network connectivity
- Check firewall rules on scanning host
- Try different scan techniques
- Use IPv6 fallback
- Check target is actually online

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Credits

Built with:
- [Python 3](https://www.python.org/)
- [Nmap](https://nmap.org/)
- [Scapy](https://scapy.net/)
- [Wireshark](https://www.wireshark.org/)

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check documentation in `/docs`
- Review logs in `network_scanner_*.log`

## 🔒 Security

If you discover a security vulnerability, please report it responsibly:
- Do not open a public issue
- Contact the maintainers directly
- Allow time for a fix before disclosure

---

**Remember**: Always use this tool ethically and legally. Obtain proper authorization before scanning any network.

Made with ❤️ for the security community
