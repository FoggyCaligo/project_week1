import subprocess
import os

cwd = r'C:\Users\human-25\project_week1'

def run(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        print(f"[{cmd}]")
        print(res.stdout)
        if res.stderr:
            print(f"ERR: {res.stderr}")
    except Exception as e:
        print(f"Exception: {e}")

run('git status -sb')
run('git add .')
run('git -c user.name="장민재" -c user.email="jang@example.com" commit -m "[local_jang>dev] 수정,추가 : app.py 코드를 routes, models, services로 분리하여 블루프린트 마이그레이션 (팀 컨벤션 반영) 및 /fridge 로그아웃 500 버그 수정"')
run('git log -3 --oneline')
