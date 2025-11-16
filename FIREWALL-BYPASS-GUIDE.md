# Advanced Firewall Bypass Techniques Guide

## Overview
This guide explains the advanced firewall evasion and bypass techniques implemented in wire-py network scanner. These features help security professionals conduct authorized penetration tests and security audits when faced with restrictive firewalls and intrusion detection systems.

⚠️ **LEGAL WARNING**: These techniques should ONLY be used on networks you own or have explicit written authorization to test. Unauthorized scanning may violate computer crime laws.

## Table of Contents
1. [Configuration Presets](#configuration-presets)
2. [Firewall Bypass Techniques](#firewall-bypass-techniques)
3. [Scan Technique Variations](#scan-technique-variations)
4. [Adaptive Retry Logic](#adaptive-retry-logic)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Configuration Presets

Wire-py now includes three configuration presets optimized for different scenarios:

### 1. Ultra Stealth Mode (`config_ultra_stealth.json`)
**Best for**: Highly secured networks, avoiding IDS/IPS detection
```bash
cp config_ultra_stealth.json config.json
python rapid-scan.py 192.168.1.0/24
```

**Features**:
- Slowest timing (T1) - Paranoid mode
- Maximum decoys (10 fake hosts)
- Long scan delays (1000ms between packets)
- Small MTU size (24 bytes)
- Multiple retry attempts (5)
- Alternative scan techniques (NULL, FIN, XMAS)
- Source port 53 (DNS) for firewall bypass
- Limited rate (10 packets/sec)

### 2. Balanced Mode (`config_balanced.json`)
**Best for**: General security assessments with moderate stealth
```bash
cp config_balanced.json config.json
python rapid-scan.py 192.168.1.0/24
```

**Features**:
- Normal timing (T3)
- Moderate decoys (5 fake hosts)
- Reasonable scan delays (100ms)
- 3 retry attempts
- Source port manipulation
- Balanced rate (50 packets/sec)

### 3. Aggressive Mode (`config_aggressive.json`)
**Best for**: Fast scans on networks with minimal security
```bash
cp config_aggressive.json config.json
python rapid-scan.py 192.168.1.0/24
```

**Features**:
- Fast timing (T4)
- No decoys (maximum speed)
- No artificial delays
- All vulnerability scripts enabled
- Brute force testing enabled
- Minimal retries

## Firewall Bypass Techniques

### 1. Source Port Manipulation
Many firewalls allow traffic from trusted ports (DNS-53, HTTP-80, HTTPS-443).

**Configuration**:
```json
"source_port": 53
```

**How it works**: Packets appear to originate from port 53 (DNS), which many firewalls allow by default.

### 2. Packet Fragmentation
Splits packets into small fragments to evade signature-based detection.

**Configuration**:
```json
"fragment_packets": true,
"mtu_size": 24
```

**Note**: Only works on Linux/BSD systems. Windows does not support this feature.

### 3. Decoy Scanning
Creates fake source IPs to confuse IDS/IPS systems.

**Configuration**:
```json
"use_decoys": true,
"decoy_count": 10
```

**How it works**: Real scan packets are mixed with packets from fake IPs, making it difficult to identify the actual scanner.

### 4. Data Length Randomization
Adds random data to packets to avoid pattern matching.

**Configuration**:
```json
"data_length": 25
```

**How it works**: Appends random bytes to packets, making each packet unique.

### 5. Timing Manipulation
Controls packet rate to avoid triggering rate-based detection.

**Configuration**:
```json
"scan_delay": 1000,
"max_rate": 10
```

**How it works**: 
- `scan_delay`: Milliseconds between each probe
- `max_rate`: Maximum packets per second

### 6. TTL Manipulation
Modifies Time-To-Live values to potentially bypass certain firewalls.

**Configuration**:
```json
"ttl_value": 64
```

### 7. MAC Address Spoofing (Linux only)
Changes the source MAC address to impersonate another device.

**Configuration**:
```json
"spoof_mac": "00:11:22:33:44:55"
```

**Options**:
- Specific MAC: `"00:11:22:33:44:55"`
- Random MAC: `"random"`
- Vendor MAC: `"Dell"`, `"Cisco"`, etc.

### 8. Bad Checksum Testing
Sends packets with invalid checksums to detect firewall presence.

**Configuration**:
```json
"badsum": true
```

**How it works**: Real hosts drop bad checksum packets, but some firewalls respond, revealing their presence.

## Scan Technique Variations

Wire-py implements multiple TCP scan techniques that behave differently with firewalls:

### 1. SYN Scan (Default)
- **Flag**: `-sS`
- **Description**: Half-open scan, doesn't complete TCP handshake
- **Stealth**: High
- **Speed**: Fast
- **Detection**: Moderate

### 2. FIN Scan
- **Flag**: `-sF`
- **Description**: Sends FIN packets to closed ports
- **Stealth**: Very High
- **Speed**: Slow
- **Detection**: Low
- **Best for**: Stateful firewalls that only track SYN packets

### 3. NULL Scan
- **Flag**: `-sN`
- **Description**: Sends packets with no flags set
- **Stealth**: Very High
- **Speed**: Slow
- **Detection**: Low
- **Best for**: Firewalls that filter specific flag combinations

### 4. XMAS Scan
- **Flag**: `-sX`
- **Description**: Sends packets with FIN, PSH, and URG flags
- **Stealth**: Very High
- **Speed**: Slow
- **Detection**: Low
- **Best for**: Evading simple packet filters

## Adaptive Retry Logic

When a scan fails, wire-py automatically retries using different techniques:

**Configuration**:
```json
"retry_on_failure": true,
"max_retries": 3,
"scan_techniques": ["syn", "fin", "null", "xmas"]
```

**Retry Sequence**:
1. **Attempt 1**: SYN scan with source port 53 (DNS)
2. **Attempt 2**: FIN scan with source port 80 (HTTP)
3. **Attempt 3**: NULL scan with source port 443 (HTTPS)
4. **Fallback**: Simple host discovery (`-sn`)
5. **Final Fallback**: IPv6 scan (if enabled)

## IPv6 Fallback

Many firewalls focus on IPv4 and have weaker IPv6 rules.

**Configuration**:
```json
"ipv6_fallback": true
```

**How it works**: If all IPv4 scans fail, the scanner attempts an IPv6 scan automatically.

## Best Practices

### 1. Start Conservative
Begin with ultra stealth mode and gradually increase aggressiveness:
```bash
# Start ultra stealth
cp config_ultra_stealth.json config.json
python rapid-scan.py <target>

# If successful, try balanced
cp config_balanced.json config.json
python rapid-scan.py <target>
```

### 2. Monitor Network Impact
- Watch for packet loss
- Check for IDS/IPS alerts (if you have access)
- Monitor scan duration
- Verify results accuracy

### 3. Combine Techniques
Use multiple bypass methods together for best results:
```json
{
  "source_port": 53,
  "fragment_packets": true,
  "use_decoys": true,
  "scan_delay": 500,
  "max_rate": 25,
  "retry_on_failure": true
}
```

### 4. Timing Adjustments
Match your scan timing to network characteristics:
- **Fast internal networks**: T3-T4, lower delays
- **Internet targets**: T2-T3, moderate delays
- **Highly secured networks**: T1-T2, high delays

### 5. Document Everything
Keep records of:
- Configuration used
- Scan timestamps
- Results obtained
- Any anomalies detected

## Troubleshooting

### Issue: All scans failing
**Solutions**:
1. Verify network connectivity
2. Check if Nmap is installed: `nmap --version`
3. Ensure you have root/admin privileges
4. Try simpler scan: `nmap -sn -Pn <target>`

### Issue: Slow scan performance
**Solutions**:
1. Reduce `scan_delay`
2. Increase `max_rate`
3. Decrease `decoy_count`
4. Use faster timing template (T3 or T4)
5. Reduce `max_retries`

### Issue: Fragmentation errors on Windows
**Solution**: Fragmentation only works on Linux/BSD. The scanner automatically detects Windows and disables fragmentation.

### Issue: MAC spoofing not working
**Solution**: MAC spoofing requires Linux and root privileges. Not supported on Windows.

### Issue: Too many IDS alerts
**Solutions**:
1. Increase `scan_delay` to 1000+
2. Use slower timing (T1 or T2)
3. Reduce `max_rate`
4. Use NULL or FIN scans instead of SYN
5. Increase decoys
6. Scan during business hours (less suspicious)

### Issue: No results despite host being up
**Possible causes**:
1. Host has very aggressive firewall
2. IDS/IPS is blocking your IP
3. All ports are actually closed
4. Target is using non-standard ports

**Solutions**:
1. Try IPv6 fallback
2. Use source port 53 or 80
3. Try UDP scan: `-sU`
4. Scan specific known-open port
5. Verify with manual connection test

## Advanced Tips

### 1. Custom Port Ranges
Focus on specific ports to reduce detection:
```bash
# Modify rapid-scan.py to scan only specific ports
# Add to nmap arguments: -p 80,443,8080,8443
```

### 2. Idle/Zombie Scan (Manual)
Use a "zombie" host for ultimate stealth:
```bash
nmap -sI <zombie_host> <target>
```

### 3. Timing Templates
Nmap timing options:
- **T0 (Paranoid)**: 5 minutes between packets
- **T1 (Sneaky)**: 15 seconds between packets
- **T2 (Polite)**: 0.4 seconds between packets
- **T3 (Normal)**: Default timing
- **T4 (Aggressive)**: Fast scan
- **T5 (Insane)**: Very fast, may miss results

### 4. Protocol-Specific Bypass
Some firewalls have weaker rules for specific protocols:
- Try UDP instead of TCP: `-sU`
- Try SCTP: `-sY`
- Try IP protocol scan: `-sO`

### 5. Application-Layer Bypass
If network-layer scans fail, try application-layer:
- HTTP banner grabbing
- HTTPS certificate inspection
- DNS queries
- SNMP enumeration

## Security Considerations

### Ethical Use Only
- ✅ Own networks
- ✅ Client networks with written permission
- ✅ Bug bounty programs (within scope)
- ✅ Educational labs
- ❌ Unauthorized networks
- ❌ Without explicit permission
- ❌ To harm or disrupt services

### Legal Compliance
Different jurisdictions have different laws. Common regulations:
- **USA**: Computer Fraud and Abuse Act (CFAA)
- **EU**: General Data Protection Regulation (GDPR)
- **UK**: Computer Misuse Act
- **Canada**: Criminal Code Section 342.1

### Minimize Impact
- Use appropriate timing
- Scan during maintenance windows
- Limit thread count
- Monitor resource usage
- Have rollback plan

## References

- [Nmap Reference Guide](https://nmap.org/book/man.html)
- [Nmap Timing and Performance](https://nmap.org/book/man-performance.html)
- [Firewall Evasion Techniques](https://nmap.org/book/firewall-subversion.html)
- [IDS/IPS Evasion](https://nmap.org/book/idps-evasion.html)

## Support

For issues or questions:
- Check logs: `network_scanner_*.log`
- Review Nmap documentation
- Test with simpler scans first
- Verify network connectivity
- Ensure proper privileges

---

**Remember**: With great power comes great responsibility. Use these techniques ethically and legally.
