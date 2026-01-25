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

# plugins/habits/handlers.py

import asyncio
from datetime import date, timedelta, datetime

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bson import ObjectId

from bot import Bot
from database.database import database


# ================= COLLECTION =================

habits_col = database["habits"]

# ================= DISTRIBUTED LOCK =================

lock_col = database["habit_lock"]


async def acquire_lock():

    now = datetime.utcnow()

    expire = now + timedelta(minutes=2)

    res = lock_col.find_one_and_update(
        {
            "$or": [
                {"expires": {"$lt": now}},
                {"expires": {"$exists": False}}
            ]
        },
        {
            "$set": {
                "expires": expire
            }
        },
        upsert=True,
        return_document=True
    )

    return res is not None

# ================= STREAK CALCULATOR =================

def get_streaks(logs: dict):

    if not logs:
        return 0, 0

    dates = sorted(
        [date.fromisoformat(d) for d, v in logs.items() if v is True]
    )

    if not dates:
        return 0, 0

    # Best streak
    best = 1
    temp = 1

    for i in range(1, len(dates)):

        if (dates[i] - dates[i - 1]).days == 1:
            temp += 1
            best = max(best, temp)
        else:
            temp = 1

    # Current streak
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


# ================= BACKGROUND WATCHER =================

async def habit_watcher():

    while True:

        try:

            # Try to become leader
            is_leader = await acquire_lock()

            if not is_leader:
                await asyncio.sleep(60)
                continue

            now = datetime.now()

            # 9:30 PM Reminder
            if now.hour == 21 and now.minute == 30:
                await smart_reminder()

            # Midnight Check
            if now.hour == 0 and now.minute == 5:
                await daily_check()

        except Exception as e:
            print("Habit Watcher Error:", e)

        await asyncio.sleep(60)



# ================= SMART REMINDER =================

async def smart_reminder():

    users = habits_col.distinct("user_id")
    today = str(date.today())

    for uid in users:

        habits = list(habits_col.find({"user_id": uid}))

        pending = []

        for h in habits:

            if h["logs"].get(today) is None:
                pending.append(h["habit"])

        if pending:

            text = "⏰ Night Reminder\n\nYou haven't logged:\n\n"

            for p in pending:
                text += f"❌ {p}\n"

            text += "\nDon’t break the streak."

            try:
                await Bot.send_message(uid, text)
            except:
                pass


# ================= DAILY CHECK =================

async def daily_check():

    yesterday = str(date.today() - timedelta(days=1))

    users = habits_col.distinct("user_id")

    for uid in users:

        habits = list(habits_col.find({"user_id": uid}))

        for h in habits:

            logs = h["logs"]

            cur, best = get_streaks(logs)

            # Missed alert
            if logs.get(yesterday) is False:

                try:
                    await Bot.send_message(
                        uid,
                        f"⚠️ You missed **{h['habit']}** yesterday.\nFix it today."
                    )
                except:
                    pass

            # Streak broken
            if cur == 0 and best >= 5:

                try:
                    await Bot.send_message(
                        uid,
                        f"💔 Streak broken: **{h['habit']}** ({best} days)\nRestart today."
                    )
                except:
                    pass


# ================= ADD HABIT =================

@Bot.on_message(filters.command("addhabit"),group=869889)
async def add_habit(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Use: /addhabit <habit name>")

    habit = " ".join(msg.command[1:])
    uid = msg.from_user.id

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

@Bot.on_message(filters.command("log"),group=86988954)
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

@Bot.on_callback_query(filters.regex("^log:"),group=866569889)
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

        text += f"{d.strftime('%a %d %b')}  {icon}\n"

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


# ================= MARK DAY =================

@Bot.on_callback_query(filters.regex("^mark:"),group=869535)
async def mark_day(_, cq):

    _, hid, day = cq.data.split(":")

    habit = habits_col.find_one({"_id": ObjectId(hid)})

    if not habit:
        return await cq.answer("Not found")

    current = habit["logs"].get(day)

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
# ================= DELETE HABIT (BUTTON) =================

@Bot.on_message(filters.command("delete"),group=756567)
async def delete_menu(_, msg):

    uid = msg.from_user.id

    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits to delete.")

    buttons = []

    for h in habits:
        buttons.append([
            InlineKeyboardButton(
                f"🗑️ {h['habit']}",
                f"del:{h['_id']}"
            )
        ])

    await msg.reply(
        "Select habit to delete:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Bot.on_callback_query(filters.regex("^del:"),group=75675)
async def delete_confirm(_, cq):

    hid = cq.data.split(":")[1]

    habit = habits_col.find_one({"_id": ObjectId(hid)})

    if not habit:
        return await cq.answer("Not found")

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Cancel", "del_cancel"),
            InlineKeyboardButton("✅ Delete", f"del_yes:{hid}")
        ]
    ])

    await cq.message.edit(
        f"⚠️ Delete **{habit['habit']}** ?\nThis cannot be undone.",
        reply_markup=buttons
    )


