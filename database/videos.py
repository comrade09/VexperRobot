import pymongo
from config import DB_URI, DB_NAME

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]
video_collection = database['videos']

async def save_video_code(question_code: str, message_id: int):
    video_collection.update_one(
        {'_id': question_code.upper()},
        {'$set': {'message_id': message_id}},
        upsert=True
    )

async def get_video_message_id(question_code: str):
    data = video_collection.find_one({'_id': question_code.upper()})
    if data:
        return data.get('message_id')
    return None
