import sys
import os

# Add app directory to path
sys.path.append(os.path.abspath("backend"))

from ldap3 import Server, Connection, ALL, NTLM
from app.core.config import settings

def test_auth(username, password):
    print(f"Testing for server: {settings.AD_SERVER_URL}")
    print(f"Domain: {settings.AD_DOMAIN}")
    
    server = Server(settings.AD_SERVER_URL, get_info=ALL)
    
    # Try multiple formats
    formats = [
        f"{settings.AD_DOMAIN}\\{username}",
        f"{username}@{settings.AD_DOMAIN}",
        f"{username}@{settings.AD_DOMAIN}.local" # Common variant
    ]
    
    for user_dn in formats:
        print(f"\nTrying format: {user_dn}")
        try:
            conn = Connection(server, user=user_dn, password=password, authentication=NTLM)
            if conn.bind():
                print(f"SUCCESS with {user_dn}!")
                conn.unbind()
                return True
            else:
                print(f"FAILED with {user_dn}: {conn.result}")
        except Exception as e:
            print(f"ERROR with {user_dn}: {e}")
            
    return False

if __name__ == "__main__":
    # In a real scenario I would get these from args, but for a quick test...
    # I'll ask the user to run this script themselves or I'll try with dummy if needed.
    # Actually, I'll just provide the script and ask the user to run it.
    pass
