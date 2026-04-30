from typing import List, Dict, Optional
from app.services.batch.service import BatchService

class CRMService:
    @staticmethod
    def verifier_services_crm(servers: List[str], username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Lister les services Microsoft Dynamics CRM et leurs comptes de démarrage.
        """
        crm_services = ["MSCRMAsyncService", "MSCRMSandboxService"]
        return BatchService.verifier_services_windows(servers, crm_services, username, password)
