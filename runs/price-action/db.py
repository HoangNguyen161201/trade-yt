from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import socket
# import winreg




def get_collect(name_db, name_collection):
    uri = "mongodb+srv://hoangdev161201:Cuem161201@cluster0.3o8ba2h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[name_db]
    collection = db[name_collection]
    return collection






def add_end_screen_video_ad(name, title, ad):
    collection = get_collect('news2', 'end_screen_videos')
    collection.insert_one({
        "name": name,
        "title": title,
        "ad": ad
    })


def update_end_screen_video_ad(id, title, ad):
    collection = get_collect('news2', 'end_screen_videos')
    # Truy vấn tất cả các tài liệu và chỉ lấy trường "link"
    collection.update_one({"_id": id}, {
        "$set": {
            "title": title,
            "ad": ad,
        }
    })

# get text to add video end screen
def get_end_screen_video_ad(name):
    collection = get_collect('news2', 'end_screen_videos')
    return collection.find_one({"name": name })
    