import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
import logging

class ServiceDetector:
    """Service detection and banner grabbing"""
    
    COMMON_PORTS = {
        80: 'HTTP',
        443: 'HTTPS',
        21: 'FTP',
        22: 'SSH',
        23: 'TELNET',
        25: 'SMTP',
        53: 'DNS',
        3306: 'MYSQL',
        5432: 'POSTGRESQL'
    }

    def __init__(self, target_host, ports):
        self.target_host = target_host
        self.ports = ports
        self.services = {}
        self.logger = logging.getLogger(__name__)

    def detect_service(self, port):
        """Detect service running on a specific port"""
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            
            # Try to connect
            sock.connect((self.target_host, port))
            
            service_banner = ""
            
            # Handle HTTPS separately
            if port == 443:
                try:
                    ssl_sock = ssl.wrap_socket(sock)
                    cert = ssl_sock.getpeercert()
                    service_banner = f"HTTPS (SSL/TLS) - Cert Subject: {cert.get('subject', 'Unknown')}"
                except ssl.SSLError:
                    service_banner = "HTTPS (SSL/TLS) - Unable to verify certificate"
            else:
                # Try to grab banner
                try:
                    sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    service_banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                except:
                    service_banner = f"Service on port {port}"
            
            self.services[port] = {
                'service': self.COMMON_PORTS.get(port, 'Unknown'),
                'banner': service_banner
            }
            
        except Exception as e:
            self.logger.debug(f"Error detecting service on port {port}: {str(e)}")
        finally:
            sock.close()

    def detect_all_services(self, max_workers=10):
        """Detect services on all specified ports using thread pool"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.detect_service, self.ports)
        
        return self.services
