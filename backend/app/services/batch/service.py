import socket
import json
import requests
from typing import List, Dict, Optional
from app.services.infra.powershell_service import PowerShellService

class BatchService:
    @staticmethod
    def verifier_services_windows(servers: List[str], service_names: List[str], username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Vérifie l'état des services Windows. Supporte les wildcards (ex: SAPHIRV3*).
        """
        results = []
        # Support des wildcards : on entoure les noms de guillemets et on laisse PowerShell faire le matching
        service_list_str = ",".join([f"'{s}'" for s in service_names])
        script = f"Get-Service -Name {service_list_str} -ErrorAction SilentlyContinue | Select-Object Name, DisplayName, Status | ConvertTo-Json -Compress"
        
        for server in servers:
            try:
                is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
                
                if is_local:
                    result = PowerShellService.run_command(script)
                else:
                    result = PowerShellService.run_remote_command(server, script, username, password)

                services_data = []
                if result["success"] and result["stdout"]:
                    raw_data = json.loads(result["stdout"].strip())
                    # Normalisation (si 1 seul service, c'est un dict, sinon une liste)
                    if isinstance(raw_data, dict):
                        raw_data = [raw_data]
                    
                    # Mapping des statuts Windows (1=Stopped, 4=Running, etc.)
                    status_map = {
                        1: "Stopped",
                        2: "StartPending",
                        3: "StopPending",
                        4: "Running",
                        5: "ContinuePending",
                        6: "PausePending",
                        7: "Paused"
                    }
                    
                    for item in raw_data:
                        raw_status = item.get("Status")
                        services_data.append({
                            "name": item.get("Name"),
                            "display_name": item.get("DisplayName"),
                            "status": status_map.get(raw_status, f"Unknown ({raw_status})"),
                            "is_running": raw_status == 4
                        })
                
                # Gérer les services non trouvés
                found_names = [s["name"].lower() for s in services_data]
                for name in service_names:
                    if name.lower() not in found_names:
                        services_data.append({
                            "name": name,
                            "display_name": f"{name} (Non trouvé)",
                            "status": "Missing",
                            "is_running": False
                        })

                results.append({
                    "server": server,
                    "services": services_data,
                    "is_reachable": result["success"],
                    "error_message": result["stderr"] if not result["success"] else None
                })
            except Exception as e:
                results.append({
                    "server": server,
                    "services": [],
                    "is_reachable": False,
                    "error_message": str(e)
                })
        return results

    @staticmethod
    def verifier_datetime(servers: List[str], username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Récupère la date et l'heure de chaque serveur.
        """
        results = []
        script = "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"
        
        for server in servers:
            is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
            if is_local:
                result = PowerShellService.run_command(script)
            else:
                result = PowerShellService.run_remote_command(server, script, username, password)
                
            results.append({
                "server": server,
                "current_time": result["stdout"].strip() if result["success"] else "Inaccessible",
                "is_reachable": result["success"]
            })
        return results

    @staticmethod
    def verifier_existence_fichiers(servers: List[str], paths: List[str], username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Vérifie si des fichiers (ex: critères) existent sur les serveurs.
        """
        results = []
        for server in servers:
            for path in paths:
                # Échapper les antislashs pour PowerShell
                safe_path = path.replace("\\", "\\\\")
                script = f"Test-Path -Path '{safe_path}'"
                
                is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
                if is_local:
                    result = PowerShellService.run_command(script)
                else:
                    result = PowerShellService.run_remote_command(server, script, username, password)
                
                exists = result["stdout"].strip().lower() == "true" if result["success"] else False
                results.append({
                    "server": server,
                    "path": path,
                    "exists": exists
                })
        return results

    @staticmethod
    def auditer_dynamique_saphir(servers: List[str], search_roots: List[str], username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Audit en mode découverte automatique (recherche .config, critères et pools).
        """
        results = []
        roots_str = "'" + "','".join(search_roots) + "'"
        script = (
            "Import-Module WebAdministration -ErrorAction SilentlyContinue; "
            "$roots = " + roots_str + "; "
            "$configs = Get-ChildItem -Path $roots -Filter '*.config' -Recurse -Depth 4 -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'Saphir|Web.config|App.config' }; "
            "$found_configs = foreach ($f in $configs) { "
            "  try { "
            "    [xml]$xml = Get-Content $f.FullName -ErrorAction SilentlyContinue; "
            "    $crit = $xml.configuration.appSettings.add | Where-Object { $_.key -eq 'PARAMCRIT0001' } | Select-Object -ExpandProperty value; "
            "    $ep = $xml.configuration.appSettings.add | Where-Object { $_.key -eq 'CentralisationParamEndPoint' } | Select-Object -ExpandProperty value; "
            "    $exists = if($crit) { Test-Path (Join-Path $f.DirectoryName $crit) } else { $false }; "
            "    @{ file_path=$f.FullName; param_crit_0001=$crit; critere_file_exists=$exists; central_param_endpoint=$ep } "
            "  } catch { continue } "
            "}; "
            "$pools = if(Get-Module WebAdministration) { Get-ChildItem IIS:\\AppPools | Select-Object Name, State } else { @() }; "
            "[PSCustomObject]@{ configs_found=$found_configs; iis_pools=$pools | ForEach-Object { @{ name=$_.Name; state=$_.State } } } | ConvertTo-Json -Compress"
        )

        for server in servers:
            try:
                is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
                if is_local:
                    result = PowerShellService.run_command(script)
                else:
                    result = PowerShellService.run_remote_command(server, script, username, password)

                if result["success"] and result["stdout"]:
                    clean_stdout = result["stdout"].strip()
                    data = json.loads(clean_stdout)
                    results.append({
                        "server": server,
                        "configs_found": data.get("configs_found", []),
                        "iis_pools": data.get("iis_pools", []),
                        "is_reachable": True
                    })
                else:
                    results.append({"server": server, "configs_found": [], "iis_pools": [], "is_reachable": False})
            except Exception:
                results.append({"server": server, "configs_found": [], "iis_pools": [], "is_reachable": False})
        return results

    @staticmethod
    def tester_connexion_sql_remote(servers: List[str], sql_instance: str, port: int = 1433, username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Teste si le serveur Batch peut atteindre l'instance SQL spécifiée.
        """
        results = []
        target_host = sql_instance.split("\\")[0]
        script = f"Test-NetConnection -ComputerName '{target_host}' -Port {port} | Select-Object TcpTestSucceeded | ConvertTo-Json -Compress"

        for server in servers:
            is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
            if is_local:
                result = PowerShellService.run_command(script)
            else:
                result = PowerShellService.run_remote_command(server, script, username, password)
            
            port_open = False
            if result["success"] and result["stdout"]:
                data = json.loads(result["stdout"].strip())
                port_open = data.get("TcpTestSucceeded", False)
            
            results.append({
                "server": server,
                "sql_instance": sql_instance,
                "is_reachable": result["success"],
                "port_open": port_open
            })
        return results
