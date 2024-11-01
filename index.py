import os
import time
from dotenv import load_dotenv
from pprint import pprint
from tuya_connector import TuyaOpenAPI
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# .env 파일 로드
load_dotenv()

# Tuya API와 장치 ID 가져오기
API_ENDPOINT = os.getenv('API_ENDPOINT')
ACCESS_ID = os.getenv('ACCESS_ID')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')
DEVICE_ID_ONLINE_8IN1_TESTER = os.getenv('DEVICE_ID_ONLINE_8IN1_TESTER')

# TuyaOpenAPI 연결
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_SECRET)
openapi.connect()

# InfluxDB 설정 가져오기
influx_url = os.getenv("INFLUXDB_URL")
token = os.getenv("INFLUXDB_TOKEN")
org = os.getenv("INFLUXDB_ORG")
bucket = os.getenv("INFLUXDB_BUCKET")

# InfluxDB 클라이언트 생성
client = InfluxDBClient(url=influx_url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

try:
    while True:
        # Tuya에서 데이터 가져오기
        data = openapi.get("/v2.0/cloud/thing/{}/shadow/properties".format(DEVICE_ID_ONLINE_8IN1_TESTER))
        
        # "current"가 포함된 code 필터링 및 결과 추출
        result = {prop['code']: prop['value'] for prop in data['result']['properties'] if 'current' in prop['code']}
        result['t'] = data['t']  # 최상위 t 값을 추가

        # 결과 확인 (선택 사항)
        print(result)

        # InfluxDB에 데이터 저장
        point = Point("measurement_name") \
            .tag("primary_key", result['t']) \
            .field("temp_current", result.get('temp_current', 0)) \
            .field("ph_current", result.get('ph_current', 0)) \
            .field("tds_current", result.get('tds_current', 0)) \
            .field("ec_current", result.get('ec_current', 0)) \
            .field("salinity_current", result.get('salinity_current', 0)) \
            .field("pro_current", result.get('pro_current', 0)) \
            .field("orp_current", result.get('orp_current', 0)) \
            .field("cf_current", result.get('cf_current', 0)) \
            .field("rh_current", result.get('rh_current', 0)) \
            .time(result['t'], WritePrecision.MS)

        write_api.write(bucket=bucket, org=org, record=point)

        # 2초 대기
        time.sleep(2)

except KeyboardInterrupt:
    print("프로그램이 중지되었습니다.")

finally:
    # 연결 종료
    client.close()
