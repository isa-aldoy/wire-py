#!/usr/bin/env python3
"""
Quick Network Discovery - Shows what we CAN detect even with firewalls blocking Nmap
"""
from scapy.all import ARP, Ether, srp
from mac_vendor_lookup import MacLookup
import socket
import json

def get_network_devices():
    # ARP scan - this WORKS even with firewalls
    print("🔍 Scanning network with ARP...")
    arp = ARP(pdst="192.168.100.0/24")
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    result = srp(packet, timeout=5, verbose=0)[0]
    devices = []
    
    mac_lookup = MacLookup()
    
    for sent, received in result:
        try:
            hostname = socket.gethostbyaddr(received.psrc)[0]
        except:
            hostname = "Unknown"
        
        try:
            vendor = mac_lookup.lookup(received.hwsrc)
        except:
            vendor = "Unknown"
            
        devices.append({
            'ip': received.psrc,
            'mac': received.hwsrc,
            'hostname': hostname,
            'vendor': vendor,
            'status': 'up (confirmed via ARP)'
        })
    
    return devices

if __name__ == "__main__":
    devices = get_network_devices()
    
    print(f"\n✅ Found {len(devices)} devices:\n")
    for dev in devices:
        print(f"📡 {dev['ip']:15} - {dev['hostname']:30} ({dev['vendor']})")
        print(f"   MAC: {dev['mac']}")
        print()
    
    # Save to JSON
    with open("quick_scan_results.json", "w") as f:
        json.dump(devices, f, indent=2)
    
    print(f"💾 Results saved to quick_scan_results.json")
