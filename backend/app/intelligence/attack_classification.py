from typing import Dict, Any

class AttackClassificationEngine:
    """
    Classifies threat patterns against standardized MITRE ATT&CK techniques.
    """

    TECHNIQUE_MAPPINGS = {
        "port_scan": {
            "technique_id": "T1046",
            "technique_name": "Network Service Discovery",
            "tactic": "Discovery",
            "description": "Adversary attempting to get a listing of services running on remote hosts."
        },
        "brute_force": {
            "technique_id": "T1110",
            "technique_name": "Brute Force",
            "tactic": "Credential Access",
            "description": "Adversary attempting authentication via systematic password guessing."
        },
        "suspicious_port_access": {
            "technique_id": "T1190",
            "technique_name": "Exploit Public-Facing Application",
            "tactic": "Initial Access",
            "description": "Access directed towards high-risk, legacy, or backdoor management interfaces."
        },
        "icmp_recon": {
            "technique_id": "T1018",
            "technique_name": "Remote System Discovery",
            "tactic": "Discovery",
            "description": "Adversary attempting to identify active host IP addresses on the subnet."
        }
    }

    @classmethod
    def get_classification(cls, alert_type: str) -> Dict[str, str]:
        return cls.TECHNIQUE_MAPPINGS.get(alert_type, {
            "technique_id": "T1000",
            "technique_name": "Uncategorized Threat Activity",
            "tactic": "Unknown",
            "description": "Unclassified network event pattern."
        })
