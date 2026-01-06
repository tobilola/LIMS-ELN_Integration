"""
Pydantic Schemas for API Request/Response Validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SampleStatus(str, Enum):
    """Sample status enum"""
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class SystemType(str, Enum):
    """System type enum"""
    LIMS = "lims"
    ELN = "eln"


# ===== Sample Schemas =====

class SampleBase(BaseModel):
    """Base sample schema"""
    sample_id: str = Field(..., min_length=1, max_length=100)
    batch_number: Optional[str] = Field(None, max_length=100)
    sample_type: Optional[str] = Field(None, max_length=50)
    source_location: Optional[str] = None
    collection_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SampleCreate(SampleBase):
    """Schema for creating a sample"""
    created_by: Optional[str] = None


class SampleUpdate(BaseModel):
    """Schema for updating a sample"""
    batch_number: Optional[str] = None
    sample_type: Optional[str] = None
    source_location: Optional[str] = None
    status: Optional[SampleStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_by: Optional[str] = None


class SampleResponse(SampleBase):
    """Schema for sample response"""
    id: int
    status: SampleStatus
    lims_id: Optional[str] = None
    eln_id: Optional[str] = None
    lims_synced: Optional[datetime] = None
    eln_synced: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== Test Result Schemas =====

class TestResultBase(BaseModel):
    """Base test result schema"""
    test_name: str = Field(..., min_length=1)
    test_type: Optional[str] = None
    result_value: Optional[float] = None
    result_unit: Optional[str] = None
    result_text: Optional[str] = None
    tested_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TestResultCreate(TestResultBase):
    """Schema for creating test result"""
    sample_id: int


class TestResultResponse(TestResultBase):
    """Schema for test result response"""
    id: int
    sample_id: int
    pass_fail: Optional[str] = None
    confidence_score: Optional[float] = None
    anomaly_detected: str = "no"
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Sync Schemas =====

class SyncRequest(BaseModel):
    """Schema for sync request"""
    sample_id: Optional[str] = None
    source_system: SystemType
    target_system: SystemType
    data: Dict[str, Any]
    force_sync: bool = Field(default=False)
    
    @validator('source_system', 'target_system')
    def validate_different_systems(cls, v, values):
        if 'source_system' in values and v == values['source_system']:
            raise ValueError('Source and target systems must be different')
        return v


class SyncResponse(BaseModel):
    """Schema for sync response"""
    success: bool
    message: str
    sample_id: str
    source_system: str
    target_system: str
    sync_timestamp: datetime
    changes_applied: int = 0
    warnings: List[str] = Field(default_factory=list)


class BatchSyncRequest(BaseModel):
    """Schema for batch sync request"""
    sample_ids: List[str]
    source_system: SystemType
    target_system: SystemType
    force_sync: bool = False


class BatchSyncResponse(BaseModel):
    """Schema for batch sync response"""
    total: int
    successful: int
    failed: int
    results: List[SyncResponse]


# ===== Validation Schemas =====

class ValidationLevel(str, Enum):
    """Validation level enum"""
    BASIC = "basic"
    STANDARD = "standard"
    FULL = "full"


class ValidationRequest(BaseModel):
    """Schema for validation request"""
    sample_data: Dict[str, Any]
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    check_anomalies: bool = True
    check_compliance: bool = True


class ValidationIssue(BaseModel):
    """Schema for validation issue"""
    severity: str  # error, warning, info
    field: Optional[str] = None
    message: str
    suggestion: Optional[str] = None


class ValidationResponse(BaseModel):
    """Schema for validation response"""
    valid: bool
    validation_level: str
    issues: List[ValidationIssue] = Field(default_factory=list)
    anomaly_score: Optional[float] = None
    compliance_score: Optional[float] = None
    recommendations: List[str] = Field(default_factory=list)


# ===== NLP Schemas =====

class NLPParseRequest(BaseModel):
    """Schema for NLP parsing request"""
    text: str = Field(..., min_length=1)
    extract_entities: bool = True
    validate_sop: bool = False


class Entity(BaseModel):
    """Schema for extracted entity"""
    text: str
    type: str  # reagent, equipment, condition, action
    start: int
    end: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NLPParseResponse(BaseModel):
    """Schema for NLP parsing response"""
    success: bool
    entities: List[Entity] = Field(default_factory=list)
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    sop_compliant: Optional[bool] = None
    confidence_score: float
    warnings: List[str] = Field(default_factory=list)


# ===== Health & Monitoring Schemas =====

class HealthStatus(str, Enum):
    """Health status enum"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ServiceHealth(BaseModel):
    """Schema for service health"""
    status: HealthStatus
    latency_ms: Optional[float] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Schema for overall health response"""
    status: HealthStatus
    timestamp: datetime
    services: Dict[str, ServiceHealth]
    version: str = "1.0.0"
