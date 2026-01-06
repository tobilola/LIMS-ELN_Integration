"""
Data Synchronization API Routes
Handles bi-directional sync between LIMS and ELN
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from app.schemas.common import (
    SyncRequest, SyncResponse, BatchSyncRequest, BatchSyncResponse
)
from app.database.postgres import get_db
from app.services.sync_service import SyncService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/sample", response_model=SyncResponse)
async def sync_sample(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Synchronize a sample between LIMS and ELN
    
    - **source_system**: System to sync from (lims or eln)
    - **target_system**: System to sync to (lims or eln)
    - **data**: Sample data to sync
    - **force_sync**: Force sync even if already synced
    """
    try:
        sync_service = SyncService(db)
        
        # Perform sync
        result = await sync_service.sync_sample(
            sample_id=request.sample_id,
            source_system=request.source_system,
            target_system=request.target_system,
            data=request.data,
            force_sync=request.force_sync
        )
        
        # Schedule background validation
        if result.success:
            background_tasks.add_task(
                sync_service.validate_sync,
                request.sample_id
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchSyncResponse)
async def batch_sync(
    request: BatchSyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Synchronize multiple samples in batch
    
    - **sample_ids**: List of sample IDs to sync
    - **source_system**: Source system
    - **target_system**: Target system
    """
    try:
        sync_service = SyncService(db)
        
        results = []
        successful = 0
        failed = 0
        
        for sample_id in request.sample_ids:
            try:
                result = await sync_service.sync_sample(
                    sample_id=sample_id,
                    source_system=request.source_system,
                    target_system=request.target_system,
                    data={},  # Will fetch from source
                    force_sync=request.force_sync
                )
                results.append(result)
                if result.success:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Failed to sync {sample_id}: {e}")
                failed += 1
                results.append(
                    SyncResponse(
                        success=False,
                        message=str(e),
                        sample_id=sample_id,
                        source_system=request.source_system.value,
                        target_system=request.target_system.value,
                        sync_timestamp=datetime.utcnow()
                    )
                )
        
        return BatchSyncResponse(
            total=len(request.sample_ids),
            successful=successful,
            failed=failed,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Batch sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{sample_id}")
async def sync_status(
    sample_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get synchronization status for a sample
    """
    try:
        sync_service = SyncService(db)
        status = await sync_service.get_sync_status(sample_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Sample not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sync status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
