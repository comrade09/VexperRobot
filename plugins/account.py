
#import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot

# Adjusted import to match your project structure
from database.database import add_new_person, get_people, get_person_by_id, add_transaction, get_total_stats

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

@Bot.on_message(filters.command(['myaccount', 'account']) & filters.private,group=389288383783)
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

@Bot.on_callback_query(group=1456550)
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
            text = f"📊 **Global Spending Statistics**\n\nTotal aggregate amount spent across all logged identities: **₹{total_spending:.2f}**"
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
            text="💰 **Enter Amount**\n\nPlease enter the structural transaction value in INR (e.g., `45` or `500`):",
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
        <html>
        <head>
            <title>Split Ledger - {person['name']}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f8f9fa; color: #212529; }}
                h2 {{ color: #495057; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }}
                .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: #fff; }}
                th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #dee2e6; }}
                th {{ background-color: #6c757d; color: white; text-transform: uppercase; font-size: 13px; }}
                tr:hover {{ background-color: #f1f3f5; }}
                .type-spent {{ color: #dc3545; font-weight: 600; }}
                .type-owed {{ color: #fd7e14; font-weight: 600; }}
                .type-they_paid {{ color: #28a745; font-weight: 600; }}
                .type-i_sent {{ color: #007bff; font-weight: 600; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Transaction Split Report: {person['name']}</h2>
                <p><strong>They owe you:</strong> INR {person['spent']:.2f}</p>
                <p><strong>You owe them:</strong> INR {person['owed']:.2f}</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Date Time</th>
                        <th>Action Modification</th>
                        <th>Value (INR)</th>
                        <th>Reason / Allocation</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for tx in person["transactions"]:
            clean_type = tx['type'].replace('_', ' ').title()
            html_raw += f"""
                    <tr>
                        <td>{tx['date']}</td>
                        <td><span class="type-{tx['type']}">{clean_type}</span></td>
                        <td>₹{tx['amount']:.2f}</td>
                        <td>{tx['reason']}</td>
                    </tr>
            """
            
        html_raw += """
                </tbody>
            </table>
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
        # Pass the callback execution down to your main callback file (e.g. group 6754674)
        cb.continue_propagation()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   TEXT STATE INTERCEPTOR PIPELINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Bot.on_message(filters.private & filters.text, group=43434555321)
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
        
        if tx_type in ["spent", "owed"]:
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
