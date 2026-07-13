import sys, subprocess, os
os.chdir('D:\\basma-\\backend')
log = open('D:\\basma-\\backend\\uvicorn.log', 'w', buffering=1)
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8000'],
    cwd='D:\\basma-\\backend',
    stdout=log, stderr=subprocess.STDOUT, text=True
)
print(proc.pid, end='')
