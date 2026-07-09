
# accounts.py
import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot

# Adjusted import to match your project database structure
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

@Bot.on_message(filters.command(['myaccount', 'account']) & filters.private, group=2728973763763)
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

@Bot.on_callback_query(group=1373673)
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
            text="📝 **Person Ledger Logs** \n\nSelect an individual below to view or alter balances, or add a new log identity profile.",
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
            text = f"📊 **Global Spending Statistics**\n"
            text += f"━━━━━━━━━━━━━━━━━━━\n"
            text += f"💰 **Total Overall Spending:** ₹{total_spending:.2f}\n\n"
            text += f"👥 **Person-wise Breakdown:**\n"
            
            if people:
                for person in people:
                    text += f"• `{person['name']}`: ₹{person['spent']:.2f}\n"
            else:
                text += "*No profiles recorded yet.*"
        else:
            text = f"📉 **Global Debt Statistics**\n"
            text += f"━━━━━━━━━━━━━━━━━━━\n"
            text += f"💸 **Total Balance Payable:** ₹{total_debt:.2f}"
            
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
            
        await cb.answer("Generating cyberpunk split dashboard...")
        
        # Reference-inspired Dark Cyberpunk Layout UI
        html_raw = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DIGITAL KENSEI LEDGER - {person['name'].upper()}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Ch克兰:wght@300;400;700&family=Inter:wght@300;400;600;800&display=swap');
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{ 
                    font-family: 'Inter', sans-serif; 
                    background-color: #0b0b0c; 
                    color: #ffffff; 
                    padding: 40px 20px;
                    background-image: linear-gradient(rgba(255, 42, 42, 0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 42, 42, 0.02) 1px, transparent 1px);
                    background-size: 20px 20px;
                }}
                .container {{ max-width: 900px; margin: 0 auto; }}
                .header {{ margin-bottom: 40px; position: relative; padding-bottom: 20px; border-bottom: 1px solid #1f1f24; }}
                .brand {{ font-size: 11px; letter-spacing: 5px; color: #ff2a2a; text-transform: uppercase; font-weight: 800; margin-bottom: 8px; }}
                .title {{ font-size: 32px; font-weight: 800; letter-spacing: -0.5px; text-transform: uppercase; }}
                .grid-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 40px; }}
                .card {{ 
                    background: #111112; 
                    border: 1px solid #1f1f24; 
                    padding: 24px; 
                    border-radius: 4px;
                    position: relative;
                    overflow: hidden;
                }}
                .card::before {{
                    content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #ff2a2a;
                }}
                .card.owe-them::before {{ background: #ffffff; }}
                .card-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #8f8f93; margin-bottom: 10px; font-weight: 600; }}
                .card-val {{ font-size: 28px; font-weight: 800; letter-spacing: -0.5px; }}
                .table-container {{ background: #111112; border: 1px solid #1f1f24; border-radius: 4px; overflow: hidden; }}
                table {{ width: 100%; border-collapse: collapse; text-align: left; }}
                th {{ background: #161618; color: #8f8f93; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; padding: 16px 20px; font-weight: 700; border-bottom: 1px solid #1f1f24; }}
                td {{ padding: 16px 20px; font-size: 14px; border-bottom: 1px solid #19191b; color: #e1e1e3; }}
                tr:last-child td {{ border-bottom: none; }}
                tr:hover td {{ background: #161618; }}
                .badge {{ display: inline-block; padding: 4px 8px; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; border-radius: 2px; }}
                .badge-spent {{ background: rgba(255, 42, 42, 0.1); color: #ff2a2a; border: 1px solid rgba(255, 42, 42, 0.2); }}
                .badge-owed {{ background: rgba(255, 255, 255, 0.05); color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.1); }}
                .badge-they_paid {{ background: rgba(40, 167, 69, 0.1); color: #28a745; border: 1px solid rgba(40, 167, 69, 0.2); }}
                .badge-i_sent {{ background: rgba(0, 123, 255, 0.1); color: #007bff; border: 1px solid rgba(0, 123, 255, 0.2); }}
                .reason-text {{ font-weight: 500; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="brand">SYSTEM METRICS // SPLIT SYSTEM</div>
                    <div class="title">{person['name']}</div>
                </div>
                
                <div class="grid-stats">
                    <div class="card">
                        <div class="card-label">THEY OWE YOU (SPENT)</div>
                        <div class="card-val">₹{person['spent']:.2f}</div>
                    </div>
                    <div class="card owe-them">
                        <div class="card-label">YOU OWE THEM (DEBT)</div>
                        <div class="card-val">₹{person['owed']:.2f}</div>
                    </div>
                </div>

                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Date Time</th>
                                <th>Operation Variant</th>
                                <th>Value Allocation</th>
                                <th>Reason Context</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for tx in person["transactions"]:
            clean_type = tx['type'].replace('_', ' ').upper()
            html_raw += f"""
                            <tr>
                                <td style="color: #8f8f93;">{tx['date']}</td>
                                <td><span class="badge badge-{tx['type']}">{clean_type}</span></td>
                                <td style="font-weight: 700;">₹{tx['amount']:.2f}</td>
                                <td class="reason-text">{tx['reason']}</td>
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
            caption=f"⚡️ **Digital Kensei Dashboard Engine rendered for {person['name']}**"
        )
        
        if os.path.exists(file_name):
            os.remove(file_name)
            
    else:
        # Pass the callback execution down to your main callback file
        cb.continue_propagation()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   TEXT STATE INTERCEPTOR PIPELINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Bot.on_message(filters.private & filters.text, group=2728973)
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
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Go to Logs", callback_data="menu_log")]]),
            parse_mode=ParseMode.MARKDOWN,
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
            # Direct the engine to split sequence computation
            USER_STATES[user_id]["state"] = "awaiting_splits"
            USER_STATES[user_id]["amount"] = amount_val
            await message.reply_text("🔢 Number of Splits: How many ways should this amount be split? (Enter `1` for no division):")
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
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 View Ledger Profile", callback_data=f"view_person:{person_id}")]]),
                parse_mode=ParseMode.MARKDOWN,
            )

    elif state == "awaiting_splits":
        try:
            splits_val = int(message.text.strip())
            if splits_val < 1:
                raise ValueError
        except ValueError:
            await message.reply_text("❌ Invalid Splits! Please enter a valid integer configuration count of 1 or greater:")
            return
            
        raw_amount = current_session["amount"]
        # Split computing division calculation logic
        final_amount = raw_amount / splits_val
        
        USER_STATES[user_id]["state"] = "awaiting_reason"
        USER_STATES[user_id]["amount"] = final_amount
        await message.reply_text("🔍 Allocation context: What was this money spent on? (e.g., grocery, milk, dahi):")
            
    elif state == "awaiting_reason":
        reason_input = message.text.strip()
        person_id = current_session["person_id"]
        tx_type = current_session["tx_type"]
        amount_val = current_session["amount"]
        date_stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        await add_transaction(person_id, tx_type, amount_val, reason_input, date_stamp)
        USER_STATES.pop(user_id, None)
        
        await message.reply_text(
            text="✅ **Ledger configuration values added successfully!**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 View Updated Totals", callback_data=f"view_person:{person_id}")]])
        )
