import subprocess
import time
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
user_data_dir = "C:/Users/admin/OneDrive/Desktop/trade-yt/youtube/trade"
subprocess.Popen([chrome_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
time.sleep(100000)


import os
from util import upload_yt


upload_yt(
    f'C:/Users/admin/OneDrive/Desktop/trade-yt/youtube/trade',
    'f df sd sds',
    'dsfs sd sd',
    'hoang,huy,tgf,',
    f'C:/Users/admin/OneDrive/Desktop/trade-yt/runs/price-action/videos/aud-jpy-price-forecast-today-technical-analysis-september-12-aud-jpy-finds-resistance-around-ma.mp4',
    f'C:/Users/admin/OneDrive/Desktop/trade-yt/runs/price-action/videos/thumbnail.png',
)