"""
Data Validation API Routes
AI-powered validation of laboratory data
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.schemas.common import ValidationRequest, ValidationResponse
from app.database.postgres import get_db
from app.services.validation_service import ValidationService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/sample", response_model=ValidationResponse)
async def validate_sample(
    request: ValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate sample data with AI-powered checks
    
    - **sample_data**: Sample data to validate
    - **validation_level**: basic, standard, or full validation
    - **check_anomalies**: Run ML anomaly detection
    - **check_compliance**: Check regulatory compliance
    """
    try:
        validation_service = ValidationService(db)
        
        result = await validation_service.validate(
            data=request.sample_data,
            level=request.validation_level,
            check_anomalies=request.check_anomalies,
            check_compliance=request.check_compliance
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-result")
async def validate_test_result(
    test_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a single test result
    """
    try:
        validation_service = ValidationService(db)
        
        result = await validation_service.validate_test_result(test_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Test result validation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def validate_batch(
    samples: list[dict],
    db: AsyncSession = Depends(get_db)
):
    """
    Validate multiple samples in batch
    """
    try:
        validation_service = ValidationService(db)
        
        results = []
        for sample_data in samples:
            try:
                result = await validation_service.validate(
                    data=sample_data,
                    level="standard",
                    check_anomalies=True,
                    check_compliance=True
                )
                results.append({
                    "sample_id": sample_data.get("sample_id"),
                    "valid": result.valid,
                    "issues": len(result.issues)
                })
            except Exception as e:
                logger.error(f"Failed to validate sample: {e}")
                results.append({
                    "sample_id": sample_data.get("sample_id"),
                    "valid": False,
                    "error": str(e)
                })
        
        return {
            "total": len(samples),
            "valid": sum(1 for r in results if r.get("valid")),
            "invalid": sum(1 for r in results if not r.get("valid")),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch validation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
