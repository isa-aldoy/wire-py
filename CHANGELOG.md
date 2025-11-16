# Changelog

All notable changes to Wire-Py will be documented in this file.

## [2.0.0] - 2024-11-16

### Added - Advanced Firewall Bypass Features

#### New Firewall Evasion Techniques
- **Source Port Manipulation**: Configure scanner to use trusted source ports (DNS-53, HTTP-80, HTTPS-443) that many firewalls allow by default
- **Packet Fragmentation**: Split packets into small fragments to evade signature-based detection (Linux/BSD only)
- **MTU Size Manipulation**: Vary packet sizes to avoid pattern detection
- **Data Length Randomization**: Add random data to packets making each unique
- **TTL Manipulation**: Control Time-To-Live values for potential firewall bypass
- **MAC Address Spoofing**: Impersonate other devices on the network (Linux only)
- **Bad Checksum Testing**: Send invalid checksums to detect firewall presence

#### Multiple Scan Techniques
- **SYN Scan**: Default half-open scanning (stealthy, fast)
- **FIN Scan**: Send FIN packets for stateful firewall bypass
- **NULL Scan**: Send packets with no flags for simple filter evasion
- **XMAS Scan**: Use FIN+PSH+URG flags for advanced evasion

#### Adaptive Retry Logic
- Automatic retry with different techniques when initial scan fails
- Intelligent source port rotation across retries (53→80→443)
- Up to 5 retry attempts with different scan methods
- IPv6 fallback when all IPv4 attempts fail
- Exponential backoff between retries

#### Configuration Presets
Three new pre-configured profiles for different scenarios:

1. **Ultra-Stealth Mode** (`config_ultra_stealth.json`)
   - Timing: T1 (Paranoid)
   - Decoys: 10 fake hosts
   - Scan delay: 1000ms
   - MTU: 24 bytes
   - Max retries: 5
   - Techniques: NULL, FIN, XMAS, SYN
   - Rate limit: 10 packets/sec
   - Best for: Highly secured networks, IDS/IPS evasion

2. **Balanced Mode** (`config_balanced.json`)
   - Timing: T3 (Normal)
   - Decoys: 5 fake hosts
   - Scan delay: 100ms
   - Max retries: 3
   - Techniques: SYN, FIN, NULL
   - Rate limit: 50 packets/sec
   - Best for: General security assessments

3. **Aggressive Mode** (`config_aggressive.json`)
   - Timing: T4 (Aggressive)
   - Decoys: None (maximum speed)
   - No artificial delays
   - Max retries: 2
   - Techniques: SYN only
   - No rate limit
   - Best for: Fast scans, less secured networks

#### Enhanced Configuration Options
New configuration parameters in `config.json`:
```json
{
  "source_port": 53,
  "data_length": 0,
  "mtu_size": 0,
  "scan_delay": 0,
  "max_rate": 0,
  "spoof_mac": null,
  "ttl_value": 0,
  "badsum": false,
  "scan_techniques": ["syn", "fin", "null", "xmas"],
  "ipv6_fallback": true,
  "retry_on_failure": true,
  "max_retries": 3,
  "adaptive_timing": true
}
```

#### Documentation
- **README.md**: Comprehensive project documentation with quick start guide
- **FIREWALL-BYPASS-GUIDE.md**: In-depth guide to firewall evasion techniques
  - Detailed explanation of each bypass method
  - Configuration examples
  - Best practices and tips
  - Troubleshooting guide
  - Legal and ethical guidelines
- **PROJECT-SUMMARY.md**: Updated with new features
- **CHANGELOG.md**: Version history and changes

#### Testing and Quality
- **test_config.py**: Automated validation script
  - Validates all configuration files
  - Checks Python syntax
  - Verifies required fields and types
  - Provides detailed test results
- **.gitignore**: Proper exclusion of build artifacts and logs
- **Security Scanning**: Passed CodeQL security analysis with 0 alerts

### Changed
- **rapid-scan.py**: Enhanced with advanced firewall bypass logic
  - Refactored nmap_scan function with retry mechanism
  - Added support for multiple scan techniques
  - Implemented intelligent fallback strategies
  - Added IPv6 scanning capability
  - Improved error handling and logging
  
- **config.json**: Updated with new firewall bypass parameters
- **config_stealth.json**: Updated to include new configuration fields

### Technical Improvements
- Platform-specific feature detection (Linux/Windows/macOS)
- Automatic disabling of unsupported features
- Enhanced logging with technique-specific information
- Better error messages for troubleshooting
- Improved retry logic with different scan methods per attempt

### Compatibility
- **Python**: 3.8+ (tested on 3.12)
- **Nmap**: 7.80+ required
- **Platforms**: 
  - Linux: Full feature support
  - Windows: Limited (no fragmentation or MAC spoofing)
  - macOS: Full feature support

### Security
- All code passed CodeQL security scanning
- No vulnerabilities detected
- Proper error handling to prevent information disclosure
- Secure configuration file handling

### Performance
- Configurable threading (1-5 threads)
- Rate limiting to avoid network saturation
- Adaptive timing based on network conditions
- Efficient retry mechanism with intelligent backoff

## [1.0.0] - Previous Release

### Features
- Basic ARP network discovery
- Nmap integration for port scanning
- Service version detection
- OS fingerprinting
- Basic stealth mode with decoys
- JSON and CSV export
- Vulnerability detection
- Brute-force credential testing
- Traffic analysis integration

---

## Migration Guide

### Upgrading from 1.x to 2.0

1. **Update Configuration Files**
   ```bash
   # Backup old config
   cp config.json config.json.backup
   
   # Use new default or preset
   cp config_balanced.json config.json
   ```

2. **New Required Fields**
   Add these fields to existing custom configs:
   - `source_port`
   - `scan_techniques`
   - `retry_on_failure`
   - `max_retries`
   - `ipv6_fallback`

3. **Test Configuration**
   ```bash
   python3 test_config.py
   ```

4. **Review New Features**
   - Read FIREWALL-BYPASS-GUIDE.md for technique explanations
   - Try different presets for your use case
   - Adjust timing based on your network

### Breaking Changes
None. All 1.x configurations will continue to work with default values for new fields.

---

## Future Roadmap

### Planned Features (v2.1)
- [ ] HTTP/HTTPS proxy support
- [ ] SOCKS proxy integration
- [ ] Custom TCP flag combinations
- [ ] Idle/zombie scan support
- [ ] UDP scan enhancements

### Planned Features (v3.0)
- [ ] Web GUI dashboard
- [ ] Database backend for results
- [ ] Machine learning for anomaly detection
- [ ] Automated exploit testing integration
- [ ] SIEM integration (Splunk, ELK)
- [ ] Real-time alerting (Email, Slack, Discord)

---

## Contributors
- isa-aldoy - Project creator and maintainer
- GitHub Copilot - AI-assisted development

## License
MIT License - See LICENSE file for details

## Legal Notice
This tool is for authorized security testing only. Users are responsible for obtaining proper authorization before scanning any network. Unauthorized use may violate computer crime laws in your jurisdiction.
