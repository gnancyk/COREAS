from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class InfraBaseRequest(BaseModel):
    servers: List[str] = Field(..., example=["srv-batch-01", "srv-batch-02"])
    username: Optional[str] = None
    password: Optional[str] = None

class PortVerificationRequest(InfraBaseRequest):
    port: int = 5986

class OSInfoRequest(InfraBaseRequest):
    pass

class AvailabilityRequest(InfraBaseRequest):
    pass

class AvailabilityResult(BaseModel):
    server: str
    is_alive: bool
    status: str

class AvailabilityResponse(BaseModel):
    results: List[AvailabilityResult]

class PortVerificationResult(BaseModel):
    server: str
    port: int
    is_open: bool
    status: str

class PortVerificationResponse(BaseModel):
    results: List[PortVerificationResult]

class FeatureVerificationRequest(InfraBaseRequest):
    features: List[str] = Field(..., example=["Web-Server", "Web-Deploy"])

class FeatureResult(BaseModel):
    server: str
    feature: str
    is_installed: bool

class FeatureVerificationResponse(BaseModel):
    results: List[FeatureResult]

class ThresholdRequest(BaseModel):
    servers: List[str]
    min_ram_gb: float = 4.0
    min_disk_gb: float = 10.0
    max_cpu_percent: float = 90.0

class MetricResult(BaseModel):
    server: str
    metric: str
    value: float
    unit: str
    is_compliant: bool
    message: Optional[str] = None

class ThresholdResponse(BaseModel):
    results: List[MetricResult]
    is_global_compliant: bool

class ProcessInfo(BaseModel):
    name: str
    cpu_usage: Optional[float] = None
    ram_usage_mb: float

class SSLInfo(BaseModel):
    subject: str
    expiry_date: str
    days_remaining: int
    is_valid: bool

class AppPoolInfo(BaseModel):
    name: str
    state: str

class OSInfoResult(BaseModel):
    server: str
    os_name: str
    os_version: str
    last_reboot: str
    cpu_count: int
    cpu_usage_percent: Optional[float] = None
    ram_total_gb: Optional[float] = None
    ram_used_gb: Optional[float] = None
    ram_free_gb: Optional[float] = None
    disk_total_gb: Optional[float] = None
    disk_used_gb: Optional[float] = None
    disk_free_gb: Optional[float] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    top_processes: List[ProcessInfo] = []
    dns_status: Dict[str, bool] = {}
    last_update_date: Optional[str] = None
    ssl_certificates: List[SSLInfo] = []
    app_pools: List[AppPoolInfo] = []
    is_reachable: bool
    error_message: Optional[str] = None

class OSInfoResponse(BaseModel):
    results: List[OSInfoResult]
