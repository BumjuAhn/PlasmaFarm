# PlasmaFarm_heyhome 

### 실행하기
- 헤이홈 실행
```
python3 heyhome.py
```
- 투야 실행
```
python3 tuya.py
```

- 백그라운드 실행
```
nohup python3 -u heyhome.py &
nohup python3 -u tuya.py &
```
- FASTAPI 실행
```
unicorn main:app --reload
```
- Web 주소
```
http://ip주소:8000
```

- 로그 보기
```
cat log_file.log
tail -f log_file.log
```
- 실행 확인
```
ps ax | grep .py
```
- 종료하기
```
kill -9 PID
ex. kill -9 13586
```
