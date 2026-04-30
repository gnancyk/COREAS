from sqlalchemy import text, create_engine
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class SQLService:
    @staticmethod
    def _get_engine(db_name: str):
        # Utilisation de la chaîne de connexion du .env comme base
        base_url = os.getenv("DATABASE_URL")
        # Remplacement de la base par défaut par celle demandée
        # Format attendu : mssql+pyodbc://user:password@server/dbname?driver=...
        if "?" in base_url:
            parts = base_url.split("?")
            main_part = parts[0]
            params = parts[1]
            # Extraire l'URL sans la DB (si possible) ou remplacer la dernière partie avant le ?
            host_part = main_part.rsplit("/", 1)[0]
            new_url = f"{host_part}/{db_name}?{params}"
        else:
            host_part = base_url.rsplit("/", 1)[0]
            new_url = f"{host_part}/{db_name}"
            
        return create_engine(new_url)

    @staticmethod
    def verifier_indices_fragmentation(db_name: str) -> List[Dict]:
        engine = SQLService._get_engine(db_name)
        query = text("""
            SELECT 
                OBJECT_NAME(ips.object_id) AS TableName,
                i.name AS IndexName,
                ips.avg_fragmentation_in_percent AS Fragmentation
            FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'DETAILED') ips
            JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
            WHERE ips.avg_fragmentation_in_percent > 10
            ORDER BY ips.avg_fragmentation_in_percent DESC
        """)
        
        results = []
        with engine.connect() as conn:
            rows = conn.execute(query)
            for row in rows:
                frag = row.Fragmentation
                action = "REBUILD" if frag > 30 else "REORGANIZE"
                results.append({
                    "table_name": row.TableName,
                    "index_name": row.IndexName,
                    "fragmentation_percent": round(frag, 2),
                    "action_suggested": action
                })
        return results

    @staticmethod
    def verifier_indices_manquants(db_name: str) -> List[Dict]:
        engine = SQLService._get_engine(db_name)
        query = text("""
            SELECT 
                OBJECT_NAME(d.object_id) AS TableName,
                d.equality_columns,
                d.inequality_columns,
                d.included_columns,
                s.user_seeks * s.avg_total_user_cost * (s.avg_user_impact / 100.0) AS Impact
            FROM sys.dm_db_missing_index_details d
            JOIN sys.dm_db_missing_index_groups g ON d.index_handle = g.index_handle
            JOIN sys.dm_db_missing_index_group_stats s ON g.group_handle = s.group_handle
            WHERE d.database_id = DB_ID()
            ORDER BY Impact DESC
        """)
        
        results = []
        with engine.connect() as conn:
            rows = conn.execute(query)
            for row in rows:
                results.append({
                    "table_name": row.TableName,
                    "equality_columns": row.equality_columns,
                    "inequality_columns": row.inequality_columns,
                    "included_columns": row.included_columns,
                    "impact": round(row.Impact, 2)
                })
        return results

    @staticmethod
    def verifier_triggers_saphir(db_name: str) -> List[Dict]:
        engine = SQLService._get_engine(db_name)
        triggers_to_check = [
            'gs2e_Trg_UniciteCampagneFacturation',
            'trg_UpdateRequeteSQL'
        ]
        query = text("""
            SELECT 
                t.name AS TriggerName,
                OBJECT_NAME(t.parent_id) AS TableName,
                t.is_disabled
            FROM sys.triggers t
            WHERE t.name IN :triggers
        """)
        
        results = []
        with engine.connect() as conn:
            rows = conn.execute(query, {"triggers": tuple(triggers_to_check)})
            found_triggers = []
            for row in rows:
                found_triggers.append(row.TriggerName)
                results.append({
                    "trigger_name": row.TriggerName,
                    "table_name": row.TableName,
                    "is_enabled": not row.is_disabled,
                    "exists": True
                })
            
            for t in triggers_to_check:
                if t not in found_triggers:
                    results.append({
                        "trigger_name": t,
                        "table_name": "Inconnue",
                        "is_enabled": False,
                        "exists": False
                    })
        return results

    @staticmethod
    def verifier_coherence_orgid(db_name: str) -> Dict:
        engine = SQLService._get_engine(db_name)
        # On cherche l'OrganizationId dominant dans une table pivot (ex: AccountBase ou SystemUserBase)
        query = text("""
            SELECT TOP 5 OrganizationId, COUNT(*) as Count
            FROM AccountBase
            GROUP BY OrganizationId
            ORDER BY Count DESC
        """)
        
        results = []
        is_consistent = True
        try:
            with engine.connect() as conn:
                rows = conn.execute(query)
                for row in rows:
                    results.append({
                        "organization_id": str(row.OrganizationId),
                        "record_count": row.Count
                    })
            
            if len(results) > 1:
                is_consistent = False
        except Exception:
            is_consistent = False # Table non trouvée ou autre
            
        return {"is_consistent": is_consistent, "results": results}

    @staticmethod
    def verifier_catalogues_suspects(db_name: str) -> List[Dict]:
        engine = SQLService._get_engine(db_name)
        # Recherche de noms de bases probables (MSCRM, Saphir, etc.) entre crochets
        query = text("""
            SELECT 
                OBJECT_NAME(m.object_id) AS ObjectName,
                o.type_desc AS ObjectType,
                m.definition
            FROM sys.sql_modules m
            JOIN sys.objects o ON m.object_id = o.object_id
            WHERE m.definition LIKE '%[%]%' -- Contient des crochets (souvent pour les DB ou Schemas)
              AND (m.definition LIKE '%MSCRM%' OR m.definition LIKE '%SAPHIR%')
        """)
        
        results = []
        with engine.connect() as conn:
            rows = conn.execute(query)
            for row in rows:
                # Extraire un snippet du code suspect
                results.append({
                    "object_name": row.ObjectName,
                    "object_type": row.ObjectType,
                    "suspect_content": row.definition[:200] + "..."
                })
        return results

    @staticmethod
    def verifier_param_critere(db_name: str = "gs2e_parametregenerauxbase") -> Dict:
        """
        Recherche le paramètre PARAMCRIT0001 dans la base spécifiée.
        """
        engine = SQLService._get_engine(db_name)
        # Requête adaptée à la structure supposée
        query = text("""
            SELECT ParamName, ParamValue 
            FROM [gs2e_parametregenerauxbase].[dbo].[Parameters] 
            WHERE ParamName = 'PARAMCRIT0001'
        """)
        
        try:
            with engine.connect() as conn:
                result = conn.execute(query).first()
                if result:
                    return {
                        "exists": True,
                        "param_name": result.ParamName,
                        "param_value": result.ParamValue,
                        "status": "OK"
                    }
                return {"exists": False, "status": "KO", "message": "Paramètre non trouvé"}
        except Exception as e:
            return {"exists": False, "status": "KO", "message": str(e)}
