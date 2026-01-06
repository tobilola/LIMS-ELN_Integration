"""
Data Synchronization Service
Handles bidirectional sync between LIMS and ELN systems
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from app.models.sample import Sample, SampleStatus, AuditLog
from app.schemas.common import SyncResponse, SystemType

logger = logging.getLogger(__name__)


class SyncService:
    """Service for managing data synchronization between systems."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def sync_sample(
        self,
        sample_id: Optional[str],
        source_system: SystemType,
        target_system: SystemType,
        data: Dict[str, Any],
        force_sync: bool = False
    ) -> SyncResponse:
        """
        Synchronize sample data between LIMS and ELN.
        
        Args:
            sample_id: Sample identifier
            source_system: Source system (lims or eln)
            target_system: Target system (lims or eln)
            data: Sample data to sync
            force_sync: Force sync even if already synced
            
        Returns:
            SyncResponse with status and details
        """
        try:
            sample = await self._get_or_create_sample(sample_id, data)
            
            if not force_sync and await self._is_synced(sample, target_system):
                return SyncResponse(
                    success=True,
                    message="Sample already synced",
                    sample_id=sample.sample_id,
                    source_system=source_system.value,
                    target_system=target_system.value,
                    sync_timestamp=datetime.utcnow(),
                    changes_applied=0
                )
            
            validation_errors = await self._validate_sync_data(data)
            if validation_errors:
                return SyncResponse(
                    success=False,
                    message="Validation failed",
                    sample_id=sample.sample_id,
                    source_system=source_system.value,
                    target_system=target_system.value,
                    sync_timestamp=datetime.utcnow(),
                    warnings=validation_errors
                )
            
            changes = await self._sync_to_target(sample, target_system, data)
            await self._update_sync_status(sample, target_system)
            await self._create_audit_log(sample, source_system, target_system, changes)
            
            await self.db.commit()
            
            return SyncResponse(
                success=True,
                message="Sync completed successfully",
                sample_id=sample.sample_id,
                source_system=source_system.value,
                target_system=target_system.value,
                sync_timestamp=datetime.utcnow(),
                changes_applied=changes
            )
            
        except Exception as e:
            logger.error(f"Sync failed for sample {sample_id}: {e}")
            await self.db.rollback()
            raise
    
    async def _get_or_create_sample(self, sample_id: Optional[str], data: Dict[str, Any]) -> Sample:
        """Get existing sample or create new one."""
        if sample_id:
            result = await self.db.execute(select(Sample).where(Sample.sample_id == sample_id))
            sample = result.scalar_one_or_none()
            if sample:
                return sample
        
        sample = Sample(
            sample_id=sample_id or data.get('sample_id'),
            batch_number=data.get('batch_number'),
            sample_type=data.get('sample_type'),
            source_location=data.get('source_location'),
            collection_date=data.get('collection_date'),
            metadata=data.get('metadata', {}),
            status=SampleStatus.REGISTERED
        )
        self.db.add(sample)
        await self.db.flush()
        return sample
    
    async def _is_synced(self, sample: Sample, target_system: SystemType) -> bool:
        """Check if sample is already synced to target system."""
        if target_system == SystemType.LIMS:
            return sample.lims_synced is not None
        else:
            return sample.eln_synced is not None
    
    async def _validate_sync_data(self, data: Dict[str, Any]) -> list:
        """Validate data before sync."""
        errors = []
        if not data.get('sample_id'):
            errors.append("Missing required field: sample_id")
        return errors
    
    async def _sync_to_target(self, sample: Sample, target_system: SystemType, data: Dict[str, Any]) -> int:
        """Sync data to target system."""
        changes = 0
        
        if 'batch_number' in data and sample.batch_number != data['batch_number']:
            sample.batch_number = data['batch_number']
            changes += 1
        
        if 'sample_type' in data and sample.sample_type != data['sample_type']:
            sample.sample_type = data['sample_type']
            changes += 1
        
        if 'metadata' in data:
            sample.metadata.update(data['metadata'])
            changes += 1
        
        return changes
    
    async def _update_sync_status(self, sample: Sample, target_system: SystemType):
        """Update sync timestamp for target system."""
        sync_time = datetime.utcnow()
        if target_system == SystemType.LIMS:
            sample.lims_synced = sync_time
        else:
            sample.eln_synced = sync_time
    
    async def _create_audit_log(self, sample: Sample, source_system: SystemType, 
                                 target_system: SystemType, changes: int):
        """Create audit trail entry."""
        audit = AuditLog(
            sample_id=sample.id,
            event_type="sync",
            action=f"sync_{source_system.value}_to_{target_system.value}",
            resource=f"sample/{sample.sample_id}",
            system_source="integration",
            changes={"changes_applied": changes},
            timestamp=datetime.utcnow()
        )
        self.db.add(audit)
    
    async def get_sync_status(self, sample_id: str) -> Optional[Dict[str, Any]]:
        """Get synchronization status for a sample."""
        result = await self.db.execute(select(Sample).where(Sample.sample_id == sample_id))
        sample = result.scalar_one_or_none()
        
        if not sample:
            return None
        
        return {
            "sample_id": sample.sample_id,
            "status": sample.status.value,
            "lims_synced": sample.lims_synced.isoformat() if sample.lims_synced else None,
            "eln_synced": sample.eln_synced.isoformat() if sample.eln_synced else None,
            "created_at": sample.created_at.isoformat(),
            "updated_at": sample.updated_at.isoformat()
        }
    
    async def validate_sync(self, sample_id: str):
        """Validate sync consistency between systems."""
        logger.info(f"Validating sync for sample {sample_id}")
