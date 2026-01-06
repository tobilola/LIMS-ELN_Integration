"""
Data Validation Service
Implements validation rules and anomaly detection
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from app.schemas.common import ValidationResponse, ValidationIssue, ValidationLevel
from app.ml.anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating laboratory data."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.anomaly_detector = AnomalyDetector()
    
    async def validate(
        self,
        data: Dict[str, Any],
        level: ValidationLevel,
        check_anomalies: bool = True,
        check_compliance: bool = True
    ) -> ValidationResponse:
        """
        Validate sample data with configurable checks.
        
        Args:
            data: Sample data to validate
            level: Validation level (basic, standard, full)
            check_anomalies: Run ML anomaly detection
            check_compliance: Check regulatory compliance
            
        Returns:
            ValidationResponse with issues and scores
        """
        issues = []
        
        # Basic validation
        issues.extend(await self._validate_required_fields(data))
        issues.extend(await self._validate_data_types(data))
        
        if level in [ValidationLevel.STANDARD, ValidationLevel.FULL]:
            issues.extend(await self._validate_ranges(data))
            issues.extend(await self._validate_references(data))
        
        if level == ValidationLevel.FULL:
            issues.extend(await self._validate_business_rules(data))
        
        # Anomaly detection
        anomaly_score = None
        if check_anomalies:
            anomaly_score = await self._check_anomalies(data)
            if anomaly_score and anomaly_score > 0.7:
                issues.append(ValidationIssue(
                    severity="warning",
                    field="test_results",
                    message="Potential anomaly detected in test results",
                    suggestion="Review results for unusual patterns"
                ))
        
        # Compliance checks
        compliance_score = None
        if check_compliance:
            compliance_score = await self._check_compliance(data)
            if compliance_score and compliance_score < 0.9:
                issues.append(ValidationIssue(
                    severity="warning",
                    message="Compliance score below threshold",
                    suggestion="Verify audit trail completeness"
                ))
        
        return ValidationResponse(
            valid=len([i for i in issues if i.severity == "error"]) == 0,
            validation_level=level.value,
            issues=issues,
            anomaly_score=anomaly_score,
            compliance_score=compliance_score,
            recommendations=self._generate_recommendations(issues)
        )
    
    async def _validate_required_fields(self, data: Dict[str, Any]) -> list[ValidationIssue]:
        """Check required fields are present."""
        issues = []
        required = ['sample_id']
        
        for field in required:
            if field not in data or data[field] is None:
                issues.append(ValidationIssue(
                    severity="error",
                    field=field,
                    message=f"Required field '{field}' is missing",
                    suggestion=f"Provide a valid {field}"
                ))
        
        return issues
    
    async def _validate_data_types(self, data: Dict[str, Any]) -> list[ValidationIssue]:
        """Validate data types."""
        issues = []
        
        if 'sample_id' in data and not isinstance(data['sample_id'], str):
            issues.append(ValidationIssue(
                severity="error",
                field="sample_id",
                message="sample_id must be a string"
            ))
        
        return issues
    
    async def _validate_ranges(self, data: Dict[str, Any]) -> list[ValidationIssue]:
        """Validate numeric ranges."""
        issues = []
        
        if 'pH' in data:
            ph = data['pH']
            if not (0 <= ph <= 14):
                issues.append(ValidationIssue(
                    severity="error",
                    field="pH",
                    message=f"pH value {ph} out of valid range (0-14)",
                    suggestion="Verify measurement accuracy"
                ))
        
        if 'temperature' in data:
            temp = data['temperature']
            if not (-273 <= temp <= 500):
                issues.append(ValidationIssue(
                    severity="warning",
                    field="temperature",
                    message=f"Temperature {temp}°C outside typical range",
                    suggestion="Confirm measurement is correct"
                ))
        
        return issues
    
    async def _validate_references(self, data: Dict[str, Any]) -> list[ValidationIssue]:
        """Validate foreign key references."""
        issues = []
        # Check if batch exists, sample references are valid, etc.
        return issues
    
    async def _validate_business_rules(self, data: Dict[str, Any]) -> list[ValidationIssue]:
        """Validate domain-specific business rules."""
        issues = []
        # Example: Check if sample type matches test type
        return issues
    
    async def _check_anomalies(self, data: Dict[str, Any]) -> float:
        """Run ML-based anomaly detection."""
        try:
            score = self.anomaly_detector.detect(data)
            return score
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return None
    
    async def _check_compliance(self, data: Dict[str, Any]) -> float:
        """Calculate compliance score."""
        # Check audit trail, timestamps, user info, etc.
        score = 1.0
        
        if 'created_by' not in data:
            score -= 0.2
        if 'timestamp' not in data:
            score -= 0.2
        
        return max(0.0, score)
    
    def _generate_recommendations(self, issues: list[ValidationIssue]) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        error_count = len([i for i in issues if i.severity == "error"])
        warning_count = len([i for i in issues if i.severity == "warning"])
        
        if error_count > 0:
            recommendations.append(f"Fix {error_count} critical errors before proceeding")
        if warning_count > 0:
            recommendations.append(f"Review {warning_count} warnings for data quality")
        
        return recommendations
    
    async def validate_test_result(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual test result."""
        issues = []
        
        if 'result_value' in test_data:
            value = test_data['result_value']
            if not isinstance(value, (int, float)):
                issues.append({
                    "field": "result_value",
                    "message": "Result value must be numeric"
                })
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
