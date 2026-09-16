from mega import Mega
import pyperclip
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import urllib.parse
from pymongo import MongoClient

def get_first_video_info():
    username = urllib.parse.quote_plus("hoangdev161201_db_user")
    password = urllib.parse.quote_plus("dAmGyKqEEo18HrK1")
    uri = f"mongodb+srv://{username}:{password}@cluster0.tmmhbkx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    client = None
    try:
        # 1. Khởi tạo kết nối
        client = MongoClient(uri)
        db = client["trade-yt"]
        collection = db["info"]

        # 2. Lấy ra bản ghi đầu tiên trong collection
        data = collection.find_one()

        if data:
            # Xóa trường '_id' của MongoDB nếu bạn chỉ muốn lấy dữ liệu thuần
            data.pop("_id", None)
            print("-> Đã lấy thành công dữ liệu từ MongoDB!")
            return data
        else:
            print("-> Collection 'info' đang rỗng, không có dữ liệu.")
            return None

    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu từ MongoDB: {e}")
        return None

    finally:
        if client:
            client.close()

def check_exist_video_hd(browser):
    timeout = 20 * 60
    start_time = time.time()
    is_not_find_status = False
    while True:
        # element = browser.find_elements(By.XPATH, '//*[@check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_COMPLETED" or @checks-summary-status-v2="UPLOAD_CHECKS_DATA_SUMMARY_STATUS_STARTED" or @check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_STARTED"]')
        element = browser.find_elements(By.XPATH, '//*[@check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_COMPLETED" or @checks-summary-status-v2="UPLOAD_CHECKS_DATA_SUMMARY_STATUS_COMPLETED" or @checks-summary-status-v2="UPLOAD_CHECKS_DATA_SUMMARY_STATUS_STARTED"]')
        if element:
            break  # Thoát vòng lặp nếu tìm thấy
        
        elapsed = time.time() - start_time
        if elapsed > timeout:
            is_not_find_status = True
            break
        print("Chưa tìm thấy, tiếp tục kiểm tra...")
        time.sleep(2)  # Đợi 2 giây trước khi kiểm tra lại

    if is_not_find_status is True:
        browser.quit()
        raise Exception("lỗi upload youtube")



def get_file_from_mega(folder_mega, folder_output_path):
    mega = Mega()
    m = mega.login("hoangdev161201@gmail.com", "Cuem1612@")

    files = m.get_files()

    node_id_found = None
    for node_id, node in files.items():
        # t == 1 là thư mục
        if node["t"] == 1 and node["a"]["n"] == folder_mega:
            node_id_found = node_id
            continue
        if node_id_found and node['p'] == node_id_found:
            try:
                m.download((node_id, node), folder_output_path)
                time.sleep(3)
            except:
                time.sleep(3)
                
    if not node_id_found:
        m.create_folder(folder_mega)
    else:
        m.delete(node_id_found)
        m.empty_trash()
        m.create_folder(folder_mega)


        
def upload_files_to_mega(folder_mega, files_path):
    mega = Mega()
    m = mega.login("hoangdev161201@gmail.com", "Cuem1612@")
    files = m.get_files()

    node_id_found = None
    for node_id, node in files.items():
        # t == 1 là thư mục
        if node["t"] == 1 and node["a"]["n"] == folder_mega:
            node_id_found = node_id
            break
                
    if not node_id_found:
        m.create_folder(folder_mega)
    else:
        m.delete(node_id_found)
        m.empty_trash()
        m.create_folder(folder_mega)
    
    node_id_found = None
    while True:
        files = m.get_files()
        for node_id, node in files.items():
            if node["t"] == 1 and node["a"]["n"] == folder_mega:
                node_id_found = node_id
                break
        if node_id_found:
            break
        
    
    for file in files_path:
        m.upload(file, node_id_found)
        
def count_files_in_mega_folder(folder_mega):
    mega = Mega()
    m = mega.login("hoangdev161201@gmail.com", "Cuem1612@")

    files = m.get_files()

    folder_id = None

    # Tìm folder
    for node_id, node in files.items():
        if node["t"] == 1 and node["a"]["n"] == folder_mega:
            folder_id = node_id
            break

    if not folder_id:
        print(f"Không tìm thấy folder: {folder_mega}")
        return 0

    # Đếm file trực tiếp trong folder
    count = 0

    for node_id, node in files.items():
        if node.get("p") == folder_id and node["t"] == 0:
            count += 1

    return count

    
