from dataclasses import dataclass
from typing import Optional, List, Dict, Union
from enum import Enum

class ScanStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ScanTarget:
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30

@dataclass
class ScanResult:
    target: ScanTarget
    status: ScanStatus
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    headers: Optional[Dict[str, str]] = None
    errors: Optional[List[str]] = None

@dataclass
class ScanConfig:
    targets: List[ScanTarget]
    concurrent_scans: int = 5
    retry_count: int = 3
    verify_ssl: bool = True