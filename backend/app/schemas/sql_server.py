from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class SQLAuditBaseRequest(BaseModel):
    db_name: str = Field(..., example="CIE_Lite_MSCRM")
    server_address: Optional[str] = None # Si différent du .env

class IndexFragmentation(BaseModel):
    table_name: str
    index_name: str
    fragmentation_percent: float
    action_suggested: str

class FragmentationResponse(BaseModel):
    database: str
    results: List[IndexFragmentation]

class MissingIndex(BaseModel):
    table_name: str
    equality_columns: Optional[str]
    inequality_columns: Optional[str]
    included_columns: Optional[str]
    impact: float

class MissingIndexResponse(BaseModel):
    database: str
    results: List[MissingIndex]

class TriggerStatus(BaseModel):
    trigger_name: str
    table_name: str
    is_enabled: bool
    exists: bool

class TriggerResponse(BaseModel):
    database: str
    results: List[TriggerStatus]

class OrgIdConsistency(BaseModel):
    organization_id: str
    record_count: int

class OrgIdResponse(BaseModel):
    database: str
    is_consistent: bool
    results: List[OrgIdConsistency]

class CatalogSuspect(BaseModel):
    object_name: str
    object_type: str
    suspect_content: str # Extrait du code SQL contenant un nom de base en dur

class CatalogResponse(BaseModel):
    database: str
    results: List[CatalogSuspect]
