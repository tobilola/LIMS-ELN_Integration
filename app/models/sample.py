"""
Sample Data Model
Represents laboratory samples tracked in the system
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database.postgres import Base


class SampleStatus(str, enum.Enum):
    """Sample status enum"""
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Sample(Base):
    """Sample model"""
    __tablename__ = "samples"
    
    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String(100), unique=True, index=True, nullable=False)
    batch_number = Column(String(100), index=True)
    
    # Sample metadata
    sample_type = Column(String(50))
    source_location = Column(String(200))
    collection_date = Column(DateTime)
    
    # Status tracking
    status = Column(Enum(SampleStatus), default=SampleStatus.REGISTERED)
    
    # System tracking
    lims_id = Column(String(100), index=True)
    eln_id = Column(String(100), index=True)
    lims_synced = Column(DateTime)
    eln_synced = Column(DateTime)
    
    # Metadata (flexible JSON field)
    metadata = Column(JSON, default={})
    
    # Audit fields
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    test_results = relationship("TestResult", back_populates="sample", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="sample", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sample(id={self.id}, sample_id={self.sample_id}, status={self.status})>"


class TestResult(Base):
    """Test result model"""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    
    # Test information
    test_name = Column(String(200), nullable=False)
    test_type = Column(String(100))
    
    # Results
    result_value = Column(Float)
    result_unit = Column(String(50))
    result_text = Column(String(500))
    
    # Quality metrics
    pass_fail = Column(String(10))
    confidence_score = Column(Float)
    anomaly_detected = Column(String(10), default="no")
    
    # Timestamps
    tested_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Relationships
    sample = relationship("Sample", back_populates="test_results")
    
    def __repr__(self):
        return f"<TestResult(id={self.id}, test_name={self.test_name}, result={self.result_value})>"


class AuditLog(Base):
    """Audit log model for compliance tracking"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=True)
    
    # Event information
    event_type = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(200))
    
    # User information
    user_id = Column(String(100))
    user_email = Column(String(200))
    ip_address = Column(String(50))
    
    # Change tracking
    changes = Column(JSON, default={})
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    # System tracking
    system_source = Column(String(50))  # lims, eln, integration
    
    # Timestamp
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    sample = relationship("Sample", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user={self.user_email})>"
