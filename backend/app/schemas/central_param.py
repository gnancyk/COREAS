from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional

class UrlControlRequest(BaseModel):
    url: str

class ParamRequest(BaseModel):
    url: str
    param_name: Optional[str] = None

class ControlResponse(BaseModel):
    url: str
    is_valid_syntax: bool
    is_wcf_service: bool
    status_code: int
    health_check: str
    message: str
    details: Optional[Dict] = None

class ParamItem(BaseModel):
    name: str
    value: Optional[str] = ""
    parsed_values: Optional[Dict[str, str]] = None

class CentralParamResponse(BaseModel):
    url: str
    count: int
    parameters: List[ParamItem]

class ConformityResponse(BaseModel):
    url: str
    is_valid_syntax: bool
    is_wcf_service: bool
    param_count: int
    is_conforme: bool
    health_check: str
    message: str
