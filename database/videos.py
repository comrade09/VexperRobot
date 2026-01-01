import pymongo
from config import DB_URI, DB_NAME

client = pymongo.MongoClient(DB_URI)
db = client[DB_NAME]

videos = db["videos"]
videos.create_index("code", unique=True)

def add_video(code, file_id, message_id):
    try:
        videos.insert_one({
            "code": code,
            "file_id": file_id,
            "message_id": message_id
        })
        return True
    except pymongo.errors.DuplicateKeyError:
        return False

def count():
    return videos.count_documents({})
