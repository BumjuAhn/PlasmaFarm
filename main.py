from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from multiprocessing import Process, active_children
import signal
import os
import heyhome
import tuya

app = FastAPI()

# HTML 템플릿 및 Static 파일 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 전역 변수로 프로세스 관리
processes = {
    "heyhome": None,
    "tuya": None,
}

def run_heyhome_main():
    """heyhome.py의 main 함수 실행"""
    heyhome.main()

def run_tuya_main():
    """tuya.py의 main 함수 실행"""
    tuya.main()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """메인 웹 페이지"""
    heyhome_status = "Running" if processes["heyhome"] and processes["heyhome"].is_alive() else "Stopped"
    tuya_status = "Running" if processes["tuya"] and processes["tuya"].is_alive() else "Stopped"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "heyhome_status": heyhome_status,
        "tuya_status": tuya_status,
    })

@app.post("/start/{service}")
def start_service(service: str):
    """서비스 시작"""
    global processes
    if service not in processes:
        return {"message": f"Unknown service: {service}"}

    if processes[service] and processes[service].is_alive():
        return {"message": f"{service} is already running."}

    if service == "heyhome":
        process = Process(target=run_heyhome_main)
    elif service == "tuya":
        process = Process(target=run_tuya_main)
    else:
        return {"message": f"Invalid service: {service}"}

    process.start()
    processes[service] = process
    return {"message": f"{service} started."}

@app.post("/stop/{service}")
def stop_service(service: str):
    """서비스 중지"""
    global processes
    if service not in processes:
        return {"message": f"Unknown service: {service}"}

    if not processes[service] or not processes[service].is_alive():
        return {"message": f"{service} is not running."}

    try:
        processes[service].terminate()
        processes[service].join()
    finally:
        processes[service] = None
    return {"message": f"{service} stopped."}

@app.on_event("shutdown")
def shutdown_event():
    """FastAPI 종료 시 모든 자식 프로세스 정리"""
    for process in active_children():
        try:
            os.kill(process.pid, signal.SIGTERM)
            process.join()
        except Exception as e:
            print(f"Error terminating process {process.pid}: {e}")
