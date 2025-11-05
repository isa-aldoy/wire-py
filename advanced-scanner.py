#!/usr/bin/env python3
"""
Advanced Network Security Scanner with Traffic Analysis Integration
Combines Nmap scanning with packet capture and anomaly detection
"""
import nmap
import subprocess
import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

# --- Configuration ---
CAPTURE_DIR = "traffic_captures"
ANALYSIS_DIR = "analysis_results"

class AdvancedNetworkScanner:
    def __init__(self, target_network):
        self.target_network = target_network
        self.nm = nmap.PortScanner()
        self.open_ports = {}
        self.vulnerable_services = []
        self.capture_processes = []
        
        # Create output directories
        os.makedirs(CAPTURE_DIR, exist_ok=True)
        os.makedirs(ANALYSIS_DIR, exist_ok=True)
    
    def scan_for_open_ports(self):
        """Comprehensive port scan to identify all open ports"""
        print(f"\n[*] Scanning {self.target_network} for open ports...")
        try:
            # Fast scan of top 1000 ports
            self.nm.scan(hosts=self.target_network, arguments='-F -T4')
            
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    self.open_ports[host] = []
                    for proto in self.nm[host].all_protocols():
                        ports = self.nm[host][proto].keys()
                        for port in ports:
                            if self.nm[host][proto][port]['state'] == 'open':
                                service = self.nm[host][proto][port]['name']
                                self.open_ports[host].append({
                                    'port': port,
                                    'protocol': proto,
                                    'service': service
                                })
                                print(f"  [+] {host}:{port}/{proto} - {service}")
            
            # Save results
            with open(f"{ANALYSIS_DIR}/open_ports.json", 'w') as f:
                json.dump(self.open_ports, f, indent=2)
                
            return self.open_ports
        except Exception as e:
            print(f"[!] Error during port scan: {e}")
            return {}
    
    def detect_vulnerable_services(self):
        """Service version detection to identify potential vulnerabilities"""
        print(f"\n[*] Detecting service versions and vulnerabilities...")
        try:
            # Service and version detection with vulnerability scripts
            self.nm.scan(hosts=self.target_network, 
                        arguments='-sV --script=vuln,default -T4')
            
            for host in self.nm.all_hosts():
                for proto in self.nm[host].all_protocols():
                    ports = self.nm[host][proto].keys()
                    for port in ports:
                        port_info = self.nm[host][proto][port]
                        service_info = {
                            'host': host,
                            'port': port,
                            'protocol': proto,
                            'service': port_info.get('name', 'unknown'),
                            'product': port_info.get('product', ''),
                            'version': port_info.get('version', ''),
                            'extrainfo': port_info.get('extrainfo', ''),
                            'cpe': port_info.get('cpe', ''),
                            'scripts': {}
                        }
                        
                        # Check for vulnerability script results
                        if 'script' in port_info:
                            service_info['scripts'] = port_info['script']
                            # Flag as vulnerable if scripts found issues
                            if any('VULNERABLE' in str(v) or 'CVE' in str(v) 
                                  for v in port_info['script'].values()):
                                service_info['vulnerable'] = True
                                self.vulnerable_services.append(service_info)
                                print(f"  [!] VULNERABLE: {host}:{port} - {service_info['service']} {service_info['version']}")
            
            # Save vulnerable services
            with open(f"{ANALYSIS_DIR}/vulnerable_services.json", 'w') as f:
                json.dump(self.vulnerable_services, f, indent=2)
            
            return self.vulnerable_services
        except Exception as e:
            print(f"[!] Error during vulnerability detection: {e}")
            return []
    
    def start_traffic_capture(self, host, port, protocol='tcp', duration=60):
        """Start tcpdump/tshark capture on specific host:port"""
        print(f"\n[*] Starting traffic capture for {host}:{port}/{protocol}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        capture_file = f"{CAPTURE_DIR}/capture_{host}_{port}_{timestamp}.pcap"
        
        # Use tshark (Wireshark CLI) if available, fallback to tcpdump
        try:
            # Check if tshark is available
            subprocess.run(['tshark', '--version'], capture_output=True, check=True)
            capture_cmd = [
                'tshark',
                '-i', 'any',  # Capture on all interfaces
                '-f', f'host {host} and {protocol} port {port}',
                '-w', capture_file,
                '-a', f'duration:{duration}'  # Auto-stop after duration
            ]
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to tcpdump
            capture_cmd = [
                'tcpdump',
                '-i', 'any',
                '-w', capture_file,
                f'host {host} and {protocol} port {port}'
            ]
        
        try:
            # Start capture in background
            process = subprocess.Popen(capture_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.capture_processes.append(process)
            print(f"  [+] Capture started: {capture_file}")
            return capture_file
        except Exception as e:
            print(f"  [!] Could not start capture: {e}")
            print(f"  [!] Note: Packet capture requires root/admin privileges and tshark/tcpdump installed")
            return None
    
    def automated_captive_portal_detection(self):
        """
        1. Automate Captive Portal Detection
        Scan for open ports, capture traffic, analyze for captive portals
        """
        print("\n" + "="*60)
        print("AUTOMATED CAPTIVE PORTAL DETECTION")
        print("="*60)
        
        # Scan for open ports
        open_ports = self.scan_for_open_ports()
        
        # Focus on HTTP/HTTPS ports (common for captive portals)
        captive_portal_ports = [80, 443, 8080, 8443]
        
        for host, ports_list in open_ports.items():
            for port_info in ports_list:
                port = port_info['port']
                if port in captive_portal_ports:
                    print(f"\n[*] Potential captive portal endpoint: {host}:{port}")
                    # Start traffic capture
                    capture_file = self.start_traffic_capture(host, port, duration=30)
                    
                    # Analyze for captive portal indicators
                    if capture_file:
                        time.sleep(35)  # Wait for capture to complete
                        self.analyze_captive_portal_traffic(capture_file, host, port)
    
    def analyze_captive_portal_traffic(self, capture_file, host, port):
        """Analyze captured traffic for captive portal indicators"""
        print(f"\n[*] Analyzing {capture_file} for captive portal indicators...")
        
        try:
            # Use tshark to analyze the capture
            cmd = [
                'tshark',
                '-r', capture_file,
                '-Y', 'http.request or http.response',
                '-T', 'fields',
                '-e', 'http.host',
                '-e', 'http.request.uri',
                '-e', 'http.response.code'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Look for redirect indicators (302, 307) or captive portal keywords
            if '302' in result.stdout or '307' in result.stdout:
                print(f"  [!] CAPTIVE PORTAL DETECTED: {host}:{port}")
                print(f"      Found HTTP redirects - likely captive portal")
            
            if any(keyword in result.stdout.lower() for keyword in 
                   ['login', 'portal', 'welcome', 'captive', 'authenticate']):
                print(f"  [!] CAPTIVE PORTAL DETECTED: {host}:{port}")
                print(f"      Found captive portal keywords in HTTP traffic")
                
        except Exception as e:
            print(f"  [!] Analysis failed: {e}")
    
    def protocol_deep_dive(self, host, port, protocol='tcp'):
        """
        2. Enhance Vulnerability Assessment with Protocol Deep Dive
        Deep analysis of specific protocols
        """
        print(f"\n[*] Starting protocol deep dive for {host}:{port}/{protocol}")
        
        # Start extended capture
        capture_file = self.start_traffic_capture(host, port, protocol, duration=120)
        
        if not capture_file:
            return
        
        print(f"  [*] Capturing traffic for 2 minutes...")
        print(f"  [*] Analyze manually with: tshark -r {capture_file}")
        
        # Wait for capture
        time.sleep(125)
        
        # Basic protocol analysis
        self.analyze_protocol_specifics(capture_file, port)
    
    def analyze_protocol_specifics(self, capture_file, port):
        """Analyze protocol-specific details"""
        print(f"\n[*] Analyzing protocol details from {capture_file}...")
        
        try:
            # Determine protocol based on port
            if port == 80:
                # HTTP analysis
                cmd = ['tshark', '-r', capture_file, '-Y', 'http', '-V']
            elif port == 443:
                # HTTPS/TLS analysis
                cmd = ['tshark', '-r', capture_file, '-Y', 'tls', '-V']
            elif port in [20, 21]:
                # FTP analysis
                cmd = ['tshark', '-r', capture_file, '-Y', 'ftp', '-V']
            else:
                # Generic TCP/UDP analysis
                cmd = ['tshark', '-r', capture_file, '-V']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Save detailed analysis
            analysis_file = f"{ANALYSIS_DIR}/protocol_analysis_{port}.txt"
            with open(analysis_file, 'w') as f:
                f.write(result.stdout)
            
            print(f"  [+] Detailed analysis saved to: {analysis_file}")
            
        except Exception as e:
            print(f"  [!] Protocol analysis failed: {e}")
    
    def realtime_anomaly_detection(self, duration=300):
        """
        3. Real-Time Anomaly Detection
        Continuous monitoring with periodic scans
        """
        print("\n" + "="*60)
        print("REAL-TIME ANOMALY DETECTION")
        print(f"Monitoring for {duration} seconds...")
        print("="*60)
        
        # Start continuous capture
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        realtime_capture = f"{CAPTURE_DIR}/realtime_{timestamp}.pcap"
        
        capture_cmd = ['tshark', '-i', 'any', '-w', realtime_capture]
        
        try:
            capture_process = subprocess.Popen(capture_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[+] Continuous capture started: {realtime_capture}")
        except Exception as e:
            print(f"[!] Could not start continuous capture: {e}")
            return
        
        # Periodic scans
        scan_interval = 60  # Scan every 60 seconds
        end_time = time.time() + duration
        baseline_hosts = set()
        
        while time.time() < end_time:
            # Quick ping scan
            print(f"\n[*] Periodic scan at {datetime.now().strftime('%H:%M:%S')}")
            self.nm.scan(hosts=self.target_network, arguments='-sn')
            
            current_hosts = set(self.nm.all_hosts())
            
            # Detect new hosts (anomaly)
            new_hosts = current_hosts - baseline_hosts
            if new_hosts:
                print(f"  [!] ANOMALY: New hosts detected: {', '.join(new_hosts)}")
            
            # Detect disappeared hosts (anomaly)
            missing_hosts = baseline_hosts - current_hosts
            if missing_hosts:
                print(f"  [!] ANOMALY: Hosts disappeared: {', '.join(missing_hosts)}")
            
            baseline_hosts = current_hosts
            time.sleep(scan_interval)
        
        # Stop capture
        capture_process.terminate()
        print(f"\n[+] Real-time monitoring complete. Capture saved to: {realtime_capture}")
    
    def correlate_nmap_wireshark(self):
        """
        5. Correlate Nmap and Wireshark Data for Threat Hunting
        """
        print("\n" + "="*60)
        print("CORRELATING NMAP AND TRAFFIC CAPTURE DATA")
        print("="*60)
        
        # Full Nmap scan
        print("[*] Running comprehensive Nmap scan...")
        self.nm.scan(hosts=self.target_network, arguments='-A -T4 -oX nmap_results.xml')
        
        # Start network-wide capture
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        network_capture = f"{CAPTURE_DIR}/network_full_{timestamp}.pcap"
        
        print(f"[*] Starting network-wide capture: {network_capture}")
        capture_cmd = ['tshark', '-i', 'any', '-w', network_capture, '-a', 'duration:120']
        
        try:
            subprocess.run(capture_cmd, timeout=125)
        except Exception as e:
            print(f"[!] Capture error: {e}")
            return
        
        # Correlate data
        print("\n[*] Correlating Nmap results with traffic captures...")
        for host in self.nm.all_hosts():
            output_file = f"{CAPTURE_DIR}/correlated_{host}.pcap"
            
            try:
                # Extract traffic for each scanned host
                cmd = [
                    'tshark',
                    '-r', network_capture,
                    '-Y', f'ip.addr == {host}',
                    '-w', output_file
                ]
                subprocess.run(cmd, check=True, timeout=30)
                
                # Get packet count
                count_cmd = ['tshark', '-r', output_file, '-q', '-z', 'io,stat,0']
                result = subprocess.run(count_cmd, capture_output=True, text=True)
                
                print(f"  [+] {host}: Correlated traffic saved to {output_file}")
                
            except Exception as e:
                print(f"  [!] Correlation failed for {host}: {e}")
    
    def cleanup(self):
        """Stop all capture processes"""
        for process in self.capture_processes:
            try:
                process.terminate()
            except:
                pass

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Network Security Scanner')
    parser.add_argument('target', help='Target network (e.g., 192.168.1.0/24)')
    parser.add_argument('--mode', choices=['captive', 'vuln', 'realtime', 'correlate', 'all'],
                       default='all', help='Scanning mode')
    
    args = parser.parse_args()
    
    scanner = AdvancedNetworkScanner(args.target)
    
    try:
        if args.mode == 'captive' or args.mode == 'all':
            scanner.automated_captive_portal_detection()
        
        if args.mode == 'vuln' or args.mode == 'all':
            scanner.detect_vulnerable_services()
        
        if args.mode == 'realtime':
            scanner.realtime_anomaly_detection(duration=300)
        
        if args.mode == 'correlate' or args.mode == 'all':
            scanner.correlate_nmap_wireshark()
            
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
    finally:
        scanner.cleanup()
        print("\n[+] Scan complete. Check the following directories:")
        print(f"    - Traffic captures: {CAPTURE_DIR}/")
        print(f"    - Analysis results: {ANALYSIS_DIR}/")

if __name__ == "__main__":
    main()
