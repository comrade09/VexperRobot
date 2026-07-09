import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot

# Adjusted import to match your project structure
from database.database import (
    add_new_person, get_people, get_person_by_id, 
    add_transaction, get_total_stats
)

# In-memory session layout to track multi-step text actions
USER_STATES = {}

# Main Menu Markups
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Log Entries", callback_data="menu_log")],
        [
            InlineKeyboardButton("📊 Total Spending", callback_data="stats_spending"),
            InlineKeyboardButton("📉 Total Debt", callback_data="stats_debt")
        ]
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   COMMAND HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Bot.on_message(filters.command(['myaccount', 'account']) & filters.private,group=1334887)
async def my_account_hub(bot: Bot, message: Message):
    user_id = message.from_user.id
    USER_STATES.pop(user_id, None) # Clear any hanging state configurations
    
    await message.reply_text(
        text="🗂 **Account Management Dashboard**\n\nTrack splits, record active ledger variations, and view HTML statements seamlessly.",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   UNIFIED CALLBACK QUERY HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Bot.on_callback_query(group=133320)
async def accounts_callback_handler(bot: Bot, cb: CallbackQuery):
    data = cb.data
    if not data:
        return
        
    user_id = cb.from_user.id

    if data == "menu_main":
        USER_STATES.pop(user_id, None)
        await cb.message.edit_text(
            text="🗂 **Account Management Dashboard**\n\nTrack splits, record active ledger variations, and view HTML statements seamlessly.",
            reply_markup=main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "menu_log":
        USER_STATES.pop(user_id, None)
        people = await get_people(user_id)
        buttons = []
        row = []
        
        # Group names into 2 buttons per row
        for person in people:
            row.append(InlineKeyboardButton(person["name"], callback_data=f"view_person:{str(person['_id'])}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
            
        buttons.append([InlineKeyboardButton("➕ Add New Person", callback_data="add_person_init")])
        buttons.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")])
        
        await cb.message.edit_text(
            text="📝 **Person Ledger Logs**\n\nSelect an individual below to view or alter balances, or add a new log identity profile.",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "add_person_init":
        USER_STATES[user_id] = {"state": "awaiting_person_name"}
        await cb.message.edit_text(
            text="👤 **Add Person Profile**\n\nPlease enter the full name of the individual you want to add below:",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data.startswith("stats_"):
        stat_type = data.split("_")[1]
        total_spending, total_debt = await get_total_stats(user_id)
        
        if stat_type == "spending":
            people = await get_people(user_id)
            breakdown_text = ""
            for person in people:
                breakdown_text += f"• **{person['name']}**: ₹{person['spent']:.2f}\n"
            
            if not breakdown_text:
                breakdown_text = "_No active spending records found._\n"

            text = (
                f"📊 **Global Spending Statistics**\n\n"
                f"Total Aggregate Spending: **₹{total_spending:.2f}**\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"**Person-wise Spending Breakdown:**\n"
                f"{breakdown_text}"
            )
        else:
            text = f"📉 **Global Debt Statistics**\n\nTotal current balance owed/payable across all profiles: **₹{total_debt:.2f}**"
            
        await cb.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data.startswith("view_person:"):
        person_id = data.split(":")[1]
        person = await get_person_by_id(person_id)
        
        if not person:
            await cb.answer("Profile records could not be found.", show_alert=True)
            return
            
        text = (
            f"👤 **Account: {person['name']}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **How much they owe me:** ₹{person['spent']:.2f}\n"
            f"💸 **How much I owe them:** ₹{person['owed']:.2f}\n"
        )
        
        buttons = [
            [
                InlineKeyboardButton("Spent on Them", callback_data=f"tx_init:{person_id}:spent"),
                InlineKeyboardButton("Owe Them", callback_data=f"tx_init:{person_id}:owed")
            ],
            [
                InlineKeyboardButton("They Paid Me", callback_data=f"tx_init:{person_id}:they_paid"),
                InlineKeyboardButton("I Sent Money", callback_data=f"tx_init:{person_id}:i_sent")
            ],
            [InlineKeyboardButton("📊 Day-wise Split (HTML)", callback_data=f"html_split:{person_id}")],
            [InlineKeyboardButton("🔙 Back to Logs", callback_data="menu_log")]
        ]
        
        await cb.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("tx_init:"):
        _, person_id, tx_type = data.split(":")
        USER_STATES[user_id] = {
            "state": "awaiting_amount",
            "person_id": person_id,
            "tx_type": tx_type
        }
        
        await cb.message.edit_text(
            text="💰 **Enter Amount**\n\nPlease enter the total transaction value in INR (e.g., `45` or `500`):",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data.startswith("html_split:"):
        person_id = data.split(":")[1]
        person = await get_person_by_id(person_id)
        
        if not person or not person.get("transactions"):
            await cb.answer("No transactional metrics logged to construct a visual report for this profile yet.", show_alert=True)
            return
            
        await cb.answer("Generating ledger spreadsheet report...")
        
        html_raw = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Split Ledger - {person['name']}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --border-color: #e5e7eb;
            --primary: #4f46e5;
            --spent-bg: #fee2e2; --spent-color: #991b1b;
            --owed-bg: #ffedd5; --owed-color: #9a3412;
            --paid-bg: #dcfce7; --paid-color: #166534;
            --sent-bg: #dbeafe; --sent-color: #1e40af;
        }}
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            width: 100%;
            max-width: 900px;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 28px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
            margin-bottom: 24px;
            border: 1px solid var(--border-color);
        }}
        .card h2 {{
            margin-top: 0;
            font-size: 24px;
            font-weight: 700;
            color: var(--text-main);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 16px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        .stat-box {{
            padding: 16px;
            border-radius: 8px;
            background-color: #f9fafb;
            border: 1px solid var(--border-color);
        }}
        .stat-box span {{
            display: block;
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 500;
            margin-bottom: 4px;
        }}
        .stat-box strong {{
            font-size: 20px;
            font-weight: 700;
        }}
        .table-wrapper {{
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        th {{
            background-color: #f9fafb;
            color: var(--text-muted);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 14px 20px;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        tr:hover {{
            background-color: #f9fafb;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }}
        .type-spent {{ background: var(--spent-bg); color: var(--spent-color); }}
        .type-owed {{ background: var(--owed-bg); color: var(--owed-color); }}
        .type-they_paid {{ background: var(--paid-bg); color: var(--paid-color); }}
        .type-i_sent {{ background: var(--sent-bg); color: var(--sent-color); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>Transaction Split Report: {person['name']}</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <span>They Owe You</span>
                    <strong style="color: #059669;">₹{person['spent']:.2f}</strong>
                </div>
                <div class="stat-box">
                    <span>You Owe Them</span>
                    <strong style="color: #dc2626;">₹{person['owed']:.2f}</strong>
                </div>
            </div>
        </div>
        
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Date & Time</th>
                        <th>Action</th>
                        <th>Amount</th>
                        <th>Reason / Allocation</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for tx in person["transactions"]:
            clean_type = tx['type'].replace('_', ' ').title()
            html_raw += f"""
                    <tr>
                        <td style="color: var(--text-muted);">{tx['date']}</td>
                        <td><span class="badge type-{tx['type']}">{clean_type}</span></td>
                        <td style="font-weight: 600;">₹{tx['amount']:.2f}</td>
                        <td>{tx['reason']}</td>
                    </tr>
            """
            
        html_raw += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        """
        
        file_name = f"split_{person_id}.html"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html_raw)
            
        await bot.send_document(
            chat_id=cb.message.chat.id,
            document=file_name,
            caption=f"📊 **Day-wise ledger breakdown report for {person['name']}**"
        )
        
        if os.path.exists(file_name):
            os.remove(file_name)
            
    else:
        cb.continue_propagation()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   TEXT STATE INTERCEPTOR PIPELINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Bot.on_message(filters.private & filters.text, group=4531)
async def state_input_processor(bot: Bot, message: Message):
    if message.text.startswith("/"):
        return
        
    user_id = message.from_user.id
    if user_id not in USER_STATES:
        return
        
    current_session = USER_STATES[user_id]
    state = current_session["state"]
    
    if state == "awaiting_person_name":
        name_input = message.text.strip()
        await add_new_person(user_id, name_input)
        USER_STATES.pop(user_id, None)
        
        await message.reply_text(
            text=f"✅ **Success!** Added **{name_input}** to log directory records.\n\nPress /myaccount to refresh active screens.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Go to Logs", callback_data="menu_log")]])
        )
        
    elif state == "awaiting_amount":
        try:
            amount_val = float(message.text.strip())
            if amount_val <= 0:
                raise ValueError
        except ValueError:
            await message.reply_text("❌ **Invalid Value!** Please respond with a valid numerical positive figure:")
            return
            
        person_id = current_session["person_id"]
        tx_type = current_session["tx_type"]
        
        if tx_type == "spent":
            USER_STATES[user_id]["state"] = "awaiting_splits"
            USER_STATES[user_id]["total_amount"] = amount_val
            await message.reply_text("🔢 **Number of Splits:** How many people are splitting this amount? (Enter `1` if no split):")
            
        elif tx_type == "owed":
            USER_STATES[user_id]["state"] = "awaiting_reason"
            USER_STATES[user_id]["amount"] = amount_val
            await message.reply_text("🔍 **Allocation context:** What was this money spent on? (e.g., *grocery, milk, dahi*):")
            
        else:
            default_reason = "Repayment Settle" if tx_type == "they_paid" else "Funds Remittance"
            date_stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            await add_transaction(person_id, tx_type, amount_val, default_reason, date_stamp)
            USER_STATES.pop(user_id, None)
            
            await message.reply_text(
                text="✅ **Payment log adjustments adjusted successfully!**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 View Ledger Profile", callback_data=f"view_person:{person_id}")]])
            )

    elif state == "awaiting_splits":
        try:
            splits_count = int(message.text.strip())
            if splits_count < 1:
                raise ValueError
        except ValueError:
            await message.reply_text("❌ **Invalid Split Number!** Please enter a positive whole number (e.g., `1`, `2`, `3`):")
            return

        total_amount = current_session["total_amount"]
        final_amount = total_amount / splits_count if splits_count > 1 else total_amount

        USER_STATES[user_id]["state"] = "awaiting_reason"
        USER_STATES[user_id]["amount"] = final_amount
        
        split_info = f" (Original Amount: ₹{total_amount:.2f} divided by {splits_count} = **₹{final_amount:.2f}**)" if splits_count > 1 else ""
        
        await message.reply_text(f"🔍 **Allocation context:** What was this money spent on?{split_info}\n(e.g., *grocery, milk, dahi*):")

    elif state == "awaiting_reason":
        reason_input = message.text.strip()
        person_id = current_session["person_id"]
        tx_type = current_session["tx_type"]
        amount_val = current_session["amount"]
        date_stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        await add_transaction(person_id, tx_type, amount_val, reason_input, date_stamp)
        USER_STATES.pop(user_id, None)
        
        await message.reply_text(
            text="✅ **Ledger ledger configuration values added successfully!**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 View Updated Totals", callback_data=f"view_person:{person_id}")]])
        )
