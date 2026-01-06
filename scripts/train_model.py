"""
Model Training Script
"""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.ml.anomaly_detector import AnomalyDetector

def generate_sample_data(n_samples=1000):
    """Generate synthetic laboratory data."""
    n_normal = int(n_samples * 0.9)
    normal_data = np.random.normal(loc=[7.0, 25.0, 1.0, 50.0], 
                                   scale=[0.5, 2.0, 0.1, 5.0], 
                                   size=(n_normal, 4))
    
    n_anomaly = n_samples - n_normal
    anomaly_data = np.random.uniform(low=[0.0, -10.0, 0.0, 0.0],
                                     high=[14.0, 100.0, 10.0, 200.0],
                                     size=(n_anomaly, 4))
    
    X_train = np.vstack([normal_data, anomaly_data])
    y_train = np.array([1] * n_normal + [-1] * n_anomaly)
    
    shuffle_idx = np.random.permutation(len(X_train))
    return X_train[shuffle_idx], y_train[shuffle_idx]

def main():
    print("Training anomaly detection model...")
    X_train, y_train = generate_sample_data(1000)
    
    detector = AnomalyDetector()
    detector.train(X_train)
    
    metrics = detector.evaluate(X_train, y_train)
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"F1 Score: {metrics['f1_score']:.3f}")
    
    detector.save()
    print("Model saved successfully")

if __name__ == "__main__":
    main()