@Bot.on_callback_query(filters.regex("^del_yes:"))
async def delete_final(_, cq):

    hid = cq.data.split(":")[1]

    habits_col.delete_one({"_id": ObjectId(hid)})

    await cq.message.edit("✅ Habit deleted.")


@Bot.on_callback_query(filters.regex("^del_cancel"),group=8667)
async def delete_cancel(_, cq):

    await cq.message.edit("❌ Cancelled.")


# ================= WEEKLY =================

@Bot.on_message(filters.command("weekly"),group=869433)
async def weekly_report(_, msg):

    uid = msg.from_user.id
    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    today = date.today()
    start = today - timedelta(days=6)

    text = "📊 Weekly Report\n\n"

    for h in habits:

        cur, best = get_streaks(h["logs"])

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
            f"  🟢 {done}  🔴 {miss}  ⚪ {7-done-miss}\n"
            f"  🔥 {cur}  🏆 {best}\n\n"
        )

    await msg.reply(text)


# ================= HEATMAP =================

@Bot.on_message(filters.command("heatmap"),group=869889545)
async def heatmap(_, msg):

    uid = msg.from_user.id
    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    today = date.today()
    start = today - timedelta(days=29)

    text = "🔥 30-Day Heatmap\n\n"

    for h in habits:

        cur, best = get_streaks(h["logs"])

        text += f"📌 {h['habit']} 🔥{cur} 🏆{best}\n"

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

@Bot.on_message(filters.command("month"),group=86988942)
async def month(_, msg):

    uid = msg.from_user.id
    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    today = date.today()
    start = today - timedelta(days=29)

    text = "📊 Monthly Stats\n\n"

    for h in habits:

        cur, best = get_streaks(h["logs"])

        text += f"🏷️ {h['habit']} 🔥{cur} 🏆{best}\n"

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

@Bot.on_message(filters.command("habit"),group=8694343)
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

    cur, best = get_streaks(habit["logs"])

    today = date.today()
    start = today - timedelta(days=29)

    text = (
        f"📅 {habit['habit']} (30 Days)\n"
        f"🔥 Current: {cur}  🏆 Best: {best}\n\n"
    )

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


# ================= DASHBOARD =================

@Bot.on_message(filters.command("life"),group=765635355)
async def dashboard(_, msg):

    uid = msg.from_user.id
    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    total = len(habits)
    score = 0

    text = "📊 Life Dashboard\n\n"

    for h in habits:

        cur, best = get_streaks(h["logs"])
        score += cur

        text += f"• {h['habit']} → 🔥{cur} 🏆{best}\n"

    discipline = min(100, int((score / (total * 7)) * 100))

    text += f"\n💯 Life Score: {discipline}/100"

    await msg.reply(text)


# ================= MONTHLY COMPARE =================

@Bot.on_message(filters.command("compare"),group=894366)
async def compare(_, msg):

    uid = msg.from_user.id
    habits = list(habits_col.find({"user_id": uid}))

    if not habits:
        return await msg.reply("No habits.")

    today = date.today()

    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)

    text = "📈 Monthly Comparison\n\n"

    for h in habits:

        cur_m = 0
        prev_m = 0

        for d, v in h["logs"].items():

            d = date.fromisoformat(d)

            if v is True:

                if d >= this_month:
                    cur_m += 1

                elif last_month <= d < this_month:
                    prev_m += 1

        diff = cur_m - prev_m
        sign = "+" if diff >= 0 else ""

        text += f"• {h['habit']}: {prev_m} → {cur_m} ({sign}{diff})\n"

    await msg.reply(text)


