import nmap
import logging
from typing import List, Tuple

class NetworkReconnaissance:
    def __init__(self):
        try:
            self.scanner = nmap.PortScanner()
        except nmap.PortScannerError:
            logging.error("Nmap not found, please install nmap: https://nmap.org/download.html")
            raise
        except Exception as e:
            logging.error(f"Failed to initialize scanner: {str(e)}")
            raise

    def scan_network(self, target: str) -> List[Tuple[str, str]]:
        try:
            self.scanner.scan(hosts=target, arguments='-sn')
            hosts_list = [(x, self.scanner[x]['status']['state']) 
                         for x in self.scanner.all_hosts()]
            for host, status in hosts_list:
                logging.info(f'Host: {host} | Status: {status}')
            return hosts_list
        except Exception as e:
            logging.error(f"Scan failed: {str(e)}")
            return [] 