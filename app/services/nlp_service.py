"""
NLP Service
Natural language processing for protocol parsing
"""

import spacy
from typing import Dict, Any, List
import logging

from app.schemas.common import NLPParseResponse, Entity

logger = logging.getLogger(__name__)


class NLPService:
    """Service for natural language processing of laboratory protocols."""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    async def parse_protocol(
        self,
        text: str,
        extract_entities: bool = True,
        validate_sop: bool = False
    ) -> NLPParseResponse:
        """
        Parse laboratory protocol text and extract structured information.
        
        Args:
            text: Protocol text to parse
            extract_entities: Extract entities (reagents, equipment, conditions)
            validate_sop: Check compliance with SOPs
            
        Returns:
            NLPParseResponse with entities and structured data
        """
        if not self.nlp:
            return NLPParseResponse(
                success=False,
                entities=[],
                structured_data={},
                confidence_score=0.0,
                warnings=["NLP model not loaded"]
            )
        
        try:
            doc = self.nlp(text)
            entities = []
            structured_data = {}
            
            if extract_entities:
                entities = await self._extract_entities(doc)
                structured_data = await self._structure_data(doc, entities)
            
            sop_compliant = None
            if validate_sop:
                sop_compliant = await self._validate_sop_compliance(doc)
            
            return NLPParseResponse(
                success=True,
                entities=entities,
                structured_data=structured_data,
                sop_compliant=sop_compliant,
                confidence_score=0.85,
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"Protocol parsing failed: {e}")
            return NLPParseResponse(
                success=False,
                entities=[],
                structured_data={},
                confidence_score=0.0,
                warnings=[str(e)]
            )
    
    async def _extract_entities(self, doc) -> List[Entity]:
        """Extract named entities from protocol text."""
        entities = []
        
        # Extract standard NER entities
        for ent in doc.ents:
            entities.append(Entity(
                text=ent.text,
                type=ent.label_.lower(),
                start=ent.start_char,
                end=ent.end_char,
                metadata={}
            ))
        
        # Extract domain-specific entities
        entities.extend(await self._extract_reagents(doc))
        entities.extend(await self._extract_equipment(doc))
        entities.extend(await self._extract_conditions(doc))
        
        return entities
    
    async def _extract_reagents(self, doc) -> List[Entity]:
        """Extract reagent mentions."""
        reagents = []
        reagent_keywords = ['reagent', 'solution', 'buffer', 'acid', 'base']
        
        for token in doc:
            if token.text.lower() in reagent_keywords:
                # Look for quantity before/after
                for child in token.children:
                    if child.pos_ == "NUM":
                        reagents.append(Entity(
                            text=f"{child.text} {token.text}",
                            type="reagent",
                            start=min(token.idx, child.idx),
                            end=max(token.idx + len(token.text), child.idx + len(child.text)),
                            metadata={"quantity": child.text}
                        ))
        
        return reagents
    
    async def _extract_equipment(self, doc) -> List[Entity]:
        """Extract equipment mentions."""
        equipment = []
        equipment_keywords = ['centrifuge', 'spectro', 'flask', 'beaker', 'pipette']
        
        for token in doc:
            for keyword in equipment_keywords:
                if keyword in token.text.lower():
                    equipment.append(Entity(
                        text=token.text,
                        type="equipment",
                        start=token.idx,
                        end=token.idx + len(token.text),
                        metadata={}
                    ))
        
        return equipment
    
    async def _extract_conditions(self, doc) -> List[Entity]:
        """Extract experimental conditions (temperature, time, etc)."""
        conditions = []
        
        for token in doc:
            # Temperature
            if '°' in token.text or 'C' in token.text:
                conditions.append(Entity(
                    text=token.text,
                    type="condition",
                    start=token.idx,
                    end=token.idx + len(token.text),
                    metadata={"type": "temperature"}
                ))
            
            # Time
            if token.text.lower() in ['hours', 'minutes', 'seconds', 'hr', 'min', 'sec']:
                conditions.append(Entity(
                    text=f"{token.nbor(-1).text} {token.text}",
                    type="condition",
                    start=token.nbor(-1).idx,
                    end=token.idx + len(token.text),
                    metadata={"type": "time"}
                ))
        
        return conditions
    
    async def _structure_data(self, doc, entities: List[Entity]) -> Dict[str, Any]:
        """Convert extracted entities to structured data."""
        structured = {
            "reagents": [],
            "equipment": [],
            "conditions": {},
            "steps": []
        }
        
        for entity in entities:
            if entity.type == "reagent":
                structured["reagents"].append({
                    "name": entity.text,
                    "quantity": entity.metadata.get("quantity")
                })
            elif entity.type == "equipment":
                structured["equipment"].append(entity.text)
            elif entity.type == "condition":
                cond_type = entity.metadata.get("type", "other")
                structured["conditions"][cond_type] = entity.text
        
        # Extract steps (sentences starting with verbs)
        for sent in doc.sents:
            if sent[0].pos_ == "VERB":
                structured["steps"].append(sent.text)
        
        return structured
    
    async def _validate_sop_compliance(self, doc) -> bool:
        """Check if protocol follows SOP requirements."""
        # Basic compliance checks
        required_keywords = ['temperature', 'time', 'volume']
        text_lower = doc.text.lower()
        
        compliance = sum(1 for keyword in required_keywords if keyword in text_lower)
        return compliance >= 2
    
    async def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from free-text lab notes."""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        metadata = {
            "dates": [],
            "quantities": [],
            "locations": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "DATE":
                metadata["dates"].append(ent.text)
            elif ent.label_ == "QUANTITY":
                metadata["quantities"].append(ent.text)
            elif ent.label_ == "GPE":
                metadata["locations"].append(ent.text)
        
        return metadata
    
    async def classify_protocol(self, text: str) -> Dict[str, Any]:
        """Classify protocol type."""
        text_lower = text.lower()
        
        protocol_types = {
            "extraction": ["extract", "isolate", "purify"],
            "analysis": ["analyze", "measure", "quantify"],
            "synthesis": ["synthesize", "prepare", "react"]
        }
        
        scores = {}
        for ptype, keywords in protocol_types.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[ptype] = score
        
        classified_type = max(scores, key=scores.get) if any(scores.values()) else "unknown"
        
        return {
            "type": classified_type,
            "confidence": max(scores.values()) / len(protocol_types[classified_type]) if classified_type != "unknown" else 0.0,
            "scores": scores
        }
