"""
CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM
Script: Test PostgreSQL Connection with Password Testing
Author: Data Engineer Agent (CO4031 - HCMUT)

Cách sử dụng:
1. Chạy bình thường (đọc từ .env):
   python scripts/test_postgres_connection.py

2. Thử nhanh nhiều mật khẩu cùng lúc:
   python scripts/test_postgres_connection.py mk1 mk2 123456 root admin
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# UTF-8 stdout fix for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def test_single_password(host, port, user, password):
    display_pwd = "***" if password else "<empty>"
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=2
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        ver = cur.fetchone()[0]
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = [row[0] for row in cur.fetchall()]
        conn.close()
        return True, ver, dbs
    except Exception as e:
        return False, str(e).strip(), []

def main():
    print("=" * 70)
    print("🔑 TEST KẾT NỐI POSTGRESQL & KIỂM TRA MẬT KHẨU")
    print("=" * 70)

    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    user = os.getenv("DB_USER", "postgres")
    env_password = os.getenv("DB_PASSWORD", "")

    # Candidates to test
    candidates = []
    
    # If passwords passed via command line arguments
    if len(sys.argv) > 1:
        candidates = sys.argv[1:]
        print(f"--> Đang thử {len(candidates)} mật khẩu từ tham số dòng lệnh...")
    else:
        if env_password:
            candidates.append(env_password)
            print(f"--> Đang kiểm tra mật khẩu từ file .env...")
        else:
            print(f"--> File .env đang để trống mật khẩu.")
            print(f"    Bạn có thể:")
            print(f"    1. Mở file .env và điền DB_PASSWORD=mật_khẩu_của_bạn rồi chạy lại.")
            print(f"    2. Hoặc chạy: python scripts/test_postgres_connection.py <mat_khau_1> <mat_khau_2>")
            return

    matched_pwd = None
    for idx, pwd in enumerate(candidates, 1):
        print(f"\n[Thử {idx}/{len(candidates)}] Thử với mật khẩu: '{pwd}' ...")
        success, info, dbs = test_single_password(host, port, user, pwd)
        if success:
            print(f"  ===> [THÀNH CÔNG!] Kết nối PostgreSQL thành công rực rỡ!")
            print(f"       + Phiên bản: {info}")
            print(f"       + Các Database hiện có: {', '.join(dbs)}")
            matched_pwd = pwd
            
            # Update .env automatically if requested
            if env_password != pwd:
                with open(".env", "w", encoding="utf-8") as f:
                    f.write(f"# PostgreSQL Database Configuration for CO4031 Data Warehouse\n")
                    f.write(f"DB_HOST={host}\n")
                    f.write(f"DB_PORT={port}\n")
                    f.write(f"DB_NAME=telecom_dw\n")
                    f.write(f"DB_USER={user}\n")
                    f.write(f"DB_PASSWORD={pwd}\n")
                print(f"  ===> [ĐÃ LƯU] Đã tự động cập nhật mật khẩu chính xác vào file .env!")
            break
        else:
            if "password authentication failed" in info:
                print(f"  ---> [Sai mật khẩu] (Password authentication failed)")
            else:
                print(f"  ---> [Lỗi khác]: {info}")

    if not matched_pwd:
        print("\n[!] Chưa tìm thấy mật khẩu chính xác trong danh sách thử.")
        print("    Hãy thử lại với các mật khẩu khác mà bạn hay dùng nhé!")

if __name__ == "__main__":
    main()
