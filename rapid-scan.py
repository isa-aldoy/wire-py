#!/usr/bin/env python3
import nmap
from scapy.all import ARP, Ether, srp # type: ignore
import ipaddress
import socket
import json
import csv
import os
import sys
from datetime import datetime
import threading
import logging
import re
import time # For threading sleep and main function
from tqdm import tqdm # For progress bar
from mac_vendor_lookup import MacLookup # MAC vendor lookup

# --- Configuration Loading ---
CONFIG = { # Default config
    "nmap_scan_mode": "stealth",
    "local_network_subnet_override": None,
    "nmap_arguments_custom": "-sS -sV -f -T2 -Pn --script=http-title,banner",
    "enable_brute_force": False,
    "brute_force_scripts": "ftp-brute,ssh-brute,telnet-brute",
    "brute_force_userdb": "users.txt",
    "brute_force_passdb": "pass.txt",
    "brute_force_stop_on_success": True,
    "nmap_scan_timeout_per_host": 300,
    "max_nmap_threads": 2,
    "log_file": "network_scanner_advanced.log",
    "log_level": "INFO",
    "use_decoys": True,
    "decoy_count": 3,
    "fragment_packets": True,
    "randomize_hosts": True,
    "credentials": {
        "ssh": { "username": "", "password": "", "key_path": "" },
        "smb": { "username": "", "password": "", "domain": "" }
    },
    "external_db_urls": {
        "nvd_cve": "https://nvd.nist.gov/vuln/detail/",
        "exploitdb_search": "https://www.exploit-db.com/search?q="
    }
}

def load_config(config_file="config.json"):
    global CONFIG
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                for key, value in user_config.items():
                    if isinstance(value, dict) and isinstance(CONFIG.get(key), dict):
                        CONFIG[key].update(value)
                    else:
                        CONFIG[key] = value
                logging.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            logging.error(f"Error loading {config_file}: {e}. Using default/current config values.")
    else:
        logging.warning(f"{config_file} not found. Using default config values and creating a default one.")
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(CONFIG, f, indent=2)
        except Exception as e:
            logging.error(f"Could not write default config file {config_file}: {e}")

