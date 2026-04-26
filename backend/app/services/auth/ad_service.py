from ldap3 import Server, Connection, ALL, NTLM
from app.core.config import settings

class ADService:
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict:
        """
        Interroge l'AD pour authentifier l'utilisateur et récupérer ses infos.
        """
        server = Server(settings.AD_SERVER_URL, get_info=ALL)
        user_dn = f"{settings.AD_DOMAIN}\\{username}"
        
        try:
            conn = Connection(
                server, 
                user=user_dn, 
                password=password, 
                authentication='SIMPLE',
                auto_bind=True
            )
            
            if conn.bound:
                # Recherche des informations complémentaires
                conn.search(
                    search_base=settings.AD_BASE_DN,
                    search_filter=f"(sAMAccountName={username})",
                    attributes=["displayName", "mail"]
                )
                
                user_info = {
                    "username": username,
                    "full_name": username,
                    "email": None,
                   
                }
                
                if conn.entries:
                    entry = conn.entries[0]
                    user_info["full_name"] = str(entry.displayName.value) if entry.displayName else username
                    user_info["email"] = str(entry.mail.value) if entry.mail else None
                    

                conn.unbind()
                return user_info
            
            return None
            
        except Exception as e:
            print(f"[DEBUG] Erreur d'authentification AD pour {user_dn}: {str(e)}")
            return None
