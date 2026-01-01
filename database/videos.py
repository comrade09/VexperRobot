import pymongo
from config import DB_URI, DB_NAME

client = pymongo.MongoClient(DB_URI)
db = client[DB_NAME]

videos = db["videos"]

# Make sure each code is unique
videos.create_index("code", unique=True)

def add_video(code, file_id, message_id):
    """
    Add a new video.
    Returns True if added.
    Returns False if code already exists.
    """
    try:
        videos.insert_one({
            "code": code,
            "file_id": file_id,
            "message_id": message_id
        })
        return True
    except pymongo.errors.DuplicateKeyError:
        return False

def get_video(code):
    """
    Get video by code.
    Returns document or None.
    """
    return videos.find_one({"code": code})

def delete_video(code):
    """
    Delete a video by code.
    """
    return videos.delete_one({"code": code})

def count():
    """
    Total indexed videos.
    """
    return videos.count_documents({})

def all_codes():
    """
    Return list of all codes.
    """
    return [x["code"] for x in videos.find({}, {"code": 1})]
