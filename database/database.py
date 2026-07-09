import pymongo, os
from config import DB_URI, DB_NAME
from bson import ObjectId

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
# New collection for tracking person accounts
accounts_data = database['accounts']

async def present_user(user_id : int):
    found = user_data.find_one({'_id': user_id})
    if found:
        return True
    else:
        return False

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return

# --- NEW ACCOUNTS LOGIC (DO NOT REMOVE ABOVE FUNCTIONS) ---

async def add_new_person(user_id: int, name: str):
    accounts_data.insert_one({
        "user_id": user_id,
        "name": name,
        "spent": 0.0,  # Money they owe me
        "owed": 0.0,   # Money I owe them
        "transactions": []
    })

async def get_people(user_id: int):
    return list(accounts_data.find({"user_id": user_id}))

async def get_person_by_id(person_id: str):
    return accounts_data.find_one({"_id": ObjectId(person_id)})

async def add_transaction(person_id: str, tx_type: str, amount: float, reason: str, date_str: str):
    inc_fields = {}
    if tx_type == 'spent':
        inc_fields["spent"] = amount
    elif tx_type == 'owed':
        inc_fields["owed"] = amount
    elif tx_type == 'they_paid':
        inc_fields["spent"] = -amount  # Reduces what they owe me
    elif tx_type == 'i_sent':
        inc_fields["owed"] = -amount   # Reduces what I owe them

    accounts_data.update_one(
        {"_id": ObjectId(person_id)},
        {
            "$inc": inc_fields,
            "$push": {
                "transactions": {
                    "date": date_str,
                    "amount": amount,
                    "type": tx_type,
                    "reason": reason
                }
            }
        }
    )

async def get_total_stats(user_id: int):
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "total_spending": {"$sum": "$spent"},
            "total_debt": {"$sum": "$owed"}
        }}
    ]
    result = list(accounts_data.aggregate(pipeline))
    if result:
        return result[0].get("total_spending", 0.0), result[0].get("total_debt", 0.0)
    return 0.0, 0.0
