# Advanced Network Security Scanner - User Guide

## Overview
This advanced scanner integrates Nmap with Wireshark/tshark for comprehensive network security analysis, implementing 5 advanced techniques:

1. **Automated Captive Portal Detection**
2. **Vulnerability Assessment with Protocol Deep Dive**
3. **Real-Time Anomaly Detection**
4. **Post-Exploitation Traffic Analysis** (simulation mode)
5. **Correlated Nmap-Wireshark Threat Hunting**

## Prerequisites

### Required Tools
```bash
# Windows (with administrator/elevated privileges)
winget install Nmap.Nmap
winget install WiresharkFoundation.Wireshark

# Linux
sudo apt-get install nmap wireshark tshark tcpdump

# Verify installation
nmap --version
tshark --version
```

### Python Dependencies
```bash
pip install -r requirements-advanced.txt
```

## Usage Examples

### 1. Automated Captive Portal Detection
Scans network for HTTP/HTTPS services and analyzes traffic for captive portal redirects:

```bash
python advanced-scanner.py 192.168.100.0/24 --mode captive
```

**What it does:**
- Scans for open ports 80, 443, 8080, 8443
- Captures HTTP traffic automatically
- Detects 302/307 redirects (captive portal indicators)
- Identifies login/authentication pages

### 2. Vulnerability Assessment with Protocol Deep Dive
Identifies vulnerable services and performs deep protocol analysis:

```bash
python advanced-scanner.py 192.168.100.0/24 --mode vuln
```

**What it does:**
- Runs Nmap with `-sV` and vulnerability scripts
- Identifies services with known CVEs
- Captures traffic on vulnerable ports
- Performs protocol-specific analysis (HTTP, FTP, SMB, etc.)

### 3. Real-Time Anomaly Detection
Continuous monitoring with periodic scans to detect network changes:

```bash
python advanced-scanner.py 192.168.100.0/24 --mode realtime
```

**What it does:**
- Starts continuous packet capture
- Performs ping scans every 60 seconds
- Detects new hosts appearing on network (anomaly)
- Detects hosts disappearing (anomaly)
- Runs for 5 minutes (configurable)

### 4. Correlated Nmap-Wireshark Analysis
Combines Nmap scan results with traffic captures for each host:

```bash
python advanced-scanner.py 192.168.100.0/24 --mode correlate
```

**What it does:**
- Runs comprehensive Nmap scan (`-A`)
- Captures all network traffic simultaneously
- Creates per-host packet captures
- Correlates scan results with actual traffic patterns
- Saves results to separate files per host

### 5. Full Scan (All Modes)
Runs all analysis modes in sequence:

```bash
python advanced-scanner.py 192.168.100.0/24 --mode all
```

## Output Files

### Traffic Captures (`traffic_captures/`)
- `capture_<host>_<port>_<timestamp>.pcap` - Per-host/port captures
- `realtime_<timestamp>.pcap` - Real-time monitoring captures
- `network_full_<timestamp>.pcap` - Full network captures
- `correlated_<host>.pcap` - Per-host correlated captures

### Analysis Results (`analysis_results/`)
- `open_ports.json` - All discovered open ports
- `vulnerable_services.json` - Services with detected vulnerabilities
- `protocol_analysis_<port>.txt` - Detailed protocol breakdowns

## Analyzing Captures with Wireshark

### Open in Wireshark GUI:
```bash
wireshark traffic_captures/capture_192.168.100.1_80_*.pcap
```

### Command-line analysis with tshark:
```bash
# View HTTP requests
tshark -r capture.pcap -Y "http.request" -T fields -e http.host -e http.request.uri

# View DNS queries
tshark -r capture.pcap -Y "dns.qry.name" -T fields -e dns.qry.name

# Extract files from HTTP
tshark -r capture.pcap --export-objects http,extracted_files/

# Statistics
tshark -r capture.pcap -q -z io,stat,1
```

## Security Considerations

⚠️ **Important Warnings:**

1. **Legal Authorization Required**
   - Only scan networks you own or have written permission to test
   - Unauthorized scanning may violate computer crime laws
   - Some techniques may trigger IDS/IPS alerts

2. **Packet Capture Requires Privileges**
   - Run with administrator/root privileges
   - Windows: Run PowerShell as Administrator
   - Linux: Use `sudo` or configure capabilities

3. **Performance Impact**
   - Aggressive scanning can impact network performance
   - Continuous packet capture uses disk space quickly
   - Monitor system resources during scans

4. **Privacy**
   - Captured packets may contain sensitive data
   - Secure captured .pcap files appropriately
   - Delete captures after analysis

## Troubleshooting

### "tshark not found"
- Install Wireshark (includes tshark)
- Add tshark to PATH:
  - Windows: `C:\Program Files\Wireshark`
  - Linux: Usually in `/usr/bin/tshark`

### "Permission denied" when capturing
- Windows: Run as Administrator
- Linux: `sudo` or add user to wireshark group

### "No traffic captured"
- Verify network interface name (`tshark -D` to list)
- Check firewall isn't blocking traffic
- Ensure target hosts are actually communicating

### Nmap scan returns no results
- Hosts may have firewalls blocking scans
- Try less aggressive timing (`-T2` instead of `-T4`)
- Use decoy scanning (`-D RND:10`)

## Advanced Usage

### Custom Capture Duration
Edit `advanced-scanner.py` and modify:
```python
duration=120  # Capture for 120 seconds
```

### Target Specific Ports
Modify the scan in the script:
```python
self.nm.scan(hosts=target, arguments='-p 80,443,8080,8443')
```

### Filter Traffic by Protocol
When analyzing, use tshark filters:
```bash
tshark -r capture.pcap -Y "tcp.port == 80 or tcp.port == 443"
```

## Integration with Other Tools

### Export to SIEM
```bash
# Convert pcap to JSON for SIEM ingestion
tshark -r capture.pcap -T json > events.json
```

### Create Custom Reports
```python
import json

with open('analysis_results/vulnerable_services.json') as f:
    vulns = json.load(f)
    
for vuln in vulns:
    print(f"ALERT: {vuln['host']}:{vuln['port']} - {vuln['service']}")
```

## Example Workflow

Complete network security assessment:

```bash
# 1. Quick discovery
python quick-scan.py

# 2. Detailed vulnerability scan
python advanced-scanner.py 192.168.100.0/24 --mode vuln

# 3. Start real-time monitoring
python advanced-scanner.py 192.168.100.0/24 --mode realtime &

# 4. Correlate with traffic
python advanced-scanner.py 192.168.100.0/24 --mode correlate

# 5. Analyze results
wireshark traffic_captures/correlated_192.168.100.1.pcap
```

## Support

For issues or questions:
- Check Wireshark documentation: https://www.wireshark.org/docs/
- Nmap reference guide: https://nmap.org/book/man.html
- Scapy documentation: https://scapy.readthedocs.io/
