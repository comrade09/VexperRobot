# plugins/habits/handlers.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import date, timedelta, datetime
from database.database import database


from database.database import add_user, del_user, full_userbase, present_user

from bson import ObjectId
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM

# plugins/habits/handlers.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import date, timedelta, datetime
from database.database import database

from bson import ObjectId
from bot import Bot


# ================= COLLECTION =================

habits_col = database["habits"]


# ================= STREAK =================

def get_streaks(logs: dict):

    if not logs:
        return 0, 0

    dates = sorted(
        [date.fromisoformat(d) for d, v in logs.items() if v is True]
    )

    if not dates:
        return 0, 0

    best = 1
    temp = 1

    for i in range(1, len(dates)):

        if (dates[i] - dates[i - 1]).days == 1:
            temp += 1
            best = max(best, temp)
        else:
            temp = 1

    today = date.today()
    cur = 0
    d = today

    while True:

        if logs.get(str(d)) is True:
            cur += 1
            d -= timedelta(days=1)
        else:
            break

    return cur, best


# ================= GAMIFICATION =================

def calc_level(xp):
    return max(1, xp // 100 + 1)


def get_badges(streak, best, xp):

    badges = []

    if best >= 7:
        badges.append("🥉 7-Day Streak")

    if best >= 30:
        badges.append("🥈 30-Day Streak")

    if best >= 90:
        badges.append("🥇 90-Day Streak")

    if xp >= 500:
        badges.append("💎 500 XP")

    if xp >= 1000:
        badges.append("👑 1000 XP")

    return badges


# ================= ADD =================

@Bot.on_message(filters.command("addhabit"), group=869889)
async def add_habit(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Use: /addhabit <name>")

    habit = " ".join(msg.command[1:])
    uid = msg.from_user.id

    if habits_col.find_one({"user_id": uid, "habit": habit}):
        return await msg.reply("Already exists.")

    habits_col.insert_one({
        "user_id": uid,
        "habit": habit,
        "logs": {},
        "xp": 0,
        "level": 1,
        "created": datetime.utcnow()
    })

    await msg.reply(f"✅ Added: {habit}")


# ================= LOG =================

@Bot.on_message(filters.command("log"), group=86988954)
async def log_menu(_, msg):

    uid = msg.from_user.id
    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    buttons = []

    for h in habits:
        buttons.append([
            InlineKeyboardButton(h["habit"], f"log:{h['_id']}")
        ])

    await msg.reply(
        "Select Habit:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= SELECT =================

@Bot.on_callback_query(filters.regex("^log:"), group=866569889)
async def select_habit(_, cq):

    hid = cq.data.split(":")[1]
    habit = habits_col.find_one({"_id": ObjectId(hid)})

    if not habit:
        return await cq.answer("Not found")

    today = date.today()

    text = f"📅 {habit['habit']}\n\n"
    buttons = []

    for i in range(6, -1, -1):

        d = today - timedelta(days=i)
        ds = str(d)

        val = habit["logs"].get(ds)

        if val is True:
            icon = "🟢"
        elif val is False:
            icon = "🔴"
        else:
            icon = "⚪"

        text += f"{d.strftime('%a %d %b')} {icon}\n"

        buttons.append([
            InlineKeyboardButton(
                f"{icon} {d.strftime('%a')} {d.day}",
                f"mark:{hid}:{ds}"
            )
        ])

    await cq.message.edit(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= MARK =================

@Bot.on_callback_query(filters.regex("^mark:"), group=869535)
async def mark_day(_, cq):

    _, hid, day = cq.data.split(":")

    habit = habits_col.find_one({"_id": ObjectId(hid)})

    if not habit:
        return await cq.answer("Not found")

    current = habit["logs"].get(day)

    if current is None:
        new = True

        old_xp = habit.get("xp", 0)
        new_xp = old_xp + 10
        lvl = calc_level(new_xp)

        habits_col.update_one(
            {"_id": habit["_id"]},
            {"$set": {"xp": new_xp, "level": lvl}}
        )

    elif current is True:
        new = False
    else:
        new = None

    if new is None:

        habits_col.update_one(
            {"_id": habit["_id"]},
            {"$unset": {f"logs.{day}": ""}}
        )

    else:

        habits_col.update_one(
            {"_id": habit["_id"]},
            {"$set": {f"logs.{day}": new}}
        )

    await select_habit(_, cq)


# ================= DELETE =================

@Bot.on_message(filters.command("delete"), group=756567)
async def delete_menu(_, msg):

    uid = msg.from_user.id
    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    buttons = []

    for h in habits:
        buttons.append([
            InlineKeyboardButton(
                f"🗑️ {h['habit']}",
                f"del:{h['_id']}"
            )
        ])

    await msg.reply(
        "Select habit:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Bot.on_callback_query(filters.regex("^del:"), group=7565675)
async def delete_confirm(_, cq):

    hid = cq.data.split(":")[1]

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Cancel", "del_cancel"),
            InlineKeyboardButton("✅ Delete", f"del_yes:{hid}")
        ]
    ])

    await cq.message.edit(
        "⚠️ Confirm delete?",
        reply_markup=buttons
    )


@Bot.on_callback_query(filters.regex("^del_yes:"), group=786724434)
async def delete_final(_, cq):

    hid = cq.data.split(":")[1]
    habits_col.delete_one({"_id": ObjectId(hid)})

    await cq.message.edit("✅ Deleted.")


@Bot.on_callback_query(filters.regex("^del_cancel"), group=8667)
async def delete_cancel(_, cq):

    await cq.message.edit("❌ Cancelled.")


# ================= EDIT =================

@Bot.on_message(filters.command("edithabit"), group=7867244545)
async def edit_habit(_, msg):

    if "|" not in msg.text:
        return await msg.reply("Use: /edithabit Old | New")

    old, new = msg.text.split("|", 1)

    old = old.replace("/edithabit", "").strip()
    new = new.strip()

    uid = msg.from_user.id

    res = habits_col.find_one_and_update(
        {
            "user_id": uid,
            "habit": {"$regex": f"^{old}$", "$options": "i"}
        },
        {"$set": {"habit": new}}
    )

    if not res:
        return await msg.reply("Not found.")

    await msg.reply("✅ Updated.")


# ================= GOAL =================

@Bot.on_message(filters.command("setgoal"), group=78672665)
async def set_goal(_, msg):

    if len(msg.command) < 3:
        return await msg.reply("Use: /setgoal Habit 5")

    name = msg.command[1]

    try:
        goal = int(msg.command[2])
    except:
        return await msg.reply("Invalid number.")

    uid = msg.from_user.id

    res = habits_col.find_one_and_update(
        {
            "user_id": uid,
            "habit": {"$regex": f"^{name}$", "$options": "i"}
        },
        {"$set": {"goal": goal}}
    )

    if not res:
        return await msg.reply("Not found.")

    await msg.reply("🎯 Goal set.")


# ================= NOTE =================

@Bot.on_message(filters.command("note"), group=786724434334)
async def add_note(_, msg):

    if len(msg.command) < 3:
        return await msg.reply("Use: /note Habit text")

    habit_name = msg.command[1]
    note = " ".join(msg.command[2:])

    uid = msg.from_user.id
    today = str(date.today())

    res = habits_col.find_one_and_update(
        {
            "user_id": uid,
            "habit": {"$regex": f"^{habit_name}$", "$options": "i"}
        },
        {"$set": {f"notes.{today}": note}}
    )

    if not res:
        return await msg.reply("Not found.")

    await msg.reply("📝 Saved.")


# ================= PROFILE =================

@Bot.on_message(filters.command("profile"), group=784367234)
async def profile(_, msg):

    uid = msg.from_user.id
    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    total_xp = 0
    total_done = 0
    total_days = 0

    text = "🎮 Profile\n\n"

    for h in habits:

        logs = h["logs"]

        done = sum(1 for v in logs.values() if v is True)
        total = len(logs)

        xp = h.get("xp", 0)
        total_xp += xp

        cur, best = get_streaks(logs)

        percent = int((done / total) * 100) if total else 0

        badges = get_badges(cur, best, xp)
        badge_text = ", ".join(badges) if badges else "None"

        total_done += done
        total_days += total

        text += (
            f"📌 {h['habit']}\n"
            f"Progress: {percent}%\n"
            f"🔥 {cur} | 🏆 {best}\n"
            f"XP: {xp}\n"
            f"Badges: {badge_text}\n\n"
        )

    level = calc_level(total_xp)
    overall = int((total_done / total_days) * 100) if total_days else 0

    text += (
        f"━━━━━━━━━━━━━━\n"
        f"Level: {level}\n"
        f"XP: {total_xp}\n"
        f"Overall: {overall}%"
    )

    await msg.reply(text)
