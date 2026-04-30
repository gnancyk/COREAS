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
        script = f"Get-CimInstance Win32_Service -Filter \"Name LIKE '{service_names[0].replace('*', '%')}'\" | Select-Object Name, DisplayName, State, StartName | ConvertTo-Json -Compress"
        # Note: Si plusieurs noms ou wildcards complexes, on ajuste le script
        if len(service_names) > 1 or "*" in service_names[0]:
            filter_parts = " OR ".join([f"Name LIKE '{s.replace('*', '%')}'" for s in service_names])
            script = f"Get-CimInstance Win32_Service -Filter \"{filter_parts}\" | Select-Object Name, DisplayName, State, StartName | ConvertTo-Json -Compress"
        
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
                    if isinstance(raw_data, dict):
                        raw_data = [raw_data]
                    
                    for item in raw_data:
                        services_data.append({
                            "name": item.get("Name"),
                            "display_name": item.get("DisplayName"),
                            "status": item.get("State"),
                            "start_account": item.get("StartName"),
                            "is_running": item.get("State") == "Running"
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
    def verifier_sante_http(urls: List[str]) -> List[Dict]:
        """
        Vérifie les réponses HTTP (200 OK) pour une liste d'URLs.
        """
        results = []
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                results.append({
                    "url": url,
                    "status_code": response.status_code,
                    "is_healthy": response.status_code == 200,
                    "message": "En ligne" if response.status_code == 200 else f"Erreur HTTP {response.status_code}"
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "status_code": 0,
                    "is_healthy": False,
                    "message": str(e)
                })
        return results

    @staticmethod
    def auditer_dynamique_saphir(servers: List[str], search_roots: List[str], username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Audit en mode découverte automatique (recherche .config, critères et pools).
        """
        results = []
        # Ajout des chemins Program Files si non présents
        standard_roots = ['C:\\inetpub', 'C:\\Program Files\\gs2E2', 'C:\\Program Files (x86)\\gs2E2']
        all_roots = list(set(search_roots + standard_roots))
        roots_str = "'" + "','".join(all_roots).replace("\\", "\\\\") + "'"
        
        script = (
            "Import-Module WebAdministration -ErrorAction SilentlyContinue; "
            "$roots = @(" + roots_str + "); "
            # Recherche de web.config et *.exe.config dans les dossiers SAPHIRV3
            "$configs = Get-ChildItem -Path $roots -Include 'web.config','*.exe.config' -Recurse -Depth 5 -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'SAPHIRV3' }; "
            "$found_configs = foreach ($f in $configs) { "
            "  try { "
            "    [xml]$xml = Get-Content $f.FullName -ErrorAction SilentlyContinue; "
            "    $ep = $xml.configuration.appSettings.add | Where-Object { $_.key -eq 'CentralisationParamEndPoint' } | Select-Object -ExpandProperty value; "
            "    @{ file_path=$f.FullName; central_param_endpoint=$ep } "
            "  } catch { continue } "
            "}; "
            "$pools = if(Get-Module WebAdministration) { Get-ChildItem IIS:\\AppPools | Where-Object { $_.Name -like 'SAPHIRV3*' } } else { @() }; "
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
                    
                    # Sécurisation des types pour éviter ResponseValidationError
                    configs = data.get("configs_found", [])
                    if isinstance(configs, dict): configs = [configs] if configs else []
                    
                    pools = data.get("iis_pools", [])
                    if isinstance(pools, dict): pools = [pools] if pools else []

                    results.append({
                        "server": server,
                        "configs_found": configs,
                        "iis_pools": pools,
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

    @staticmethod
    def _extract_server_and_path(path: str, discovery_map: Dict, target_servers: Optional[List[str]]):
        """Helper pour parser les UNC et peupler la map de découverte."""
        import re
        # Support pour \\Host, \\\\Host ou n'importe quel nombre de \ au début
        match = re.match(r"^\\+([^\\]+)(.*)", path)
        if match:
            srv = match.group(1).upper()
            remaining_path = match.group(2).replace("\\\\", "\\") # Nettoyage des doubles backslashes
            
            # Traduction UNC Admin Share (ex: \C$\SaphirV3 -> C:\SaphirV3)
            local_path = remaining_path
            admin_share_match = re.match(r"^\\([A-Z])\$(.*)", remaining_path, re.IGNORECASE)
            if admin_share_match:
                drive = admin_share_match.group(1)
                subpath = admin_share_match.group(2)
                local_path = f"{drive}:{subpath}"
            elif remaining_path.startswith("\\") and len(remaining_path) > 1:
                # Si c'est un partage simple (ex: \SaphirV3), on suppose C:\SaphirV3
                local_path = "C:" + remaining_path
            
            if srv not in discovery_map: discovery_map[srv] = []
            # On stocke le chemin traduit pour l'exécution locale
            discovery_map[srv].append(local_path if local_path else path)
        else:
            actual_srvs = target_servers if target_servers else ["localhost"]
            for s in actual_srvs:
                if s not in discovery_map: discovery_map[s] = []
                discovery_map[s].append(path)

    @staticmethod
    def verifier_conformite_centralisation(servers: Optional[List[str]], central_param_url: str, modules: Optional[List[str]] = None, search_paths: Optional[List[str]] = None, username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Audit de conformité : localise les serveurs et les fichiers .config via CentralParam OU via chemins directs.
        """
        from app.services.central_param.service import CentralParamService

        # Map pour stocker : server -> list of paths
        discovery_map = {}
        if servers:
            for s in servers: discovery_map[s] = []

        # 1. Traitement des chemins fournis manuellement
        if search_paths:
            for path in search_paths:
                BatchService._extract_server_and_path(path, discovery_map, servers)

        # 2. Découverte via CentralParam (si modules fournis)
        if modules:
            try:
                for mod in modules:
                    params = CentralParamService.extraire_parametres(central_param_url, filter_list=[mod])
                    if params:
                        for p in params:
                            name = p.get("name", "")
                            value = p.get("value", "")
                            
                            if "directory" in name.lower() or "path" in name.lower():
                                if value and value.strip():
                                    BatchService._extract_server_and_path(value, discovery_map, servers)
                            
                            if p.get("parsed_values"):
                                for key, path in p["parsed_values"].items():
                                    if "directory" in key.lower() or "path" in key.lower():
                                        BatchService._extract_server_and_path(path, discovery_map, servers)
            except Exception:
                pass

        # Fallback si rien trouvé
        if not discovery_map:
            discovery_map["localhost"] = ["C:\\inetpub"]

        final_results = []
        for server, paths in discovery_map.items():
            actual_paths = list(set(paths)) if paths else ["C:\\inetpub"]
            roots_str = "'" + "','".join(actual_paths).replace("\\", "\\\\") + "'"
            
            script = (
                f"$roots = @({roots_str}); "
                "$configs = Get-ChildItem -Path $roots -Filter 'web.config' -Recurse -Depth 5 -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'SAPHIRV3' }; "
                "$results = foreach ($f in $configs) { "
                "  try { "
                "    [xml]$xml = Get-Content $f.FullName -ErrorAction SilentlyContinue; "
                "    $ep = $xml.configuration.appSettings.add | Where-Object { $_.key -eq 'CentralisationParamEndPoint' } | Select-Object -ExpandProperty value; "
                "    if($ep) { @{ file=$f.FullName; endpoint=$ep } } "
                "  } catch { } "
                "}; "
                "if($results) { $results | ConvertTo-Json -Compress } else { '[]' }"
            )

            try:
                is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
                result = PowerShellService.run_command(script) if is_local else PowerShellService.run_remote_command(server, script, username, password)

                if result["success"] and result["stdout"]:
                    data = json.loads(result["stdout"].strip())
                    if isinstance(data, dict): data = [data]
                    for entry in data:
                        local_ep = entry.get("endpoint")
                        final_results.append({
                            "server": server,
                            "config_file": entry.get("file"),
                            "local_endpoint": local_ep,
                            "reference_endpoint": central_param_url,
                            "is_compliant": local_ep == central_param_url
                        })
                else:
                    final_results.append({"server": server, "config_file": "Aucun .config trouvé", "local_endpoint": None, "reference_endpoint": central_param_url, "is_compliant": False})
            except Exception as e:
                final_results.append({"server": server, "config_file": f"Erreur: {str(e)}", "local_endpoint": None, "reference_endpoint": central_param_url, "is_compliant": False})
        
        return final_results
