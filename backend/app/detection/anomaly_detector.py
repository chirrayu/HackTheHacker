import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Event, Alert

logger = logging.getLogger("hackthehacker.detector.anomaly")

class AnomalyDetector:
    """
    Machine Learning Anomaly Detection Interface using Scikit-Learn Isolation Forest.
    Analyzes multi-dimensional traffic feature vectors (packet rates, port variance, connection bursts).
    Notice: Anomaly scores indicate statistical deviation from baseline, NOT conclusive proof of an attack.
    """

    MODEL_VERSION = "isoforest-v1.0.0"

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = None

    def extract_features(self, db: Session, window_minutes: int = 15) -> Dict[str, Dict[str, float]]:
        """
        Extracts behavioral feature vectors per source IP:
        1. Event count (frequency)
        2. Unique destination ports accessed (diversity)
        3. Unique destination IPs (breadth)
        """
        since = datetime.utcnow() - timedelta(minutes=window_minutes)
        events = db.query(Event).filter(Event.timestamp >= since).all()

        profiles: Dict[str, Dict[str, Any]] = {}
        for ev in events:
            src = ev.source_ip
            if src not in profiles:
                profiles[src] = {
                    "events": 0,
                    "ports": set(),
                    "targets": set()
                }
            profiles[src]["events"] += 1
            if ev.destination_port:
                profiles[src]["ports"].add(ev.destination_port)
            profiles[src]["targets"].add(ev.destination_ip)

        features = {}
        for src, p in profiles.items():
            features[src] = {
                "event_count": float(p["events"]),
                "unique_ports": float(len(p["ports"])),
                "unique_targets": float(len(p["targets"]))
            }

        return features

    def analyze(self, db: Session) -> List[Alert]:
        """Runs Isolation Forest on extracted features and generates explainable anomaly alerts."""
        features = self.extract_features(db)
        if len(features) < 3:
            # Need minimum sample size for unsupervised outlier detection
            return []

        ips = list(features.keys())
        X = np.array([[f["event_count"], f["unique_ports"], f["unique_targets"]] for f in features.values()])

        alerts = []
        try:
            from sklearn.ensemble import IsolationForest
            clf = IsolationForest(contamination=self.contamination, random_state=42)
            clf.fit(X)
            preds = clf.predict(X)  # -1 for anomaly, 1 for normal
            scores = clf.decision_function(X)

            for idx, pred in enumerate(preds):
                if pred == -1:
                    src_ip = ips[idx]
                    anomaly_score = float(scores[idx])
                    feat = features[src_ip]

                    evidence = {
                        "model_version": self.MODEL_VERSION,
                        "anomaly_score": round(anomaly_score, 4),
                        "features": feat,
                        "evaluation_metric": "Isolation Forest Decision Function Distance",
                        "explainability_limitations": "Statistical deviation does not constitute definitive proof of malicious intent."
                    }

                    alert = Alert(
                        alert_type="ml_traffic_anomaly",
                        title=f"Traffic Behavior Anomaly Detected ({src_ip})",
                        description=f"Host {src_ip} exhibited abnormal traffic features (Score: {anomaly_score:.3f}).",
                        severity="Moderate",
                        source_ip=src_ip,
                        destination_ip="Multiple/Network",
                        status="new",
                        confidence=0.75,
                        evidence=json.dumps(evidence),
                        created_at=datetime.utcnow()
                    )
                    db.add(alert)
                    alerts.append(alert)

            if alerts:
                db.commit()
                logger.info(f"AnomalyDetector generated {len(alerts)} alerts.")

        except ImportError:
            logger.warning("Scikit-learn not available. Skipping ML anomaly phase.")
        except Exception as e:
            logger.error(f"Anomaly detection encountered error: {e}")

        return alerts
