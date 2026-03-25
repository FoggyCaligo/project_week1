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
run('git -c user.name="장민재" -c user.email="jang@example.com" commit -m "[local_jang>dev] 추가 : 공공데이터 API(COOKRCP01) 활용 재료 매칭 추천 알고리즘 및 템플릿 연동 구현 (팀원3 파트 연계)"')
run('git log -3 --oneline')
