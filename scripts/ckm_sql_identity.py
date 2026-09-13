"""Repair and verify only CKM's own contained SQL identity; never invoke a model."""
import argparse
import base64
from datetime import datetime, timezone
import json
import os
import struct
import uuid

import pyodbc
from azure.identity import DefaultAzureCredential

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["repair", "verify"])
args = parser.parse_args()
result = {"scope": "CKM own SQL contained identity", "mode": args.mode, "model_requests": 0,
          "checked_at": datetime.now(timezone.utc).isoformat()}
connection = None
try:
    credential = DefaultAzureCredential()
    token = credential.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
    connection = pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};Server=sql-ptu-conversation-7d804f70.database.windows.net;"
        "Database=ptu-conversation;Encrypt=yes;TrustServerCertificate=no;",
        attrs_before={1256: struct.pack(f"<I{len(token)}s", len(token), token)}, timeout=30,
    )
    cursor = connection.cursor()
    if args.mode == "repair":
        # CREATE USER without Graph validation uses client ID for service principals, not object ID.
        sid = uuid.UUID("1b458b7e-1768-45a9-b676-9a3245a4dfbe").bytes_le.hex()
        cursor.execute(f"""
            IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name=N'id-ptu-conversation-runtime')
            CREATE USER [id-ptu-conversation-runtime] WITH SID=0x{sid}, TYPE=E, DEFAULT_SCHEMA=dbo
        """)
        for role in ["db_datareader", "db_datawriter", "db_ddladmin"]:
            cursor.execute(f"ALTER ROLE [{role}] ADD MEMBER [id-ptu-conversation-runtime]")
            cursor.execute(f"""
                IF EXISTS (
                    SELECT 1 FROM sys.database_role_members m
                    JOIN sys.database_principals r ON r.principal_id=m.role_principal_id
                    JOIN sys.database_principals u ON u.principal_id=m.member_principal_id
                    WHERE r.name=N'{role}' AND u.name=N'id-ptu-conversation')
                ALTER ROLE [{role}] DROP MEMBER [id-ptu-conversation]
            """)
        connection.commit()
        result["incorrect_sid_user_roles_removed"] = True
        result["users_or_data_deleted"] = False
    row = cursor.execute("""
        SELECT CURRENT_USER, IS_MEMBER('db_owner'), IS_MEMBER('db_datareader'),
               IS_MEMBER('db_datawriter'), IS_MEMBER('db_ddladmin')
    """).fetchone()
    result["current_user"] = row[0]
    result["db_owner"] = row[1]
    result["reader"] = row[2]
    result["writer"] = row[3]
    result["ddl_admin"] = row[4]
    row = cursor.execute("""
        SELECT COUNT(*), COUNT(DISTINCT JSON_VALUE(metadata,'$.category')),
               COUNT(DISTINCT source_type) FROM documents
    """).fetchone()
    result["ground_truth"] = {"records": row[0], "categories": row[1], "source_types": row[2]}
    if args.mode == "verify":
        assert result["current_user"] == "id-ptu-conversation-runtime"
        assert result["db_owner"] == 0
        assert all(result[key] == 1 for key in ["reader", "writer", "ddl_admin"])
        os.environ["AZURE_SQL_SERVER"] = "sql-ptu-conversation-7d804f70.database.windows.net"
        os.environ["AZURE_SQL_DATABASE"] = "ptu-conversation"
        from src.api.storage.sql_service import sql_service
        assert sql_service.available
        assert len(sql_service.load_all_documents()) == 3
        result["native_sql_initialized_and_reloaded"] = True
    result["status"] = "succeeded"
except Exception as exc:
    result["status"] = "failed"
    result["error_type"] = type(exc).__name__
    if isinstance(exc, pyodbc.Error):
        result["sqlstate"] = str(exc.args[0])
finally:
    if connection is not None:
        connection.close()
print("CKM_SQL_RESULT_BASE64=" + base64.b64encode(json.dumps(result).encode()).decode())
raise SystemExit(0 if result["status"] == "succeeded" else 2)
