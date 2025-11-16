#!/usr/bin/env python3
"""
Simple test script to validate configuration files and basic functionality
"""
import json
import sys
import os

def test_config_file(config_path):
    """Test if a configuration file is valid"""
    print(f"\nTesting {config_path}...")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = [
            'nmap_scan_mode',
            'max_nmap_threads',
            'log_file',
            'use_decoys',
            'fragment_packets',
            'randomize_hosts',
            'source_port',
            'retry_on_failure',
            'max_retries',
            'scan_techniques',
            'ipv6_fallback'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"  ❌ Missing fields: {', '.join(missing_fields)}")
            return False
        
        # Validate field types and values
        if not isinstance(config['max_nmap_threads'], int) or config['max_nmap_threads'] < 1:
            print(f"  ❌ Invalid max_nmap_threads: {config['max_nmap_threads']}")
            return False
        
        if not isinstance(config['use_decoys'], bool):
            print(f"  ❌ Invalid use_decoys: {config['use_decoys']}")
            return False
        
        if not isinstance(config['scan_techniques'], list) or len(config['scan_techniques']) == 0:
            print(f"  ❌ Invalid scan_techniques: {config['scan_techniques']}")
            return False
        
        if not isinstance(config['source_port'], int) or config['source_port'] < 0 or config['source_port'] > 65535:
            print(f"  ❌ Invalid source_port: {config['source_port']}")
            return False
        
        print(f"  ✅ Valid configuration")
        print(f"     - Mode: {config['nmap_scan_mode']}")
        print(f"     - Threads: {config['max_nmap_threads']}")
        print(f"     - Decoys: {config['use_decoys']} ({config.get('decoy_count', 0)})")
        print(f"     - Source port: {config['source_port']}")
        print(f"     - Retry enabled: {config['retry_on_failure']}")
        print(f"     - Max retries: {config['max_retries']}")
        print(f"     - Scan techniques: {', '.join(config['scan_techniques'])}")
        print(f"     - IPv6 fallback: {config['ipv6_fallback']}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parsing error: {e}")
        return False
    except FileNotFoundError:
        print(f"  ❌ File not found")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_all_configs():
    """Test all configuration files"""
    print("="*60)
    print("Wire-Py Configuration Validation Test")
    print("="*60)
    
    config_files = [
        'config.json',
        'config_stealth.json',
        'config_ultra_stealth.json',
        'config_balanced.json',
        'config_aggressive.json'
    ]
    
    results = {}
    for config_file in config_files:
        if os.path.exists(config_file):
            results[config_file] = test_config_file(config_file)
        else:
            print(f"\n⚠️  {config_file} not found (skipping)")
            results[config_file] = None
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for config_file, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        print(f"{config_file:30s} {status}")
    
    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed > 0:
        print("\n❌ Some tests failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def test_python_syntax():
    """Test Python syntax of main scripts"""
    print("\n" + "="*60)
    print("Python Syntax Validation")
    print("="*60)
    
    scripts = [
        'rapid-scan.py',
        'quick-scan.py',
        'advanced-scanner.py'
    ]
    
    all_valid = True
    for script in scripts:
        if os.path.exists(script):
            print(f"\nChecking {script}...")
            result = os.system(f"python3 -m py_compile {script} 2>/dev/null")
            if result == 0:
                print(f"  ✅ Valid Python syntax")
            else:
                print(f"  ❌ Syntax errors found")
                all_valid = False
        else:
            print(f"\n⚠️  {script} not found")
    
    return all_valid

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    syntax_ok = test_python_syntax()
    config_ok = test_all_configs()
    
    # Exit with appropriate code
    if syntax_ok and config_ok:
        print("\n" + "="*60)
        print("🎉 All validation tests passed!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ Some validation tests failed!")
        print("="*60)
        sys.exit(1)
