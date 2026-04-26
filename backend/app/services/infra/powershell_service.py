import subprocess
import json
import socket
from typing import List, Dict, Optional

class PowerShellService:
    """
    Service pour exécuter des commandes PowerShell localement ou à distance.
    """
    
    @staticmethod
    def run_command(command: str) -> Dict:
        """
        Exécute une commande PowerShell locale et retourne le résultat.
        """
        try:
            process = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    @staticmethod
    def run_remote_command(server: str, command: str, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """
        Exécute une commande sur un serveur distant via Invoke-Command.
        Détecte SSL et gère les identifiants si fournis.
        """
        use_ssl = PowerShellService.check_port(server, 5986)
        
        # Préparation des credentials si fournis
        cred_setup = ""
        cred_param = ""
        if username and password:
            # Échapper les guillemets simples dans le mot de passe
            safe_password = password.replace("'", "''")
            cred_setup = f"$pw = ConvertTo-SecureString '{safe_password}' -AsPlainText -Force; $cred = New-Object System.Management.Automation.PSCredential ('{username}', $pw); "
            cred_param = "-Credential $cred"

        options = ""
        if use_ssl:
            options = "-UseSSL -SessionOption (New-PSSessionOption -SkipCACheck -SkipCNCheck)"
        
        full_cmd = f"{cred_setup}Invoke-Command -ComputerName {server} {options} {cred_param} -ScriptBlock {{ {command} }}"
            
        return PowerShellService.run_command(full_cmd)

    @staticmethod
    def check_port(server: str, port: int, timeout: int = 3) -> bool:
        """
        Vérifie si un port TCP est ouvert sur un serveur.
        """
        try:
            with socket.create_connection((server, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    @staticmethod
    def run_script_json(server: str, script: str) -> Optional[Dict]:
        """
        Exécute un script distant et tente de parser la sortie comme du JSON.
        Ajoute automatiquement | ConvertTo-Json si nécessaire.
        """
        full_script = f"{script} | ConvertTo-Json -Compress"
        result = PowerShellService.run_remote_command(server, full_script)
        
        if result["success"] and result["stdout"]:
            try:
                # Nettoyage minimal si PowerShell ajoute des warnings
                json_str = result["stdout"].strip()
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        return None
