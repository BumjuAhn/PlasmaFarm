import mysql.connector
from config import DB_CONFIG, LOG_FILE
import logging
import os

def connect_to_db():
    """Create a new database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def connect_mysql():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def check_mysql_connection():
    """MySQL 연결 상태를 확인하고 끊어진 경우 재연결"""
    global mysql_connection, cursor  # 전역 변수 재선언
    try:
        mysql_connection.ping(reconnect=True, attempts=3, delay=2)
    except mysql.connector.Error:
        print("MySQL connection lost. Reconnecting...")
        mysql_connection = connect_mysql()
        cursor = mysql_connection.cursor()

def initialize_db_heyhome():
    """Initialize the database schema."""
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS power_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cycle_id INT NOT NULL,
                timestamp DATETIME NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                fog BOOLEAN NOT NULL,
                plasma BOOLEAN NOT NULL,
                pump BOOLEAN NOT NULL,
                description TEXT NOT NULL
            )
        """)
        conn.commit()
        logging.info("Database initialized successfully.")
    finally:
        conn.close()

def save_to_db_heyhome(device_id, states, description, cycle_id):
    """Insert a new status record into the database."""
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO power_status (cycle_id, timestamp, device_id, fog, plasma, pump, description)
            VALUES (%s, NOW(), %s, %s, %s, %s, %s)
        """, (cycle_id, device_id, states.get("power1"), states.get("power2"), states.get("power3"), description))
        conn.commit()
        logging.info(f"State saved to database: {states}, Description: {description}, Cycle: {cycle_id}")
    finally:
        conn.close()

def save_to_mysql_tuya(result, timestamp):
    """MySQL에 데이터를 저장하는 함수"""
    check_mysql_connection()  # 연결 상태 확인 및 복구
    try:
        query = """
            INSERT INTO measurement_table (t, temp_current, ph_current, tds_current, ec_current, salinity_current, pro_current, orp_current, cf_current, rh_current)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (timestamp, *[result.get(key, 0) for key in ["temp_current", "ph_current", "tds_current", "ec_current", "salinity_current", "pro_current", "orp_current", "cf_current", "rh_current"]]))
        mysql_connection.commit()
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
