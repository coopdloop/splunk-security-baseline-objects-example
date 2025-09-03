#!/usr/bin/env python3
"""
SOAR Platform Integration Example  
Demonstrates integration with Security Orchestration, Automation, and Response platforms
"""

import json
import requests
from datetime import datetime

class SOARIntegration:
    """Generic SOAR platform integration"""
    
    def __init__(self, soar_url, api_token):
        self.soar_url = soar_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def create_incident(self, alert_data):
        """Create incident in SOAR platform from Splunk alert"""
        incident_payload = {
            'title': alert_data.get('alert_name', 'Splunk Security Alert'),
            'description': alert_data.get('description', ''),
            'severity': self._map_severity(alert_data.get('severity', 'medium')),
            'source': 'Splunk',
            'artifacts': self._extract_artifacts(alert_data),
            'created_time': datetime.now().isoformat(),
            'tags': ['splunk', 'automated', alert_data.get('category', 'security')]
        }
        
        try:
            response = requests.post(
                f"{self.soar_url}/api/incidents",
                headers=self.headers,
                json=incident_payload
            )
            response.raise_for_status()
            
            incident_data = response.json()
            return {
                'success': True,
                'incident_id': incident_data.get('id'),
                'incident_url': f"{self.soar_url}/incidents/{incident_data.get('id')}"
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _map_severity(self, splunk_severity):
        """Map Splunk severity levels to SOAR severity"""
        severity_map = {
            'critical': 'Critical',
            'high': 'High', 
            'medium': 'Medium',
            'low': 'Low',
            'informational': 'Info'
        }
        return severity_map.get(splunk_severity.lower(), 'Medium')
    
    def _extract_artifacts(self, alert_data):
        """Extract IOCs and artifacts from Splunk alert data"""
        artifacts = []
        
        # IP addresses
        if 'src_ip' in alert_data:
            artifacts.append({
                'type': 'ip',
                'value': alert_data['src_ip'],
                'tags': ['source_ip', 'network']
            })
        
        if 'dest_ip' in alert_data:
            artifacts.append({
                'type': 'ip', 
                'value': alert_data['dest_ip'],
                'tags': ['destination_ip', 'network']
            })
        
        # File hashes
        if 'file_hash' in alert_data:
            artifacts.append({
                'type': 'hash',
                'value': alert_data['file_hash'],
                'tags': ['file_hash', 'malware']
            })
        
        # URLs
        if 'url' in alert_data:
            artifacts.append({
                'type': 'url',
                'value': alert_data['url'], 
                'tags': ['web', 'communication']
            })
        
        # Domain names
        if 'domain' in alert_data:
            artifacts.append({
                'type': 'domain',
                'value': alert_data['domain'],
                'tags': ['dns', 'communication']
            })
        
        return artifacts

class PhantomIntegration(SOARIntegration):
    """Splunk Phantom/SOAR specific integration"""
    
    def create_container(self, alert_data):
        """Create container in Phantom"""
        container_payload = {
            'name': alert_data.get('alert_name'),
            'description': alert_data.get('description'),
            'severity': self._map_severity(alert_data.get('severity')),
            'sensitivity': 'amber',
            'status': 'new',
            'source_data_identifier': alert_data.get('search_id'),
            'label': 'splunk_security'
        }
        
        try:
            response = requests.post(
                f"{self.soar_url}/rest/container",
                headers=self.headers,
                json=container_payload
            )
            response.raise_for_status()
            
            container_data = response.json()
            container_id = container_data.get('id')
            
            # Add artifacts to container
            self._add_artifacts_to_container(container_id, alert_data)
            
            return {
                'success': True,
                'container_id': container_id,
                'container_url': f"{self.soar_url}/mission/{container_id}"
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_artifacts_to_container(self, container_id, alert_data):
        """Add artifacts to Phantom container"""
        artifacts = self._extract_artifacts(alert_data)
        
        for artifact in artifacts:
            artifact_payload = {
                'container_id': container_id,
                'label': 'artifact',
                'name': f"{artifact['type'].upper()}: {artifact['value']}",
                'cef': {
                    artifact['type']: artifact['value']
                },
                'tags': artifact['tags']
            }
            
            try:
                requests.post(
                    f"{self.soar_url}/rest/artifact",
                    headers=self.headers,
                    json=artifact_payload
                )
            except requests.RequestException as e:
                print(f"Failed to add artifact: {e}")

class ServiceNowIntegration:
    """ServiceNow ITSM integration for incident management"""
    
    def __init__(self, instance_url, username, password):
        self.instance_url = instance_url
        self.auth = (username, password)
        self.headers = {'Content-Type': 'application/json'}
    
    def create_security_incident(self, alert_data):
        """Create security incident in ServiceNow"""
        incident_payload = {
            'short_description': alert_data.get('alert_name'),
            'description': self._format_incident_description(alert_data),
            'category': 'Security',
            'subcategory': 'Security Incident',
            'urgency': self._map_urgency(alert_data.get('severity')),
            'impact': self._map_impact(alert_data.get('asset_criticality')),
            'caller_id': 'splunk.integration',
            'assignment_group': 'Security Operations',
            'work_notes': f"Alert generated by Splunk at {datetime.now()}"
        }
        
        try:
            response = requests.post(
                f"{self.instance_url}/api/now/table/incident",
                headers=self.headers,
                auth=self.auth,
                json=incident_payload
            )
            response.raise_for_status()
            
            incident_data = response.json()
            return {
                'success': True,
                'incident_number': incident_data.get('result', {}).get('number'),
                'sys_id': incident_data.get('result', {}).get('sys_id')
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_incident_description(self, alert_data):
        """Format incident description with alert details"""
        description = f"""
Security Alert Details:
- Alert: {alert_data.get('alert_name')}
- Severity: {alert_data.get('severity')}
- Source IP: {alert_data.get('src_ip', 'N/A')}
- Destination IP: {alert_data.get('dest_ip', 'N/A')}
- User: {alert_data.get('user', 'N/A')}
- Time: {alert_data.get('_time')}

Search Query: {alert_data.get('search_query', '')}

Investigation Required: {alert_data.get('description')}
        """
        return description.strip()
    
    def _map_urgency(self, severity):
        """Map Splunk severity to ServiceNow urgency"""
        urgency_map = {
            'critical': '1',
            'high': '2',
            'medium': '3', 
            'low': '3'
        }
        return urgency_map.get(severity, '3')
    
    def _map_impact(self, asset_criticality):
        """Map asset criticality to ServiceNow impact"""
        impact_map = {
            'critical': '1',
            'high': '2', 
            'medium': '3',
            'low': '3'
        }
        return impact_map.get(asset_criticality, '3')

# Example Splunk Script for Alert Actions
def splunk_alert_action():
    """Example script called by Splunk alert action"""
    import sys
    import os
    
    # Read alert data from Splunk
    alert_data = {}
    for line in sys.stdin:
        # Parse CSV alert results
        pass  # Implementation depends on alert format
    
    # Initialize integrations
    api_key = os.environ.get('THREAT_INTEL_API_KEY')
    if api_key:
        threat_api = ThreatIntelAPI(api_key)
        
        # Update threat intelligence
        threat_api.update_splunk_lookup()
    
    # Create SOAR incident
    soar_url = os.environ.get('SOAR_URL')
    soar_token = os.environ.get('SOAR_TOKEN')
    if soar_url and soar_token:
        soar = SOARIntegration(soar_url, soar_token)
        result = soar.create_incident(alert_data)
        
        if result['success']:
            print(f"Created SOAR incident: {result['incident_id']}")
        else:
            print(f"Failed to create SOAR incident: {result['error']}")

if __name__ == "__main__":
    # Example usage
    sample_alert = {
        'alert_name': 'Suspicious Network Activity',
        'severity': 'high',
        'src_ip': '192.0.2.100',
        'dest_ip': '198.51.100.200',
        'user': 'john.doe',
        'description': 'Multiple failed authentication attempts detected',
        '_time': '2024-01-01 12:00:00',
        'asset_criticality': 'high'
    }
    
    # Test SOAR integration
    soar = SOARIntegration('https://soar.example.com', 'api_token_here')
    result = soar.create_incident(sample_alert)
    print(f"SOAR Result: {result}")