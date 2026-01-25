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

# ================= COLLECTION =================

habits_col = database["habits"]


# ================= ADD HABIT =================

@bot.on_message(filters.command("addhabit"))
async def add_habit(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Use: /addhabit <habit name>")

    habit = " ".join(msg.command[1:])
    uid = msg.from_user.id

    # Prevent duplicates
    if habits_col.find_one({"user_id": uid, "habit": habit}):
        return await msg.reply("Habit already exists.")

    habits_col.insert_one({
        "user_id": uid,
        "habit": habit,
        "logs": {},
        "created": datetime.utcnow()
    })

    await msg.reply(f"✅ Added: {habit}")


# ================= /LOG =================

@bot.on_message(filters.command("log"))
async def log_menu(_, msg):

    uid = msg.from_user.id

    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits. Use /addhabit")

    buttons = []

    for h in habits:
        buttons.append(
            [InlineKeyboardButton(h["habit"], f"log:{h['_id']}")]
        )

    await msg.reply(
        "Select Habit:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= SELECT HABIT =================

@bot.on_callback_query(filters.regex("^log:"))
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

        status = habit["logs"].get(ds)

        if status is True:
            icon = "🟢"
        elif status is False:
            icon = "🔴"
        else:
            icon = "⚪"

        day_label = d.strftime("%a %d %b")
        btn_label = f"{icon} {d.strftime('%a')} {d.day}"

        text += f"{day_label}  {icon}\n"

        buttons.append([
            InlineKeyboardButton(
                btn_label,
                f"mark:{hid}:{ds}"
            )
        ])

    await cq.message.edit(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= MARK DAY =================

@bot.on_callback_query(filters.regex("^mark:"))
async def mark_day(_, cq):

    _, hid, day = cq.data.split(":")

    habit = habits_col.find_one({"_id": ObjectId(hid)})

    if not habit:
        return await cq.answer("Not found")

    current = habit["logs"].get(day)

    # Toggle: None → True → False → None
    if current is None:
        new = True
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


# ================= WEEKLY =================

@bot.on_message(filters.command("weekly"))
async def weekly_report(_, msg):

    uid = msg.from_user.id

    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    today = date.today()
    start = today - timedelta(days=6)

    text = "📊 Weekly Report\n\n"

    for h in habits:

        done = miss = 0

        for i in range(7):

            d = start + timedelta(days=i)
            val = h["logs"].get(str(d))

            if val is True:
                done += 1
            elif val is False:
                miss += 1

        text += (
            f"• {h['habit']}\n"
            f"  🟢 {done}  🔴 {miss}  ⚪ {7-done-miss}\n\n"
        )

    await msg.reply(text)


# ================= HEATMAP =================

@bot.on_message(filters.command("heatmap"))
async def heatmap(_, msg):

    uid = msg.from_user.id

    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    today = date.today()
    start = today - timedelta(days=29)

    text = "🔥 30-Day Heatmap\n\n"

    for h in habits:

        text += f"📌 {h['habit']}\n"
        row = ""

        for i in range(30):

            d = start + timedelta(days=i)
            val = h["logs"].get(str(d))

            if val is True:
                row += "🟩"
            elif val is False:
                row += "🟥"
            else:
                row += "⬜"

            if (i + 1) % 10 == 0:
                row += "\n"

        text += row + "\n\n"

    await msg.reply(text)


# ================= MONTH =================

@bot.on_message(filters.command("month"))
async def month(_, msg):

    uid = msg.from_user.id

    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    today = date.today()
    start = today - timedelta(days=29)

    text = "📊 Monthly Stats\n\n"

    for h in habits:

        text += f"🏷️ {h['habit']}\n"
        line = ""

        for i in range(30):

            d = start + timedelta(days=i)
            val = h["logs"].get(str(d))

            if val is True:
                icon = "🟢"
            elif val is False:
                icon = "🔴"
            else:
                icon = "⚪"

            line += f"{d.day:02d}{icon}  "

            if (i + 1) % 5 == 0:
                line += "\n"

        text += line + "\n\n"

    await msg.reply(text)


# ================= SINGLE HABIT =================

@bot.on_message(filters.command("habit"))
async def habit_stats(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Use: /habit <name>")

    name = " ".join(msg.command[1:]).lower()
    uid = msg.from_user.id

    habit = habits_col.find_one({
        "user_id": uid,
        "habit": {"$regex": f"^{name}$", "$options": "i"}
    })

    if not habit:
        return await msg.reply("Habit not found.")

    today = date.today()
    start = today - timedelta(days=29)

    text = f"📅 {habit['habit']} (30 Days)\n\n"

    for i in range(30):

        d = start + timedelta(days=i)
        val = habit["logs"].get(str(d))

        if val is True:
            icon = "🟢 Done"
        elif val is False:
            icon = "🔴 Missed"
        else:
            icon = "⚪ Not logged"

        text += f"{d.strftime('%d %b %a')} → {icon}\n"

    await msg.reply(text)
