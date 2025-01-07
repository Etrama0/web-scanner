import dns.resolver
import dns.zone
from concurrent.futures import ThreadPoolExecutor
import logging

class SubdomainEnumerator:
    """Subdomain enumeration and DNS reconnaissance"""
    
    def __init__(self, domain):
        self.domain = domain
        self.subdomains = set()
        self.logger = logging.getLogger(__name__)
        
        # Common subdomain prefixes to check
        self.common_subdomains = [
            'www', 'mail', 'remote', 'blog', 'webmail', 'server',
            'ns1', 'ns2', 'smtp', 'secure', 'vpn', 'api', 'dev',
            'staging', 'test', 'portal', 'admin', 'cdn', 'cloud'
        ]

    def check_subdomain(self, subdomain):
        """Check if a subdomain exists"""
        try:
            full_domain = f"{subdomain}.{self.domain}"
            answers = dns.resolver.resolve(full_domain, 'A')
            
            for answer in answers:
                self.subdomains.add({
                    'subdomain': full_domain,
                    'ip': answer.to_text(),
                    'type': 'A'
                })
                
            # Try to get MX records
            try:
                mx_records = dns.resolver.resolve(full_domain, 'MX')
                for mx in mx_records:
                    self.subdomains.add({
                        'subdomain': full_domain,
                        'mx': mx.to_text(),
                        'type': 'MX'
                    })
            except:
                pass
                
        except Exception as e:
            self.logger.debug(f"No record found for {subdomain}.{self.domain}: {str(e)}")

    def enumerate(self, max_workers=10):
        """Perform subdomain enumeration"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.check_subdomain, self.common_subdomains)
            
        return list(self.subdomains)

    def attempt_zone_transfer(self):
        """Attempt DNS zone transfer"""
        try:
            # Try to get NS records first
            ns_records = dns.resolver.resolve(self.domain, 'NS')
            
            for ns in ns_records:
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(str(ns), self.domain))
                    for name, node in zone.nodes.items():
                        name = str(name)
                        if name != '@':
                            self.subdomains.add({
                                'subdomain': f"{name}.{self.domain}",
                                'source': 'zone_transfer',
                                'nameserver': str(ns)
                            })
                except:
                    self.logger.debug(f"Zone transfer failed for {ns}")
                    
        except Exception as e:
            self.logger.error(f"Zone transfer error: {str(e)}")