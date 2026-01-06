"""
Anomaly Detection Model
Uses Isolation Forest for detecting unusual patterns in laboratory data
"""

import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """ML model for detecting anomalies in laboratory test results."""
    
    def __init__(self, model_path: str = "app/ml/models/anomaly_detector.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.feature_names = ['pH', 'temperature', 'concentration', 'volume']
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model or create new one."""
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                logger.info("Loaded pre-trained anomaly detection model")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self._create_default_model()
        else:
            self._create_default_model()
    
    def _create_default_model(self):
        """Create default Isolation Forest model."""
        self.model = IsolationForest(
            contamination=0.1,
            n_estimators=100,
            max_samples='auto',
            random_state=42
        )
        logger.info("Created default anomaly detection model")
    
    def detect(self, data: Dict[str, Any]) -> float:
        """
        Detect anomalies in sample data.
        
        Args:
            data: Sample data dictionary
            
        Returns:
            Anomaly score (0-1, higher = more anomalous)
        """
        try:
            features = self._extract_features(data)
            if features is None:
                return 0.5
            
            # Reshape for single prediction
            features_array = np.array(features).reshape(1, -1)
            
            # Get anomaly score
            # Isolation Forest returns -1 for anomalies, 1 for normal
            prediction = self.model.predict(features_array)[0]
            
            # Get decision function score (distance from threshold)
            score = self.model.decision_function(features_array)[0]
            
            # Normalize to 0-1 range (higher = more anomalous)
            # Typical scores range from -0.5 to 0.5
            normalized_score = max(0.0, min(1.0, (-score + 0.5)))
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return 0.5
    
    def _extract_features(self, data: Dict[str, Any]) -> list:
        """Extract numeric features from data."""
        features = []
        
        for feature_name in self.feature_names:
            value = data.get(feature_name, 0.0)
            if isinstance(value, (int, float)):
                features.append(float(value))
            else:
                features.append(0.0)
        
        return features if len(features) == len(self.feature_names) else None
    
    def train(self, training_data: np.ndarray):
        """
        Train the anomaly detection model.
        
        Args:
            training_data: Array of shape (n_samples, n_features)
        """
        try:
            self.model.fit(training_data)
            logger.info(f"Trained model on {len(training_data)} samples")
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def save(self):
        """Save trained model to disk."""
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"Saved model to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def evaluate(self, test_data: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            test_data: Test samples
            labels: True labels (1 = normal, -1 = anomaly)
            
        Returns:
            Dictionary with evaluation metrics
        """
        predictions = self.model.predict(test_data)
        
        # Calculate metrics
        correct = np.sum(predictions == labels)
        accuracy = correct / len(labels)
        
        # True positives, false positives, etc.
        tp = np.sum((predictions == -1) & (labels == -1))
        fp = np.sum((predictions == -1) & (labels == 1))
        tn = np.sum((predictions == 1) & (labels == 1))
        fn = np.sum((predictions == 1) & (labels == -1))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1
        }