# --- Logging Setup ---
def setup_logging():
    log_level_str = CONFIG.get("log_level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(CONFIG.get("log_file", "network_scanner_advanced.log"), encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    logging.getLogger("macvendors.macvendors").setLevel(logging.WARNING)

load_config()
setup_logging()

# --- Network Utilities (get_local_ip, get_network_cidr, scan_arp_network, reverse_dns, get_mac_vendor) ---
# These functions remain the same as in the previous version. For brevity, they are not repeated here.
# Ensure you have them from the previous response.

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        logging.info(f"Local IP determined: {local_ip}")
        return local_ip
    except Exception as e:
        logging.error(f"Error getting local IP: {e}. Attempting fallback.")
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if not local_ip.startswith("127."):
                 logging.info(f"Local IP (via hostname) determined: {local_ip}")
                 return local_ip
            logging.warning("Could not determine a non-loopback local IP via hostname fallback.")
        except Exception as e_fallback:
            logging.error(f"Fallback for local IP failed: {e_fallback}")
        logging.critical("Failed to determine local IP. Please specify a target network via 'local_network_subnet_override' in config.json or as a command-line argument.")
        sys.exit(1)
    finally:
        s.close()

def get_network_cidr(local_ip_address=None, target_override=None):
    if target_override:
        try:
            ipaddress.ip_network(target_override, strict=False)
            logging.info(f"Using overridden target network/IP: {target_override}")
            return target_override
        except ValueError:
            try:
                ipaddress.ip_address(target_override)
                logging.info(f"Using overridden single IP target: {target_override}")
                return f"{target_override}/32"
            except ValueError:
                logging.info(f"Target '{target_override}' appears to be a hostname. Will resolve later.")
                return target_override

    if CONFIG.get("local_network_subnet_override"):
        try:
            override_net = CONFIG["local_network_subnet_override"]
            ipaddress.ip_network(override_net, strict=False)
            logging.info(f"Using configured network CIDR override: {override_net}")
            return override_net
        except ValueError as e:
            logging.error(f"Invalid local_network_subnet_override '{CONFIG['local_network_subnet_override']}': {e}. Falling back.")

    if not local_ip_address:
        logging.error("Local IP address not provided and no override configured. Cannot determine network CIDR.")
        sys.exit(1)
    try:
        ip_net = ipaddress.ip_network(f"{local_ip_address}/24", strict=False)
        cidr = str(ip_net.supernet(new_prefix=24))
        logging.info(f"Calculated network CIDR: {cidr} (assuming /24 for local IP {local_ip_address})")
        return cidr
    except Exception as e:
        logging.error(f"Error calculating network CIDR for {local_ip_address}: {e}")
        sys.exit(1)

def scan_arp_network(network_cidr_str):
    logging.info(f"Starting ARP scan on network: {network_cidr_str}")
    try:
        target_network = ipaddress.ip_network(network_cidr_str, strict=False)
        logging.info(f"ARP scanning target network: {str(target_network)}")
    except ValueError:
        logging.error(f"ARP scan target '{network_cidr_str}' is not a valid IP network. Skipping ARP scan.")
        return []

    arp = ARP(pdst=str(target_network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    devices_found = []
    try:
        result = srp(packet, timeout=10, verbose=0, iface_hint=str(target_network.network_address))[0]
        for sent, received in result:
            devices_found.append({'ip': received.psrc, 'mac': received.hwsrc})
        logging.info(f"ARP scan complete. {len(devices_found)} devices found on {network_cidr_str}.")
    except PermissionError:
        logging.critical("ARP scan requires root/administrator privileges.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error during ARP scan on {network_cidr_str}: {e}")
    return devices_found

def reverse_dns(ip_addr):
    try:
        return socket.gethostbyaddr(ip_addr)[0]
    except socket.herror:
        return "Unknown (Reverse DNS failed)"
    except Exception as e:
        logging.warning(f"Reverse DNS lookup for {ip_addr} failed: {e}")
        return "Unknown (Error in lookup)"

def get_mac_vendor(mac_address_str):
    if not mac_address_str or mac_address_str.lower() == "n/a":
        return "N/A"
    try:
        mac_lookup = MacLookup()
        return mac_lookup.lookup(mac_address_str)
    except Exception:
        return "Unknown Vendor"

# --- Nmap Scanning and Parsing (nmap_scan, parse_nmap_results) ---
# These functions are largely the same as the previous version,
# but parse_nmap_results will be slightly modified for CVSS placeholder.
# For brevity, nmap_scan is not fully repeated here. Ensure you have it.
def nmap_scan(ip_addr):
    nm = nmap.PortScanner() # type: ignore
    nmap_base_args_str = ""
    nmap_final_scripts_to_run = set()
    nmap_final_script_args_list = []

    scan_mode = CONFIG.get("nmap_scan_mode", "stealth")

    if scan_mode == "default":
        nmap_base_args_str = "-sS -sV -O -Pn"
        nmap_final_scripts_to_run.add("banner")
    elif scan_mode == "stealth":
        # Stealth mode: SYN scan, slower timing
        # Note: Packet fragmentation (-f) only works on Linux/BSD, causes errors on Windows
        nmap_base_args_str = "-sS -sV -T2 -Pn"
        # Only add fragmentation on non-Windows systems
        if CONFIG.get("fragment_packets", False) and sys.platform.startswith('linux'):
            nmap_base_args_str += " -f"
            logging.info("Packet fragmentation enabled (Linux detected)")
        nmap_final_scripts_to_run.update(["http-title", "banner"])
    elif scan_mode == "aggressive":
        nmap_base_args_str = "-T4 -A -Pn"
        nmap_final_scripts_to_run.update(["vuln", "http-enum", "banner"]) # default is implied by -A
    elif scan_mode == "custom":
        nmap_base_args_str = CONFIG.get("nmap_arguments_custom", "-sS -sV -T2 -Pn -f --script=http-title,banner")
        if "--script=" in nmap_base_args_str:
            try:
                script_part = nmap_base_args_str.split("--script=")[1].split(" ")[0]
                nmap_final_scripts_to_run.update(s.strip() for s in script_part.split(','))
                nmap_base_args_str = re.sub(r"--script=[\w,-]+", "", nmap_base_args_str).strip()
            except IndexError:
                logging.warning("Could not parse scripts from custom Nmap arguments string.")
    else: 
        nmap_base_args_str = "-sS -sV -T2 -Pn -f"
        nmap_final_scripts_to_run.update(["http-title", "banner"])

    if CONFIG.get("enable_brute_force", False):
        brute_scripts_config_str = CONFIG.get("brute_force_scripts", "")
        if brute_scripts_config_str:
            nmap_final_scripts_to_run.update(s.strip() for s in brute_scripts_config_str.split(','))
            userdb_path = CONFIG.get("brute_force_userdb", "users.txt")
            passdb_path = CONFIG.get("brute_force_passdb", "pass.txt")
            stop_on_success = "true" if CONFIG.get("brute_force_stop_on_success", True) else "false"
            if os.path.exists(userdb_path): nmap_final_script_args_list.append(f"userdb={os.path.abspath(userdb_path)}")
            else: logging.warning(f"User wordlist '{userdb_path}' not found.")
            if os.path.exists(passdb_path): nmap_final_script_args_list.append(f"passdb={os.path.abspath(passdb_path)}")
            else: logging.warning(f"Password wordlist '{passdb_path}' not found.")
            nmap_final_script_args_list.append(f"brute.stoponfirst={stop_on_success}")
            nmap_final_script_args_list.append("brute.threads=2")

    cfg_creds = CONFIG.get("credentials", {})
    if "ssh" in cfg_creds and cfg_creds["ssh"].get("username"):
        nmap_final_script_args_list.append(f"ssh.user='{cfg_creds['ssh']['username']}'")
        if cfg_creds["ssh"].get("password"): nmap_final_script_args_list.append(f"ssh.pass='{cfg_creds['ssh']['password']}'")
        ssh_key_path = cfg_creds["ssh"].get("key_path")
        if ssh_key_path and os.path.exists(ssh_key_path):
            nmap_final_script_args_list.append(f"ssh.privatekey='{os.path.abspath(ssh_key_path)}'")

    if "smb" in cfg_creds and cfg_creds["smb"].get("username"):
        nmap_final_script_args_list.append(f"smbuser='{cfg_creds['smb']['username']}'")
        if cfg_creds["smb"].get("password"): nmap_final_script_args_list.append(f"smbpass='{cfg_creds['smb']['password']}'")
        nmap_final_script_args_list.append(f"smbdomain='{cfg_creds['smb'].get('domain', 'WORKGROUP')}'")

    nmap_command_args = nmap_base_args_str
    if nmap_final_scripts_to_run:
        nmap_command_args += f" --script={','.join(sorted(list(nmap_final_scripts_to_run)))}"
    if nmap_final_script_args_list:
        nmap_command_args += f" --script-args \"{','.join(nmap_final_script_args_list)}\""

    # Add decoy scanning for stealth
    if CONFIG.get("use_decoys", False):
        import random
        # Generate random decoy IPs from the same subnet
        try:
            target_ip = ipaddress.ip_address(ip_addr)
            network = ipaddress.ip_network(f"{target_ip}/24", strict=False)
            decoy_count = CONFIG.get("decoy_count", 3)
            decoys = []
            for _ in range(decoy_count):
                random_host = random.randint(1, 254)
                decoy_ip = str(ipaddress.ip_address(int(network.network_address) + random_host))
                if decoy_ip != ip_addr:
                    decoys.append(decoy_ip)
            if decoys:
                nmap_command_args += f" -D {','.join(decoys[:decoy_count])},ME"
                logging.info(f"Using decoys for {ip_addr}: {','.join(decoys[:decoy_count])}")
        except Exception as e:
            logging.warning(f"Could not generate decoys: {e}")

    # Add random host order for stealth
    if CONFIG.get("randomize_hosts", False):
        nmap_command_args += " --randomize-hosts"

    nmap_timeout_opt = f"--host-timeout {CONFIG.get('nmap_scan_timeout_per_host', 300)}s"
    full_nmap_args = f"{nmap_command_args.strip()} {nmap_timeout_opt}"

    logging.info(f"Nmap scanning {ip_addr} with arguments: {full_nmap_args}")
    try:
        nm.scan(hosts=ip_addr, arguments=full_nmap_args)
        if ip_addr in nm.all_hosts():
            logging.info(f"Nmap scan for {ip_addr} completed successfully - host data found")
            return nm[ip_addr]
        else:
            # Host blocking aggressive scan - try simple ping scan
            logging.warning(f"Nmap scan for {ip_addr} completed but host data not found. Trying fallback ping scan...")
            try:
                nm_fallback = nmap.PortScanner()
                nm_fallback.scan(hosts=ip_addr, arguments="-sn -Pn")  # Simple host discovery
                if ip_addr in nm_fallback.all_hosts():
                    logging.info(f"Fallback ping scan successful for {ip_addr}")
                    return nm_fallback[ip_addr]
            except Exception as fallback_err:
                logging.debug(f"Fallback scan also failed for {ip_addr}: {fallback_err}")
            
            logging.warning(f"Host {ip_addr} is likely blocking all scan attempts (firewall active)")
            return None
    except nmap.nmap.PortScannerError as e:
        logging.error(f"Nmap PortScannerError for {ip_addr}: {e}.")
        return None
    except Exception as e:
        logging.error(f"Unhandled error scanning {ip_addr} with Nmap: {e}")
        return None

def parse_nmap_results(nmap_host_data, ip_addr_str):
    if not nmap_host_data: return {}
    parsed_info = {}
    try:
        parsed_info['hostname'] = nmap_host_data.hostname() if nmap_host_data.hostname() else reverse_dns(ip_addr_str)
    except AttributeError:
        parsed_info['hostname'] = reverse_dns(ip_addr_str)
    parsed_info['state'] = nmap_host_data.state() if hasattr(nmap_host_data, 'state') else 'unknown'

    parsed_info['os_matches'] = []
    if 'osmatch' in nmap_host_data and nmap_host_data['osmatch']:
        for osmatch in nmap_host_data['osmatch']:
            os_detail = {'name': osmatch.get('name', 'N/A'), 'accuracy': osmatch.get('accuracy', 'N/A'), 'osclass': []}
            for osclass_entry in osmatch.get('osclass', []):
                os_detail['osclass'].append({
                    'type': osclass_entry.get('type', 'N/A'), 'vendor': osclass_entry.get('vendor', 'N/A'),
                    'osfamily': osclass_entry.get('osfamily', 'N/A'), 'osgen': osclass_entry.get('osgen', 'N/A'),
                    'accuracy': osclass_entry.get('accuracy', 'N/A')
                })
            parsed_info['os_matches'].append(os_detail)
        if parsed_info['os_matches'] : parsed_info['os'] = parsed_info['os_matches'][0]['name']
        else: parsed_info['os'] = "Unknown"
    else:
        parsed_info['os'] = "Unknown"

    parsed_info['ports'] = []
    parsed_info['vulnerabilities'] = []
    parsed_info['credentials_found'] = []
    parsed_info['web_enum'] = {}

    for proto in nmap_host_data.all_protocols():
        if proto not in nmap_host_data: continue
        port_keys = list(nmap_host_data[proto].keys())
        for port_num in port_keys:
            port_details = nmap_host_data[proto][port_num]
            p_info = {
                'protocol': proto, 'port': port_num, 'state': port_details.get('state', ''),
                'name': port_details.get('name', ''), 'product': port_details.get('product', ''),
                'version': port_details.get('version', ''), 'extrainfo': port_details.get('extrainfo', ''),
                'cpe': port_details.get('cpe', ''), 'scripts': {}
            }
            if 'script' in port_details:
                for script_name, script_output_raw in port_details['script'].items():
                    p_info['scripts'][script_name] = script_output_raw
                    script_output_str = str(script_output_raw)

                    if "vuln" in script_name.lower() or "exploit" in script_name.lower() or "cve-" in script_output_str.lower():
                        vuln_detail = {
                            'port': port_num, 'protocol': proto, 'script': script_name, 
                            'output': script_output_raw, 'references': [],
                            'cvss_score': "N/A (Lookup not implemented)", # Placeholder
                            'severity': "Unknown" # Placeholder
                        }
                        cve_matches = re.findall(r"CVE-\d{4}-\d{4,7}", script_output_str.upper())
                        if cve_matches:
                            ext_urls = CONFIG.get("external_db_urls", {})
                            for cve_id in set(cve_matches): # Unique CVEs
                                vuln_detail['cve_ids'] = list(set(cve_matches)) # Store CVE IDs
                                if ext_urls.get("nvd_cve"): vuln_detail['references'].append(f"{ext_urls['nvd_cve']}{cve_id}")
                                if ext_urls.get("exploitdb_search"): vuln_detail['references'].append(f"{ext_urls['exploitdb_search']}{cve_id}")
                        # Basic severity hinting based on keywords (very naive)
                        if any(kw in script_output_str.lower() for kw in ["critical", "high", "exploit", "remote code execution"]):
                            vuln_detail['severity'] = "High (keyword match)"
                        elif "medium" in script_output_str.lower():
                             vuln_detail['severity'] = "Medium (keyword match)"
                        parsed_info['vulnerabilities'].append(vuln_detail)

                    if "brute" in script_name.lower() and ("SUCCESS" in script_output_str.upper() or "VALID" in script_output_str.upper() or "Credentials:" in script_output_str):
                        if "account" in script_output_str.lower() or "credentials" in script_output_str.lower() or ":" in script_output_str:
                            parsed_info['credentials_found'].append({
                                'port': port_num, 'protocol': proto, 'service': port_details.get('name', 'N/A'),
                                'script': script_name, 'details': script_output_raw
                            })
                    if script_name == 'http-enum':
                        parsed_info['web_enum'][f"{port_num}/{proto}"] = script_output_raw
            parsed_info['ports'].append(p_info)
    return parsed_info


# --- Data Saving (save_json, save_csv) ---
# save_json remains the same. save_csv is slightly adapted for new fields.
# For brevity, save_json is not repeated. Ensure you have it.
def save_json(data_to_save, filename_str):
    try:
        with open(filename_str, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, default=str)
        logging.info(f"Results saved to JSON: {filename_str}")
    except Exception as e:
        logging.error(f"Error saving JSON file {filename_str}: {e}")

def save_csv(data_list, filename_str):
    if not data_list:
        logging.warning("No data to save to CSV.")
        return
    try:
        with open(filename_str, mode='w', newline='', encoding='utf-8') as f:
            header_fields = [
                'IP', 'MAC', 'Vendor', 'Hostname', 'State', 'Primary OS',
                'Port_Protocol', 'Port_State', 'Service_Name', 'Service_Product', 'Service_Version',
                'CVE_IDs', 'CVSS_Score', 'Severity', 'Vulnerability_Details', 'Vulnerability_References',
                'Found_Credentials_Service', 'Found_Credentials_Details',
                'Web_Enum_Port', 'Web_Enum_Details'
            ]
            writer = csv.DictWriter(f, fieldnames=header_fields, extrasaction='ignore', quoting=csv.QUOTE_ALL)
            writer.writeheader()

            for device_dict in data_list:
                base_row = {
                    'IP': device_dict.get('ip', ''), 'MAC': device_dict.get('mac', ''),
                    'Vendor': device_dict.get('vendor', ''), 'Hostname': device_dict.get('hostname', ''),
                    'State': device_dict.get('state', ''), 'Primary OS': device_dict.get('os', '')
                }

                # Handle cases where there might be multiple findings per device
                # For CSV, often best to have one primary finding type per row or aggregate
                
                # Version 1: One row per device, findings aggregated or summarized
                # This is simpler but loses some granularity in CSV if not careful
                
                row_to_write = base_row.copy()
                
                ports_summary = []
                if device_dict.get('ports'):
                    for p in device_dict['ports']:
                        ports_summary.append(f"{p.get('port')}/{p.get('protocol')} ({p.get('state')}) {p.get('name','')}-{p.get('product','')}-{p.get('version','')}")
                row_to_write['Service_Name'] = " | ".join(ports_summary) if ports_summary else "N/A"


                vuln_summary = []
                cve_ids_agg = set()
                severities_agg = set()
                cvss_agg = set() # CVSS is usually per CVE
                refs_agg = set()

                if device_dict.get('vulnerabilities'):
                    for v in device_dict['vulnerabilities']:
                        vuln_summary.append(f"Port {v.get('port')}/{v.get('protocol')} ({v.get('script')}): {str(v.get('output',''))[:100]}...")
                        if v.get('cve_ids'): cve_ids_agg.update(v['cve_ids'])
                        severities_agg.add(v.get('severity', 'Unknown'))
                        cvss_agg.add(v.get('cvss_score', 'N/A'))
                        if v.get('references'): refs_agg.update(v['references'])
                
                row_to_write['Vulnerability_Details'] = " | ".join(vuln_summary) if vuln_summary else "N/A"
                row_to_write['CVE_IDs'] = ", ".join(sorted(list(cve_ids_agg))) if cve_ids_agg else "N/A"
                row_to_write['Severity'] = ", ".join(sorted(list(severities_agg))) if severities_agg else "N/A"
                row_to_write['CVSS_Score'] = ", ".join(sorted(list(cvss_agg))) if cvss_agg else "N/A" # Needs better handling if actual scores come
                row_to_write['Vulnerability_References'] = " | ".join(sorted(list(refs_agg))) if refs_agg else "N/A"


                creds_summary = []
                if device_dict.get('credentials_found'):
                     for c in device_dict['credentials_found']:
                         creds_summary.append(f"Port {c.get('port')}/{c.get('protocol')} ({c.get('service')} via {c.get('script')}): {str(c.get('details',''))[:100]}...")
                row_to_write['Found_Credentials_Details'] = " | ".join(creds_summary) if creds_summary else "N/A"


                web_enum_summary = []
                if device_dict.get('web_enum'):
                    for port_key, enum_val in device_dict['web_enum'].items():
                        web_enum_summary.append(f"{port_key}: {str(enum_val)[:100]}...")
                row_to_write['Web_Enum_Details'] = " | ".join(web_enum_summary) if web_enum_summary else "N/A"

                writer.writerow(row_to_write)

        logging.info(f"Results saved to CSV: {filename_str}")
    except Exception as e:
        logging.error(f"Error saving CSV file {filename_str}: {e}", exc_info=True)


# --- Main Execution ---
THREAD_RESULTS_LIST = []
RESULTS_LOCK_OBJ = threading.Lock()

def scan_host_threaded_worker(device_arp_info_dict, pbar_instance=None): # Added pbar
    ip = device_arp_info_dict['ip']
    mac = device_arp_info_dict['mac']

    # Logging info moved to main loop before thread start for cleaner pbar
    vendor_str = get_mac_vendor(mac)
    host_scan_data = {
        'ip': ip, 'mac': mac, 'vendor': vendor_str,
        'hostname': reverse_dns(ip), 'state': 'up (ARP)', 'os': 'unknown', 
        'os_matches': [], 'ports': [], 'vulnerabilities': [], 
        'credentials_found': [], 'web_enum': {},
        'scan_timestamp': datetime.now().isoformat(),
        'scan_result': 'blocked_by_firewall'  # Default assumption
    }
    nmap_raw_scan_data = nmap_scan(ip)
    if nmap_raw_scan_data:
        parsed_nmap_host_info = parse_nmap_results(nmap_raw_scan_data, ip)
        host_scan_data.update(parsed_nmap_host_info)
        host_scan_data['ip'] = ip; host_scan_data['mac'] = mac; host_scan_data['vendor'] = vendor_str # Ensure these
        host_scan_data['scan_result'] = 'success'
        if parsed_nmap_host_info.get('hostname') and parsed_nmap_host_info['hostname'] not in ["Unknown (Reverse DNS failed)", "Unknown (Error in lookup)"]:
            host_scan_data['hostname'] = parsed_nmap_host_info['hostname']
    else:
        # Even if Nmap fails, we know the host is up from ARP
        host_scan_data['state'] = 'up (via ARP) - Nmap blocked by firewall'
        logging.info(f"Host {ip} detected via ARP but Nmap scan blocked - likely has active firewall")
    
    # Always store the result - we at least have ARP data
    with RESULTS_LOCK_OBJ:
        THREAD_RESULTS_LIST.append(host_scan_data)
    
    if pbar_instance:
        pbar_instance.update(1) # Update progress bar

def main(target_arg=None):
    logging.info("Autonomous Network Scanner (Enhanced V2) Starting...")
    logging.warning("CRITICAL: ENSURE YOU HAVE EXPLICIT, WRITTEN PERMISSION TO SCAN ANY TARGET NETWORK.")

    global THREAD_RESULTS_LIST
    THREAD_RESULTS_LIST = []
    local_ip_addr = get_local_ip()
    
    final_target_network_str = ""
    if target_arg:
        final_target_network_str = get_network_cidr(local_ip_addr, target_override=target_arg)
    elif CONFIG.get("local_network_subnet_override"):
        final_target_network_str = get_network_cidr(local_ip_addr, target_override=CONFIG['local_network_subnet_override'])
    elif local_ip_addr:
        final_target_network_str = get_network_cidr(local_ip_addr)
    else:
        logging.critical("Could not determine a target network. Exiting.")
        sys.exit(1)

    arp_discovered_devices = []
    try:
        ip_object_for_check = None
        try: ip_object_for_check = ipaddress.ip_interface(final_target_network_str)
        except ValueError:
            try:
                resolved_ip = socket.gethostbyname(final_target_network_str)
                logging.info(f"Resolved '{final_target_network_str}' to {resolved_ip}. Target: {resolved_ip}/32.")
                final_target_network_str = f"{resolved_ip}/32"
                ip_object_for_check = ipaddress.ip_interface(final_target_network_str)
            except socket.gaierror:
                logging.error(f"Cannot resolve hostname '{final_target_network_str}' and it's not valid IP/CIDR. Exiting.")
                sys.exit(1)
        
        if ip_object_for_check.network.num_addresses == 1:
            arp_discovered_devices = scan_arp_network(str(ip_object_for_check.ip))
            if not arp_discovered_devices:
                 arp_discovered_devices.append({'ip': str(ip_object_for_check.ip), 'mac': 'N/A (ARP fail/remote)'})
        else:
            arp_discovered_devices = scan_arp_network(final_target_network_str)
    except ValueError as e:
        logging.error(f"Invalid target '{final_target_network_str}': {e}. Exiting.")
        sys.exit(1)

    if not arp_discovered_devices:
        logging.warning(f"No devices from ARP on {final_target_network_str} or target list empty. Exiting.")
        return

    scan_threads = []
    max_threads_config = CONFIG.get("max_nmap_threads", 5)
    
    # Initialize tqdm progress bar
    with tqdm(total=len(arp_discovered_devices), desc="Scanning Hosts", unit="host") as pbar:
        for device_info_dict in arp_discovered_devices:
            while threading.active_count() -1 >= max_threads_config:
                time.sleep(0.5)
            
            logging.info(f"Queueing scan for {device_info_dict['ip']} (MAC: {device_info_dict['mac']})")
            thread_obj = threading.Thread(target=scan_host_threaded_worker, args=(device_info_dict, pbar))
            scan_threads.append(thread_obj)
            thread_obj.start()

        for t in scan_threads:
            t.join()
    # pbar will close automatically here

    final_detailed_devices_list = sorted(THREAD_RESULTS_LIST, key=lambda x: ipaddress.ip_address(x['ip']))

    logging.info("\n" + "="*30 + " Scan Summary " + "="*30) # Summary logging unchanged
    for dev_dict in final_detailed_devices_list:
        summary = [
            f"IP: {dev_dict.get('ip', 'N/A')}",
            f"  MAC: {dev_dict.get('mac', 'N/A')} (Vendor: {dev_dict.get('vendor', 'N/A')})",
            f"  Hostname: {dev_dict.get('hostname', 'N/A')}",
            f"  State: {dev_dict.get('state', 'N/A')}",
            f"  Primary OS: {dev_dict.get('os', 'N/A')}"
        ]
        if dev_dict.get('os_matches'):
            for i, os_match in enumerate(dev_dict['os_matches'][:2]):
                summary.append(f"    OS Match {i+1}: {os_match.get('name')} (Accuracy: {os_match.get('accuracy')}%)")
        logging.info("\n".join(summary))

        if dev_dict.get('ports'):
            logging.info("  Open Ports:")
            for p_info in dev_dict['ports']:
                port_line = (f"    - {p_info.get('port')}/{p_info.get('protocol')} "
                             f"({p_info.get('state')}) {p_info.get('name', '')} "
                             f"{p_info.get('product', '')} {p_info.get('version', '')} "
                             f"{p_info.get('extrainfo', '')}")
                logging.info(port_line.strip())
        else:
            logging.info("  No open ports found or reported by Nmap for this host.")

        if dev_dict.get('vulnerabilities'):
            logging.warning("  Potential Vulnerabilities Found:")
            for v_info in dev_dict['vulnerabilities']:
                refs_str = ", ".join(v_info.get('references',[]))
                output_oneline = str(v_info.get('output','')).replace('\n',' ').replace('\r','')[:120]
                logging.warning(f"    - Port {v_info.get('port')}/{v_info.get('protocol')} (Script: {v_info.get('script')})")
                logging.warning(f"      Details: {output_oneline}...")
                logging.warning(f"      Severity: {v_info.get('severity')} (CVSS: {v_info.get('cvss_score')})")
                if refs_str: logging.warning(f"      References: {refs_str}")
        
        if dev_dict.get('credentials_found'):
            logging.critical("  POTENTIAL CREDENTIALS FOUND:")
            for c_info in dev_dict['credentials_found']:
                details_oneline = str(c_info.get('details','')).replace('\n',' ').replace('\r','')[:120]
                logging.critical(f"    - Port {c_info.get('port')}/{c_info.get('protocol')} ({c_info.get('service')}) (Script: {c_info.get('script')}): {details_oneline}...")
        
        if dev_dict.get('web_enum'):
            logging.info("  Web Enumeration Details:")
            for port_key, enum_data_raw in dev_dict['web_enum'].items():
                 enum_data_oneline = str(enum_data_raw).replace('\n',' ').replace('\r','')[:150]
                 logging.info(f"    - Port {port_key}: {enum_data_oneline}...")
        logging.info("-" * 70)


    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base_filename = f"network_scan_results_{timestamp_str}"
    json_output_filename = f"{output_base_filename}.json"
    csv_output_filename = f"{output_base_filename}.csv"
    output_dir = "scan_outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_json(final_detailed_devices_list, os.path.join(output_dir, json_output_filename))
    save_csv(final_detailed_devices_list, os.path.join(output_dir, csv_output_filename))

    logging.info("\nAutonomous Network Scan Complete.")
    logging.info(f"Log file: {CONFIG.get('log_file')}")
    logging.info(f"JSON/CSV reports saved in '{output_dir}' directory.")

if __name__ == "__main__":
    cli_target = None
    if len(sys.argv) > 1:
        cli_target = sys.argv[1]
    main(target_arg=cli_target)