import pyodbc
import sys

def test_conn(label, conn_str):
    print(f"--- Attempt {label} ---")
    print(f"Conn Str: {conn_str}")
    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        print("RESULT: SUCCESS")
        conn.close()
        return True
    except Exception as e:
        print(f"RESULT: FAILED - {e}")
        return False

# 1. Double backslash
test_conn("1", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=GSESPHV3S2RD\\CIEPP;DATABASE=COREAS;UID=sa;PWD=Operating0")

# 2. Single backslash
test_conn("2", r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=GSESPHV3S2RD\CIEPP;DATABASE=COREAS;UID=sa;PWD=Operating0")

# 3. No instance
test_conn("3", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=GSESPHV3S2RD;DATABASE=COREAS;UID=sa;PWD=Operating0")
