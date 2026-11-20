import logging
from typing import List
from sqlalchemy.orm import Session
from app.database.models import Alert
from app.detection.port_scan_detector import PortScanDetector
from app.detection.brute_force_detector import BruteForceDetector
from app.detection.suspicious_connection_detector import SuspiciousConnectionDetector
from app.detection.anomaly_detector import AnomalyDetector

logger = logging.getLogger("hackthehacker.rule_engine")

class DetectionEngine:
    """
    Central orchestration engine for rules and analytic detectors.
    Executes detection passes across recent events.
    """

    def __init__(self):
        self.port_scan_detector = PortScanDetector()
        self.brute_force_detector = BruteForceDetector()
        self.suspicious_detector = SuspiciousConnectionDetector()
        self.anomaly_detector = AnomalyDetector()

    def run_all(self, db: Session) -> List[Alert]:
        """Runs all enabled detection modules sequentially."""
        all_alerts: List[Alert] = []

        try:
            alerts = self.port_scan_detector.analyze(db)
            all_alerts.extend(alerts)
        except Exception as e:
            logger.error(f"Error in PortScanDetector: {e}")

        try:
            alerts = self.brute_force_detector.analyze(db)
            all_alerts.extend(alerts)
        except Exception as e:
            logger.error(f"Error in BruteForceDetector: {e}")

        try:
            alerts = self.suspicious_detector.analyze(db)
            all_alerts.extend(alerts)
        except Exception as e:
            logger.error(f"Error in SuspiciousConnectionDetector: {e}")

        try:
            alerts = self.anomaly_detector.analyze(db)
            all_alerts.extend(alerts)
        except Exception as e:
            logger.error(f"Error in AnomalyDetector: {e}")

        return all_alerts
