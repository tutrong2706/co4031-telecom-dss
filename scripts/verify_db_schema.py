"""
CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM
Script: Verify PostgreSQL Schema & Objects
Author: Data Engineer Agent (CO4031 - HCMUT)
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def verify_schema():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'telecom_dw'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )
    cur = conn.cursor()
    
    print("=" * 70)
    print("KIEM TRA CAC DOI TUONG TRONG POSTGRESQL (DATABASE: telecom_dw)")
    print("=" * 70)
    
    query = """
    SELECT table_schema, table_name, table_type 
    FROM information_schema.tables 
    WHERE table_schema IN ('staging', 'edw')
    ORDER BY table_schema, table_name;
    """
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        print(f"Schema: {row[0]:<10} | Name: {row[1]:<38} | Type: {row[2]}")
        
    print("\n--- KIEM TRA FOREIGN KEYS TRONG EDW STAR SCHEMA ---")
    fk_query = """
    SELECT
        tc.table_name, 
        kcu.column_name, 
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'edw';
    """
    cur.execute(fk_query)
    fks = cur.fetchall()
    for fk in fks:
        print(f"FK: {fk[0]}.{fk[1]}  -->  {fk[2]}.{fk[3]}")
        
    conn.close()

if __name__ == "__main__":
    verify_schema()
