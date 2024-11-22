import os
import time
import mysql.connector
from dotenv import load_dotenv
from tuya_connector import TuyaOpenAPI
from database import connect_mysql, save_to_mysql_tuya

def main():
    global mysql_connection, cursor  # 전역 변수 선언

    # 환경 변수 로드
    load_dotenv()
    
    # Tuya API 설정
    API_ENDPOINT = os.getenv('API_ENDPOINT')
    ACCESS_ID = os.getenv('ACCESS_ID')
    ACCESS_SECRET = os.getenv('ACCESS_SECRET')
    DEVICE_ID = os.getenv('DEVICE_ID_ONLINE_8IN1_TESTER')
    
    # Tuya API 연결 설정
    openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_SECRET)
    openapi.connect()
    
    # 초기 MySQL 연결
    mysql_connection = connect_mysql()
    cursor = mysql_connection.cursor()
    
    def fetch_tuya_data():
        """Tuya API에서 데이터를 가져오는 함수"""
        try:
            data = openapi.get(f"/v2.0/cloud/thing/{DEVICE_ID}/shadow/properties")
            return {prop['code']: prop['value'] for prop in data['result']['properties'] if 'current' in prop['code']}
        except Exception as e:
            print(f"Error fetching data from Tuya API: {e}")
            return None

    # 주기적 데이터 수집 및 저장 루프
    last_time = time.time()
    
    try:
        while True:
            if time.time() - last_time >= 30:
                result = fetch_tuya_data()
                if result:
                    timestamp = result.pop('t', time.time() * 1000)
                    save_to_mysql_tuya(result, timestamp)
                last_time = time.time()
    
    except KeyboardInterrupt:
        print("프로그램이 중지되었습니다.")
    
    finally:
        # 자원 해제
        cursor.close()
        mysql_connection.close()
        print("Connections closed.")

if __name__ == "__main__":
    main()
