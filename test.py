import subprocess
import time

## dùng để tạo ra 1 user
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
user_data_dir = "C:/Path/To/Chrome/trade-yt"
subprocess.Popen([chrome_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
time.sleep(10000)
