from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class BatchBaseRequest(BaseModel):
    servers: List[str] = Field(..., example=["srv-batch-01"])
    username: Optional[str] = None
    password: Optional[str] = None

class ServiceCheckRequest(BatchBaseRequest):
    services: List[str] = Field(..., example=["aspnet_state", "W3SVC", "SAPHIRV3_Batch"])

class ServiceStatus(BaseModel):
    name: str
    display_name: str
    status: str
    is_running: bool

class ServerServiceResult(BaseModel):
    server: str
    services: List[ServiceStatus]
    is_reachable: bool
    error_message: Optional[str] = None

class ServiceCheckResponse(BaseModel):
    results: List[ServerServiceResult]

class DateTimeResult(BaseModel):
    server: str
    current_time: str
    is_reachable: bool

class DateTimeResponse(BaseModel):
    results: List[DateTimeResult]

class CriteriaCheckRequest(BatchBaseRequest):
    file_paths: List[str] = Field(..., example=["C:\\SaphirV3\\Critere.xml"])

class CriteriaResult(BaseModel):
    server: str
    path: str
    exists: bool

class CriteriaResponse(BaseModel):
    results: List[CriteriaResult]

class DynamicAuditRequest(BatchBaseRequest):
    search_roots: List[str] = Field(default=["C:\\SaphirV3", "C:\\Program Files\\SaphirV3"])

class ConfigDetail(BaseModel):
    file_path: str
    param_crit_0001: Optional[str] = None
    critere_file_exists: bool = False
    central_param_endpoint: Optional[str] = None

class DynamicAuditResult(BaseModel):
    server: str
    configs_found: List[ConfigDetail]
    iis_pools: List[Dict[str, str]]
    is_reachable: bool

class DynamicAuditResponse(BaseModel):
    results: List[DynamicAuditResult]

class SQLConnectRequest(BatchBaseRequest):
    sql_instance: str = Field(..., example="GSECRMS1DEV\\SODECI")
    port: int = 1433

class SQLConnectResult(BaseModel):
    server: str
    sql_instance: str
    is_reachable: bool
    port_open: bool

class SQLConnectResponse(BaseModel):
    results: List[SQLConnectResult]

class ComplianceCheckRequest(BatchBaseRequest):
    central_param_url: str = Field(..., example="http://10.10.20.50/CentralParam/CentralParam.svc")
    saphir_modules: Optional[List[str]] = Field(default=None)
    search_paths: Optional[List[str]] = Field(default=None) # Chemins UNC fournis manuellement
    servers: Optional[List[str]] = Field(default=None)

class ComplianceCheckResult(BaseModel):
    server: str
    config_file: str
    local_endpoint: Optional[str]
    reference_endpoint: str
    is_compliant: bool

class ComplianceCheckResponse(BaseModel):
    results: List[ComplianceCheckResult]
