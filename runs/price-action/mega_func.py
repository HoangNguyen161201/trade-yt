from mega import Mega
import time
import os 

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