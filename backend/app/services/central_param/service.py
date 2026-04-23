import requests
import re
from urllib.parse import urlparse
from zeep import Client
from zeep.exceptions import Fault
from sqlalchemy.orm import Session
from app.models.verification import VerificationConfigurations
from typing import List, Dict, Optional

class CentralParamService:
    @staticmethod
    def verifier_syntaxe_url(url: str) -> bool:
        """
        Valider la syntaxe de l'URL CentralParam (http/https + domaine/hostname).
        """
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme in ['http', 'https'] and parsed_url.netloc)

    @staticmethod
    def verifier_service_soap(url: str) -> Dict:
        """
        Vérifier que l'URL est un service SVC/WCF valide et tester son état de santé.
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                is_wcf = "Service" in response.text or "WCF" in response.text or "xml" in response.headers.get("Content-Type", "").lower()
                
                health_check = "Inconnu"
                if is_wcf:
                    try:
                        # On tente de voir si le service répond à une requête de paramètres
                        # S'il répond count=0, c'est peut-être une config "blanche"
                        params = CentralParamService.extraire_parametres(url)
                        health_check = "OK" if len(params) > 0 else "Config Vide (Page Blanche probable)"
                    except Exception:
                        health_check = "Erreur Appel SOAP"

                return {
                    "is_valid": True,
                    "is_wcf": is_wcf,
                    "status_code": 200,
                    "health_check": health_check,
                    "message": "Service accessible" if is_wcf else "Réponse non spécifique au service SVC"
                }
            return {
                "is_valid": False,
                "is_wcf": False,
                "status_code": response.status_code,
                "health_check": "Indisponible",
                "message": f"Échec de la connexion, code: {response.status_code}"
            }
        except Exception as e:
            return {
                "is_valid": False,
                "is_wcf": False,
                "status_code": 0,
                "health_check": "Erreur",
                "message": str(e)
            }

    @staticmethod
    def verifier_service_wcf(url: str) -> Dict:
        """
        Vérifier que l'URL est un service SVC/WCF valide.
        """
        try:
            response = requests.get(url, timeout=10)
            # Un service WCF renvoie généralement du HTML explicatif ou du XML/WSDL
            is_wcf = (
                response.status_code == 200 and 
                ("Service" in response.text or "WCF" in response.text or "xml" in response.headers.get("Content-Type", "").lower())
            )
            return {
                "is_valid": response.status_code == 200,
                "is_wcf": is_wcf,
                "status_code": response.status_code,
                "message": "Service WCF détecté" if is_wcf else "Service accessible mais non identifié comme WCF"
            }
        except Exception as e:
            return {
                "is_valid": False,
                "is_wcf": False,
                "status_code": 0,
                "message": f"Erreur de connexion : {str(e)}"
            }

    @staticmethod
    def avoir_configuration_soap(url: str):
        """
        Découverte dynamique du service et du port SOAP dans le WSDL.
        """
        wsdl = url if url.lower().endswith('?wsdl') else url + '?wsdl'
        try:
            client = Client(wsdl=wsdl)
        except Exception as e:
            # Tentative alternative si ?wsdl échoue (ex: ?singleWsdl)
            if '?wsdl' in wsdl:
                alternative_wsdl = wsdl.replace('?wsdl', '?singleWsdl')
                try:
                    client = Client(wsdl=alternative_wsdl)
                    wsdl = alternative_wsdl
                except:
                    raise ValueError(f"Impossible de charger le WSDL depuis {url} : {str(e)}")
            else:
                raise ValueError(f"Erreur WSDL : {str(e)}")

        service_name = None
        service_port = None

        # Parcours des services pour trouver un port disponible
        if client.wsdl.services:
            for service in client.wsdl.services.values():
                service_name = service.name
                if service.ports:
                    for port in service.ports.values():
                        service_port = port.name
                        break
                if service_name and service_port:
                    break
        
        if not service_name or not service_port:
            # Si zeep ne trouve pas de service dans client.wsdl.services, 
            # on essaie de voir si on peut binder directement si on connaît le nom (cas rare)
            # Sinon, on lève une erreur explicite.
            raise ValueError(f"Aucun service ou port SOAP trouvé dans le WSDL ({wsdl}). Vérifiez la structure du service.")
        
        return client, service_name, service_port

    @staticmethod
    def parse_key_value(value: str) -> Dict[str, str]:
        """
        Parsing des chaînes type Clé=Valeur;Clé2=Valeur2.
        Supporte les espaces et les points-virgules de fin.
        """
        if not value or "=" not in value:
            return None
        
        parts = {}
        # Nettoyage et découpage
        pairs = [p.strip() for p in value.split(';') if p.strip()]
        for pair in pairs:
            if '=' in pair:
                kv = pair.split('=', 1) # On s'arrête au premier = pour la valeur
                key = kv[0].strip()
                val = kv[1].strip()
                if key:
                    parts[key] = val
        return parts if parts else None

    @staticmethod
    def extraire_parametres(url: str, filter_list: Optional[List[str]] = None) -> List[Dict]:
        """
        Méthode principale pour appeler le service SOAP GetParameter.
        """
        client, service_name, service_port = CentralParamService.avoir_configuration_soap(url)
        service = client.bind(service_name, service_port)

        # Les types SOAP sont souvent préfixés (ns2 dans l'ancienne implémentation)
        # On essaie de les récupérer dynamiquement si possible, sinon via namespace
        try:
            ArrayOfParameter = client.get_type('ns2:ArrayOfParameter')
            Parameter = client.get_type('ns2:Parameter')
        except:
            # Fallback : essayer de trouver le type sans préfixe ou chercher dans le cycle des types
            raise RuntimeError("Types SOAP 'ArrayOfParameter' ou 'Parameter' introuvables dans le WSDL.")

        items_to_request = []
        if filter_list:
            for name in filter_list:
                items_to_request.append(Parameter(ParamName=name))
        
        # Appel SOAP
        # Note: L'ancienne implémentation utilisait '_prameters' (faute incluse)
        # On garde cette compatibilité si le service backend l'exige
        try:
            array_of_params = ArrayOfParameter(items_to_request)
            response = service.GetParameter(_prameters=array_of_params)
        except Exception as e:
            raise RuntimeError(f"Échec de l'appel SOAP GetParameter : {str(e)}")

        results = []
        # Extraction sécurisée (Note: 'ListOfParmeters' avec faute incluse dans le service réel)
        list_of_params = getattr(response, 'ListOfParmeters', None)
        if list_of_params:
            parameter_list = getattr(list_of_params, 'Parameter', [])
            for p in parameter_list:
                name = getattr(p, 'ParamName', None)
                val = getattr(p, 'ParamValue', "")
                if val is None:
                    val = ""
                if name:
                    results.append({
                        "name": name,
                        "value": val,
                        "parsed_values": CentralParamService.parse_key_value(val)
                    })
        return results

    @staticmethod
    def enregistrer_snapshot(db: Session, url: str, param: Dict, username: str):
        """
        Enregistrer une capture du paramètre en base de données.
        """
        db_config = VerificationConfigurations(
            wsdl_url=url,
            param_name=param["name"],
            param_value=param["value"],
            parsed_json=param.get("parsed_values"),
            created_by=username
        )
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        return db_config
