from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class InfraBaseRequest(BaseModel):
    servers: List[str] = Field(..., example=["srv-batch-01", "srv-batch-02"])

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

class OSInfoResult(BaseModel):
    server: str
    os_name: str
    os_version: str
    last_reboot: str
    cpu_count: int
    is_reachable: bool
    error_message: Optional[str] = None

class OSInfoResponse(BaseModel):
    results: List[OSInfoResult]
