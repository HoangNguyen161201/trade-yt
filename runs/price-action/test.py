from db import get_end_screen_video_ad, update_end_screen_video_ad

data = get_end_screen_video_ad('trade')
print(data)
update_end_screen_video_ad(data['_id'], 'XAU/USD Price Forecast Today, Technical Analysis (November 06): XAU/USD Pulls Back Again', 'XAUUSD Price Forecast')

# from selenium.webdriver.common.keys import Keys
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

# import time
# import os
# base_dir = os.path.dirname(os.path.abspath(__file__))
# user_data_dir = os.path.join(base_dir, './youtubes/test')
# chrome_options = Options()

# # Chỉ định đường dẫn đến thư mục user data
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# chrome_options.add_argument(f"user-data-dir={user_data_dir}")
# # Nếu bạn muốn sử dụng profile mặc định
# chrome_options.add_argument("profile-directory=Default")
# # chrome_options.add_argument("--headless")  # Chạy trong chế độ không giao diện
# # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường dùng trong môi trường máy chủ)

# # Sử dụng Service để chỉ định ChromeDriver
# service = Service(ChromeDriverManager().install())

# # Khởi tạo WebDriver với các tùy chọn
# browser = webdriver.Chrome(service=service, options=chrome_options)

# browser.get("https://studio.youtube.com/")

# input_data = input("Nhập chọn chức năng: ")

# WebDriverWait(browser, 100).until(
#     EC.element_to_be_clickable((By.ID, 'endscreens-button'))
# )
# browser.find_element(By.ID, 'endscreens-button').click()

# # 1️⃣ Đợi cho phần tử card xuất hiện
# time.sleep(3)
# cards = WebDriverWait(browser, 100).until(
#     EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card.style-scope.ytve-endscreen-template-picker"))
# )
# browser.execute_script("arguments[0].click();", cards[0])

# time.sleep(3)
# WebDriverWait(browser, 100).until(
#     EC.element_to_be_clickable((By.ID, 'save-button'))
# )
# browser.find_element(By.ID, 'save-button').click()

# # ------------------------------------------------------------------
# time.sleep(3)
# WebDriverWait(browser, 100).until(
#     EC.element_to_be_clickable((By.ID, 'cards-button'))
# )
# browser.find_element(By.ID, 'cards-button').click()

# time.sleep(3)
# WebDriverWait(browser, 100).until(
#     EC.element_to_be_clickable((By.CLASS_NAME, 'info-card-type-option-container'))
# )
# browser.find_elements(By.CLASS_NAME, 'info-card-type-option-container')[0].click()

# time.sleep(3)
# WebDriverWait(browser, 100).until(
#     EC.element_to_be_clickable((By.ID, 'search-any'))
# )
# browser.find_element(By.ID, 'search-any').click()

# time.sleep(3)
# input = browser.find_element(By.ID, 'search-any')
# input.clear()
# input.send_keys('XAU/USD Price Forecast Today, Technical Analysis (November 05): XAU/USD Has a Strong Open')

# time.sleep(3)
# WebDriverWait(browser, 100).until(
#     EC.element_to_be_clickable((By.TAG_NAME, 'ytcp-entity-card'))
# )
# browser.find_elements(By.TAG_NAME, 'ytcp-entity-card')[0].click()

# time.sleep(3)
# textareas = WebDriverWait(browser, 30).until(
#     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "textarea.ytve-lightweight-textarea"))
# )
# textareas[0].clear()
# textareas[0].send_keys("ô thứ nhất")
# time.sleep(3)
# textareas[1].clear()
# textareas[1].send_keys("ô thứ hai")

# time.sleep(3)
# WebDriverWait(browser, 100).until(
#     EC.element_to_be_clickable((By.ID, 'save-button'))
# )
# browser.find_element(By.ID, 'save-button').click()

# time.sleep(1000000)

# # id:endscreens-button class:template-preview id:save-button
# # id:cards-button class:info-card-type-option-container[0] tagname:tp-yt-paper-tab[3] còn tiếp