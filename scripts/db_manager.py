"""
CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM
Module: Database Manager & DDL Executor (PostgreSQL + SQLite)
Author: Data Engineer Agent (CO4031 - HCMUT)
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# UTF-8 stdout fix for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def get_postgres_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "dbname": os.getenv("DB_NAME", "telecom_dw")
    }

def test_postgres_connection(password=None):
    config = get_postgres_config()
    if password is not None:
        config["password"] = password

    print(f"--> Đang thử kết nối PostgreSQL tại {config['host']}:{config['port']} (user={config['user']})...")
    try:
        # First connect to default 'postgres' db
        conn = psycopg2.connect(
            dbname="postgres",
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
            connect_timeout=3
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        v = cur.fetchone()[0]
        print(f"[OK] KẾT NỐI POSTGRESQL THÀNH CÔNG!")
        print(f"     Version: {v}")
        conn.close()
        return True, config
    except Exception as e:
        print(f"[FAIL] Không thể kết nối PostgreSQL: {e}")
        return False, str(e)

def init_postgres_dw(password=None):
    success, result = test_postgres_connection(password)
    if not success:
        return False

    config = result
    # Connect to create database if not exists
    conn = psycopg2.connect(
        dbname="postgres",
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"]
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if telecom_dw exists
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config['dbname']}';")
    if not cur.fetchone():
        print(f"--> Đang tạo database '{config['dbname']}'...")
        cur.execute(f"CREATE DATABASE {config['dbname']};")
        print(f"[OK] Đã tạo database '{config['dbname']}' thành công!")
    else:
        print(f"[OK] Database '{config['dbname']}' đã tồn tại sẵn.")
    conn.close()

    # Connect to telecom_dw and execute DDL scripts
    dw_conn = psycopg2.connect(
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"]
    )
    dw_cur = dw_conn.cursor()

    ddl_files = [
        "sql/ddl/01_staging_schema.sql",
        "sql/ddl/02_dw_star_schema.sql",
        "sql/ddl/03_indexes_and_views.sql"
    ]

    for ddl in ddl_files:
        print(f"--> Đang thực thi DDL script: {ddl}...")
        with open(ddl, "r", encoding="utf-8") as f:
            sql_content = f.read()
            dw_cur.execute(sql_content)
        dw_conn.commit()
        print(f"[OK] Thực thi thành công {ddl}")

    dw_conn.close()
    print("\n🎉 TOÀN BỘ STAGING & STAR SCHEMA TRÊN POSTGRESQL ĐÃ ĐƯỢC KHỞI TẠO HOÀN TẤT!")
    return True

if __name__ == "__main__":
    test_postgres_connection()