def upload_yt(user_data_dir, title, description, tags, video_path, video_thumbnail, comment=None, is_not_wait_check=False):
    # dùng để tạo ra 1 user
    # chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    # user_data_dir = "C:/Path/To/Chrome/news-us"
    # subprocess.Popen([chrome_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
    # time.sleep(5)

    # Tạo đối tượng ChromeOptions
    chrome_options = Options()

    # Chỉ định đường dẫn đến thư mục user data
    # chrome_options.add_argument(
    #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    # Nếu bạn muốn sử dụng profile mặc định
    chrome_options.add_argument("profile-directory=Default")
    # chrome_options.add_argument("--headless")  # Chạy trong chế độ không giao diện
    # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường dùng trong môi trường máy chủ)

    # Sử dụng Service để chỉ định ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Khởi tạo WebDriver với các tùy chọn
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get("https://studio.youtube.com/")
    
    
    # await browser load end
    element = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//ytcp-button[@icon="yt-sys-icons:video_call"]'))
    )
    element.click()
    time.sleep(1)

    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'text-item-0'))
    )

    browser.find_element(By.ID, 'text-item-0').click()
    time.sleep(10)

    # upload video
    print('upload video in youtube')
    WebDriverWait(browser, 100).until(
        lambda d: len(d.find_elements(By.TAG_NAME, 'input')
                      ) > 1  # Đảm bảo có ít nhất 2 input
    )

    file_input = browser.find_elements(By.TAG_NAME, 'input')[1]
    file_input.send_keys(video_path)
    time.sleep(3)

    # upload thumbnail
    print('upload thumbnail in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'file-loader'))
    )
    thumbnail_input = browser.find_element(By.ID, 'file-loader')
    thumbnail_input.send_keys(video_thumbnail)
    time.sleep(3)

    # enter title
    print('nhập title in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'textbox'))
    )

    title_input = browser.find_element(By.ID, 'textbox')

    check_clean_title = False
    while check_clean_title is False:
        # Xoá bằng Ctrl+A + Delete
        title_input.send_keys(Keys.CONTROL, "a")
        title_input.send_keys(Keys.DELETE)
        title_input.clear()
        time.sleep(1)
        if title_input.text.strip() == "":
            check_clean_title = True

    time.sleep(1)
    title_input.send_keys(title)
    time.sleep(1)

    # enter description
    print('nhập description in youtube')
    des_input = browser.find_elements(By.ID, 'textbox')[1]
    des_input.clear()
    time.sleep(1)
    # Copy vào clipboard
    pyperclip.copy(description)
    des_input.click()
    time.sleep(1)
    des_input.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    # enter hiển thị thêm
    # Đợi cho phần tử scrollable-content xuất hiện
    scrollable_element = WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.ID, "scrollable-content"))
    )
    # Scroll xuống cuối cùng của phần tử scrollable-content
    browser.execute_script(
        "arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_element)
    time.sleep(2)

    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'toggle-button'))
    )
    show_more_btn = browser.find_element(By.ID, 'toggle-button')
    show_more_btn.click()
    time.sleep(2)

    # enter tags
    print('nhập tags in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'text-input'))
    )
    tags_input = browser.find_element(By.ID, 'text-input')
    tags_input.send_keys(tags)
    time.sleep(2)

    # next btn
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(10)
    check_exist_video_hd(browser)
    
    # bật kiếm tiền -------------------------------------------
    earn_selection = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            'ytcp-video-monetization ytcp-icon-button.edit-button'
        ))
    )
    earn_selection.click()
    time.sleep(1)
    # 2. Chọn "Bật"
    radio_on = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "tp-yt-paper-radio-button#radio-on"
        ))
    )
    radio_on.click()
    time.sleep(1)
    # 3. Chờ nút "Xong" được enable
    save_button = WebDriverWait(browser, 100).until(
         EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        "ytcp-button#save-button:not([disabled])"
    ))
    )
    save_button.click()
    time.sleep(2)
    # next btn
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(10)
    scrollable_element = WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.ID, "scrollable-content"))
    )
    browser.execute_script(
        "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
        scrollable_element
    )
    time.sleep(2)
    checkbox = WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ytcp-checkbox-lit.all-none-checkbox div#checkbox"))
    )
    browser.execute_script("arguments[0].click();", checkbox)
    time.sleep(2)
    browser.execute_script(
        "arguments[0].scrollTo(0, 0);",
        scrollable_element
    )
    time.sleep(2)
    # 1. Đợi cho nút "Gửi thông tin đánh giá" xuất hiện
    submit_button = WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.ID, "submit-questionnaire-button"))
    )

    # 2. Click bằng JavaScript để tránh bị che khuất bởi các lớp phủ (overlay)
    browser.execute_script("arguments[0].click();", submit_button)
    time.sleep(5)
    progress = WebDriverWait(browser, 100).until(
        lambda d: d.find_element(
            By.CLASS_NAME,
            "dialog-content"
        ).find_element(
            By.TAG_NAME,
            "tp-yt-paper-progress"
        )
    )
    WebDriverWait(browser, 100).until(
        lambda d: progress.get_attribute("hidden") is not None
    )
    
    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'next-button'))
    )
    browser.find_element(By.ID, 'next-button').click()
    
    
    # # add end screens
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

    # next
    time.sleep(3)
    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'next-button'))
    )
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(2)
    
    check_exist_video_hd(browser)

    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'next-button'))
    )
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(3)
    
    
    # click public
    scrollable_element = WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.ID, "scrollable-content"))
    )
    browser.execute_script(
        "arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_element)
    time.sleep(2)
    public_radio = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'tp-yt-paper-radio-button[name="PUBLIC"]')
        )
    )
    public_radio.click()
    time.sleep(3)

    # done
    print('upload video in youtube thành công')
    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'done-button'))
    )
    browser.find_element(By.ID, 'done-button').click()

    # vào youtube để nhập bình luận
    # if comment is not None:
    #     WebDriverWait(browser, 100).until(
    #         EC.presence_of_all_elements_located((By.ID, 'share-url'))
    #     )
    #     link_redirect = browser.find_element(By.ID, 'share-url')
    #     href = link_redirect.get_attribute('href')
    #     browser.get(href)
    #     WebDriverWait(browser, 100).until(
    #         EC.presence_of_all_elements_located((By.ID, 'above-the-fold'))
    #     )
    #     time.sleep(5)
    #     is_Find_comment = False
    #     while is_Find_comment is False:
    #         try:
    #             browser.execute_script("window.scrollBy(0, 50);")
    #             time.sleep(1)
    #             comment_box = browser.find_element(
    #                 By.ID, 'simplebox-placeholder')
    #             if (comment_box):
    #                 is_Find_comment = True
    #             time.sleep(3)
    #         except:
    #             time.sleep(3)

    #     comment_box = browser.find_element(By.ID, 'simplebox-placeholder')
    #     comment_box.click()
    #     textarea = WebDriverWait(browser, 10).until(
    #         EC.presence_of_element_located(
    #             (By.CSS_SELECTOR, "div#contenteditable-root[contenteditable='true']"))
    #     )
    #     pyperclip.copy(comment)
    #     textarea.click()
    #     time.sleep(1)
    #     textarea.send_keys(Keys.CONTROL, 'v')
    #     time.sleep(2)
    #     submit_button = WebDriverWait(browser, 10).until(
    #         EC.presence_of_element_located((By.ID, "submit-button"))
    #     )
    #     submit_button.click()

    try:
        WebDriverWait(browser, 30).until(
            EC.element_to_be_clickable((By.ID, 'secondary-action-button'))
        )
        browser.find_element(By.ID, 'secondary-action-button').click()
    except:
        print('Không tồn tại dialog')
    
    time.sleep(10)
    WebDriverWait(browser, 100).until(
        EC.presence_of_element_located(
            (By.XPATH, "//tp-yt-paper-dialog[@id='dialog']"))
    )
    browser.quit()

def trim_keywords_to_limit(keywords_str, limit=400):
    keywords = [kw.strip() for kw in keywords_str.split(',')]
    result = []
    total_length = 0

    for kw in keywords:
        kw_len = len(kw)
        # Cộng thêm 1 cho dấu phẩy nếu đã có từ trước
        if result:
            kw_len += 1
        if total_length + kw_len <= limit:
            result.append(kw)
            total_length += kw_len
        else:
            break

    return ",".join(result)

