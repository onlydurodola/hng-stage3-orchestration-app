import requests
import os

def check_db_connection(db_host):
    try:
        response = requests.get(f"http://{db_host}:5432/health")
        return response.status_code == 200
    except Exception:
        return False

def run_tests():
    db1_ok = check_db_connection(os.getenv("DB1_HOST"))
    db2_ok = check_db_connection(os.getenv("DB2_HOST"))
    return db1_ok and db2_ok