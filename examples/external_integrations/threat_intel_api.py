#!/usr/bin/env python3
"""
Threat Intelligence API Integration Example
Demonstrates how to fetch threat intelligence data and format for Splunk lookup tables
"""

import csv
import json
import requests
import time
from datetime import datetime

class ThreatIntelAPI:
    """Example threat intelligence API integration"""
    
    def __init__(self, api_key, base_url="https://api.threatintel.example.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_malicious_ips(self, since_hours=24):
        """Fetch malicious IP indicators from the last N hours"""
        endpoint = f"{self.base_url}/indicators/ip"
        params = {
            'since': f'-{since_hours}h',
            'confidence': 'high,medium',
            'status': 'active'
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def get_malicious_domains(self, since_hours=24):
        """Fetch malicious domain indicators"""
        endpoint = f"{self.base_url}/indicators/domain"
        params = {
            'since': f'-{since_hours}h',
            'confidence': 'high,medium',
            'status': 'active'
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def format_for_splunk_lookup(self, indicators):
        """Convert API response to Splunk lookup table format"""
        splunk_indicators = []
        
        for indicator in indicators.get('data', []):
            splunk_indicator = {
                'threat_indicator': indicator.get('value'),
                'threat_type': indicator.get('type'),
                'confidence': indicator.get('confidence'),
                'first_seen': indicator.get('first_seen'),
                'last_seen': indicator.get('last_seen', datetime.now().isoformat()),
                'description': indicator.get('description', ''),
                'source': indicator.get('source', 'Threat Intel API')
            }
            splunk_indicators.append(splunk_indicator)
        
        return splunk_indicators
    
    def update_splunk_lookup(self, output_file='threat_indicators.csv'):
        """Update Splunk lookup table with latest threat intelligence"""
        # Fetch IP and domain indicators
        ip_data = self.get_malicious_ips()
        domain_data = self.get_malicious_domains()
        
        all_indicators = []
        
        if ip_data:
            all_indicators.extend(self.format_for_splunk_lookup(ip_data))
        
        if domain_data:
            all_indicators.extend(self.format_for_splunk_lookup(domain_data))
        
        # Write to CSV file
        if all_indicators:
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = ['threat_indicator', 'threat_type', 'confidence', 
                             'first_seen', 'last_seen', 'description', 'source']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_indicators)
            
            print(f"Updated {output_file} with {len(all_indicators)} indicators")
            return True
        else:
            print("No threat indicators retrieved")
            return False

class VirusTotalIntegration:
    """VirusTotal API integration example"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/vtapi/v2"
    
    def check_file_hash(self, file_hash):
        """Check file hash reputation via VirusTotal"""
        url = f"{self.base_url}/file/report"
        params = {
            'apikey': self.api_key,
            'resource': file_hash
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                'file_hash': file_hash,
                'positives': data.get('positives', 0),
                'total': data.get('total', 0),
                'scan_date': data.get('scan_date'),
                'permalink': data.get('permalink'),
                'reputation': 'malicious' if data.get('positives', 0) > 5 else 'clean'
            }
        except requests.RequestException as e:
            print(f"VirusTotal API error: {e}")
            return None
    
    def bulk_hash_check(self, hash_list, output_file='hash_reputation.csv'):
        """Check multiple hashes and create Splunk lookup"""
        results = []
        
        for file_hash in hash_list:
            result = self.check_file_hash(file_hash)
            if result:
                results.append(result)
            time.sleep(1)  # Rate limiting
        
        # Write to CSV
        if results:
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = ['file_hash', 'positives', 'total', 'scan_date', 
                             'permalink', 'reputation']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            return True
        return False

# Example usage
if __name__ == "__main__":
    # Threat Intelligence API example
    threat_api = ThreatIntelAPI(api_key="your_api_key_here")
    threat_api.update_splunk_lookup()
    
    # VirusTotal integration example
    vt_api = VirusTotalIntegration(api_key="your_vt_api_key")
    sample_hashes = [
        "d41d8cd98f00b204e9800998ecf8427e",
        "098f6bcd4621d373cade4e832627b4f6"
    ]
    vt_api.bulk_hash_check(sample_hashes)