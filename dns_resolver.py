import dns.resolver
import requests
import json
from PyQt5.QtCore import QObject, pyqtSignal

class SecureDNSResolver(QObject):
    resolution_complete = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        # Use Cloudflare's DNS-over-HTTPS service by default
        self.doh_url = "https://cloudflare-dns.com/dns-query"
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/dns-json'
        })

    def resolve(self, hostname):
        """Resolve hostname using DNS-over-HTTPS"""
        try:
            params = {
                'name': hostname,
                'type': 'A',
                'do': 'true',  # DNSSEC OK
                'cd': 'false'  # Checking Disabled = false (enable DNSSEC validation)
            }
            
            response = self.session.get(self.doh_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('Answer'):
                    ip = data['Answer'][0]['data']
                    self.resolution_complete.emit(hostname, ip)
                    return ip
            return None
        except Exception as e:
            print(f"DNS resolution error: {e}")
            return None

    def verify_dnssec(self, response):
        """Verify DNSSEC signatures if present"""
        try:
            if response.get('AD', False):  # AD = Authenticated Data
                return True
            return False
        except Exception:
            return False
