import subprocess
from typing import List, Dict
from app.services.infra.powershell_service import PowerShellService
import socket
import json

class InfraService:
    """
    Logique métier pour l'audit de l'infrastructure.
    """

    @staticmethod
    def verifier_disponibilite(servers: List[str]) -> List[Dict]:
        """
        Vérification de la disponibilité (Ping) pour chaque serveur.
        """
        results = []
        for server in servers:
            try:
                # Commande ping standard (Windows)
                process = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", server],
                    capture_output=True, text=True
                )
                is_alive = process.returncode == 0
                results.append({
                    "server": server,
                    "is_alive": is_alive,
                    "status": "En ligne" if is_alive else "Hors ligne"
                })
            except Exception:
                results.append({"server": server, "is_alive": False, "status": "Erreur"})
        return results

    @staticmethod
    def verifier_port_5986(servers: List[str]) -> List[Dict]:
        """
        Vérification de l'ouverture du port 5986 (WinRM HTTPS) pour chaque serveur.
        """
        results = []
        for server in servers:
            is_open = PowerShellService.check_port(server, 5986)
            results.append({
                "server": server,
                "port": 5986,
                "is_open": is_open,
                "status": "Ouvert" if is_open else "Fermé ou Inaccessible"
            })
        return results

    @staticmethod
    def obtenir_caracteristiques_os(servers: List[str]) -> List[Dict]:
        """
        Récupération des informations OS via PowerShell.
        """
        results = []
        # Script propre sans retour à la ligne inutile avant le pipe
        script = """$os = Get-CimInstance Win32_OperatingSystem; $cpu = Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum; [PSCustomObject]@{os_name = $os.Caption; os_version = $os.Version; last_reboot = $os.LastBootUpTime.ToString('yyyy-MM-dd HH:mm:ss'); cpu_count = [int]$cpu.Sum} | ConvertTo-Json -Compress"""
        
        for server in servers:
            try:
                is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
                
                if is_local:
                    result = PowerShellService.run_command(script)
                else:
                    result = PowerShellService.run_remote_command(server, script)

                if result["success"] and result["stdout"]:
                    # Nettoyage des caractères potentiels avant/après le JSON
                    clean_stdout = result["stdout"].strip()
                    data = json.loads(clean_stdout)
                    results.append({
                        "server": server,
                        **data,
                        "is_reachable": True,
                        "error_message": None
                    })
                else:
                    results.append({
                        "server": server,
                        "os_name": "Inconnu",
                        "os_version": "Inconnu",
                        "last_reboot": "Inconnu",
                        "cpu_count": 0,
                        "is_reachable": False,
                        "error_message": result["stderr"].strip() if result["stderr"] else "Accès ou WinRM impossible"
                    })
            except Exception as e:
                results.append({
                    "server": server,
                    "os_name": "Inconnu",
                    "os_version": "Inconnu",
                    "last_reboot": "Inconnu",
                    "cpu_count": 0,
                    "is_reachable": False,
                    "error_message": f"Erreur de parsing JSON ou système: {str(e)}"
                })
        return results

    @staticmethod
    def verifier_fonctionnalites(servers: List[str], features: List[str]) -> List[Dict]:
        """
        Vérifie si les fonctionnalités Windows (IIS, etc.) sont installées.
        """
        results = []
        feature_list_str = "'" + "','".join(features) + "'"
        script = f"Get-WindowsFeature -Name {feature_list_str} | Select-Object Name, Installed | ConvertTo-Json -Compress"
        
        for server in servers:
            is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
            
            if is_local:
                result = PowerShellService.run_command(script)
            else:
                result = PowerShellService.run_remote_command(server, script)

            if result["success"] and result["stdout"]:
                try:
                    data = json.loads(result["stdout"].strip())
                    if isinstance(data, dict):
                        data = [data]
                    for item in data:
                        results.append({
                            "server": server,
                            "feature": item.get("Name"),
                            "is_installed": item.get("Installed", False)
                        })
                except:
                    results.append({"server": server, "feature": "Error", "is_installed": False})
            else:
                for f in features:
                    results.append({
                        "server": server,
                        "feature": f,
                        "is_installed": False
                    })
        return results
