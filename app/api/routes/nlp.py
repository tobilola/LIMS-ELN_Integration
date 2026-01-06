"""
NLP API Routes
Natural Language Processing for protocol parsing
"""

from fastapi import APIRouter, HTTPException
import logging

from app.schemas.common import NLPParseRequest, NLPParseResponse
from app.services.nlp_service import NLPService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/parse-protocol", response_model=NLPParseResponse)
async def parse_protocol(request: NLPParseRequest):
    """
    Parse laboratory protocol text and extract structured information
    
    - **text**: Protocol text to parse
    - **extract_entities**: Extract entities (reagents, equipment, conditions)
    - **validate_sop**: Check compliance with SOPs
    """
    try:
        nlp_service = NLPService()
        
        result = await nlp_service.parse_protocol(
            text=request.text,
            extract_entities=request.extract_entities,
            validate_sop=request.validate_sop
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Protocol parsing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-metadata")
async def extract_metadata(text: str):
    """
    Extract metadata from free-text lab notes
    """
    try:
        nlp_service = NLPService()
        
        metadata = await nlp_service.extract_metadata(text)
        
        return {
            "success": True,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Metadata extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-protocol")
async def classify_protocol(text: str):
    """
    Classify protocol type (e.g., extraction, purification, analysis)
    """
    try:
        nlp_service = NLPService()
        
        classification = await nlp_service.classify_protocol(text)
        
        return classification
        
    except Exception as e:
        logger.error(f"Protocol classification failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
