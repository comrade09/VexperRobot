import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import BOT_USERNM

# Set the target date for NEET 2027 (May 2, 2027, 00:00:00)
NEET_2027_DATE = datetime(2027, 5, 2, 0, 0, 0)

@Bot.on_callback_query(group=16564)
async def neet_countdown_cb(client: Bot, query: CallbackQuery):
    data = query.data
    
    if data in ["neet_countdown", "refresh_countdown"]:
        now = datetime.now()
        time_difference = NEET_2027_DATE - now
        
        # Calculate days, hours, minutes, and seconds
        if time_difference.total_seconds() > 0:
            days = time_difference.days
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            countdown_text = (
                f"🎓 **NEET 2027 COUNTDOWN** 🎓\n\n"
                f"🎯 **Target Date:** 02 May 2027\n"
                f"⏳ **Time Remaining:**\n\n"
                f"**{days}** Days\n"
                f"**{hours}** Hours\n"
                f"**{minutes}** Minutes\n"
                f"**{seconds}** Seconds\n\n"
                f"💡 *Keep studying hard! Every second counts.*"
            )
        else:
            countdown_text = (
                "🎓 **NEET 2027 COUNTDOWN** 🎓\n\n"
                "🎯 The exam day has arrived or passed! Best of luck!"
            )

        # Updated Keyboard with "success" (green) style
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔄 Refresh", 
                        callback_data="refresh_countdown",
                        style="success"  # Renders a Green Button
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back to Main Menu", 
                        callback_data="help_six"  # Assuming 'help_six' based on your previous back buttons
                    ) 
                ]
            ]
        )

        try:
            if query.message.photo:
                await query.message.edit_caption(
                    caption=countdown_text,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.message.edit_text(
                    text=countdown_text,
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            if data == "refresh_countdown":
                await query.answer("Refreshed! 🔄")
            else:
                await query.answer()
                
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                await query.answer("Wait a second before refreshing again!", show_alert=False)
            else:
                print(f"Error in countdown: {e}")
                await query.answer("An error occurred.", show_alert=True)
