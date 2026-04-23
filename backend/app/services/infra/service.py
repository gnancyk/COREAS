import subprocess
from typing import List, Dict, Optional
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
        Vérification de la disponibilité (Ping). Pas besoin de credentials.
        """
        results = []
        for server in servers:
            try:
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
        Vérification du port 5986. Pas besoin de credentials.
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
    def obtenir_caracteristiques_os(servers: List[str], username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Récupération des informations OS et Matérielles Expertes (RAM, CPU, Disque, Process, DNS, SSL, IIS).
        """
        results = []
        # Script PowerShell Expert Final
        script = (
            "Import-Module WebAdministration -ErrorAction SilentlyContinue; "
            "$os = Get-CimInstance Win32_OperatingSystem; "
            "$cs = Get-CimInstance Win32_ComputerSystem; "
            "$proc_avg = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average; "
            "$disk = Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=''C:'''; "
            "$cpu_cores = Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum; "
            "$top_p = Get-Process | Sort-Object CPU -Descending | Select-Object -First 3 | Select-Object Name, CPU, @{Name='WorkingSet';Expression={$_.WorkingSet}}; "
            "$dns_test = Resolve-DnsName google.com -ErrorAction SilentlyContinue; "
            "$last_h = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1; "
            "$certs = Get-ChildItem Cert:\\LocalMachine\\My | Select-Object Subject, NotAfter | Where-Object { $_.NotAfter -gt (Get-Date) }; "
            "$pools = if(Get-Module WebAdministration) { Get-ChildItem IIS:\\AppPools | Select-Object Name, State } else { @() }; "
            "[PSCustomObject]@{ "
            "os_name = $os.Caption; "
            "os_version = $os.Version; "
            "last_reboot = $os.LastBootUpTime.ToString('yyyy-MM-dd HH:mm:ss'); "
            "cpu_count = [int]$cpu_cores.Sum; "
            "cpu_usage_percent = [math]::Round($proc_avg.Average, 2); "
            "ram_total_gb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2); "
            "ram_free_gb = [math]::Round($os.FreePhysicalMemory / 1MB, 2); "
            "ram_used_gb = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 2); "
            "disk_total_gb = [math]::Round($disk.Size / 1GB, 2); "
            "disk_free_gb = [math]::Round($disk.FreeSpace / 1GB, 2); "
            "disk_used_gb = [math]::Round(($disk.Size - $disk.FreeSpace) / 1GB, 2); "
            "model = $cs.Model; "
            "manufacturer = $cs.Manufacturer; "
            "top_processes = $top_p | ForEach-Object { @{ name=$_.Name; cpu_usage=[math]::Round($_.CPU, 2); ram_usage_mb=[math]::Round($_.WorkingSet / 1MB, 2) } }; "
            "dns_status = @{ 'google.com' = [bool]$dns_test }; "
            "last_update_date = if($last_h) { $last_h.InstalledOn.ToString('yyyy-MM-dd') } else { 'Inconnue' }; "
            "ssl_certificates = $certs | ForEach-Object { @{ subject=$_.Subject; expiry_date=$_.NotAfter.ToString('yyyy-MM-dd'); days_remaining=($_.NotAfter - (Get-Date)).Days; is_valid=$true } }; "
            "app_pools = $pools | ForEach-Object { @{ name=$_.Name; state=$_.State } } "
            "} | ConvertTo-Json -Compress"
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
    def verifier_fonctionnalites(servers: List[str], features: List[str], username: Optional[str] = None, password: Optional[str] = None) -> List[Dict]:
        """
        Vérifie les fonctionnalités avec support credentials.
        """
        results = []
        feature_list_str = "'" + "','".join(features) + "'"
        script = f"Get-WindowsFeature -Name {feature_list_str} | Select-Object Name, Installed | ConvertTo-Json -Compress"
        
        for server in servers:
            is_local = server.lower() in ["localhost", "127.0.0.1", socket.gethostname().lower()]
            
            if is_local:
                result = PowerShellService.run_command(script)
            else:
                result = PowerShellService.run_remote_command(server, script, username, password)

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
