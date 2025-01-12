from scapy.layers.inet import IP, TCP
from scapy.sendrecv import sr1
from scapy.automaton import Automaton

import logging

class NetworkScanner:
    """Base network scanning class for reconnaissance module"""
    
    def __init__(self, target_host, port_range=(1, 1024)):
        self.target_host = target_host
        self.port_range = port_range
        self.open_ports = []
        self.logger = logging.getLogger(__name__)
        
    def tcp_scan(self, timeout=2):
        """Perform TCP SYN scan on specified ports"""
        try:
            for port in range(self.port_range[0], self.port_range[1] + 1):
                # Create TCP SYN packet
                syn_packet = IP(dst=self.target_host)/TCP(dport=port, flags="S")
                
                # Send packet and wait for response
                response = sr1(syn_packet, timeout=timeout, verbose=False)
                
                if response is None:
                    continue
                
                # Check if port is open (SYN-ACK received)
                if response.haslayer(TCP) and response[TCP].flags == 0x12:
                    self.open_ports.append(port)
                    self.logger.info(f"Port {port} is open on {self.target_host}")
                    
                    # Send RST to close connection
                    rst_packet = IP(dst=self.target_host)/TCP(dport=port, flags="R")
                    sr1(rst_packet, timeout=timeout, verbose=False)
                    
        except Exception as e:
            self.logger.error(f"Scan error: {str(e)}")
            raise
            
    def get_scan_results(self):
        """Return scan results in a structured format"""
        return {
            'target': self.target_host,
            'open_ports': self.open_ports,
            'scan_range': self.port_range
        }
