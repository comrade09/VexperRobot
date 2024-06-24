import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM
import time
import random

ELP_LINK = "https://t.me/+0YrmrOzS40wzYTU1"

trigger_responses = {
    "thank": {
        "text_options": [
            "Pyrogram is a great library for working with the Telegram API!",
            "Did you know Pyrogram is based on asyncio?",
            "Learning Pyrogram? Ask me anything!",
            "bhai, thanks bolna kyu   We're like the Gandhis of coolness, spreading non-violent vibes and smiles. ✌️😄",
            "Arey bade bade log, thanking me is like thanking the moon for being bright – I'm just naturally radiant. 🌕💫",
            "Thanks? We're like the WiFi in your life – you never realize how much you need us until we're gone. 📶😏",
            "No need for thanks, yaar! We're like the weather forecast – predicting a 100 percent chance of good times whenever we're around. ☀️",
            "Thank you? We're the stand-up comedians of friendship, always ready to deliver the punchline of joy. 🎤😂",
            "Oh, thanks mat bol yaar! We're the architects of amusement, building bridges of laughter between us. 🏗️😄",
            "Bro, thanking me is like thanking your phone for having a sense of humor – it's just programmed that way! 📱🤣",
            "Thanks? We're like the Batman and Robin of banter, fighting the crime of boredom in Gotham City. 🦇🤘",
            "No need for gratitude, my friend! We're like the GPS of happiness, recalculating routes and always finding the scenic path. 🗺️😎",
            "Thank you? We're the magicians of mirth, making smiles appear out of thin air. Ta-da! 🎩😁",
            "Oh bhai, thanking me is like thanking the sun for shining – I'm just naturally brilliant. ☀️😎",
            "No need for thanks, buddy! We're like the secret agents of good times, undercover and always on a mission to have fun. 🕵️‍♂️🎉",
            "Thank you? We're the Jedi knights of laughter, using the Force to keep the humor strong. May the laughter be with you! 🌌😂",
            "Thanks yaar, but let's be real – we're the rockstars of everyday life, rocking the stage of friendship! 🎸🤘",
            "Oh, thanks mat bol, bro! We're the GPS of friendship, recalculating routes and always finding our way back to awesome. 🗺️😄",
            "Arey bade bade log, thanking me? We're like the pizza delivery guys of good times – always on time and everyone's favorite! 🍕😜",
            "Thank you? Nahin yaar, we're like the emojis in the chat, expressing feelings without saying a word! 😂🤷‍♂️",
            "Bro, thanking me is like thanking coffee for waking you up – it's just what I do, keeping you alert and entertained! ☕🤣",
            "Thanks? We're the unsung heroes of banter, fighting boredom one witty remark at a time. Stay epic, my friend! 🦸‍♂️💬",
            "No need for formalities, my dude! We're like the Avengers of humor, saving the world from seriousness. 🦸‍♂️🌍"
            "Arrey bhai, no thanks needed, yaar! We're like Batman and Robin, saving the day with our awesomeness. 🦸‍♂️🦸‍♂️",
            "Oh please, thanking me is like thanking gravity for keeping us grounded. It's just doing its job! 🌍😄",
            "Thanks? Bro, we're just the background dancers in the Bollywood movie of life. Keep the music playing! 💃🕺",
            "Thank you? Nahin yaar, we're just the sidekicks in this epic saga called friendship. Cheers to us! 🥂😎",
            "No need for thanks, buddy! We're like Wi-Fi – silently making things happen in the background. 📶😏",
            "Arey bade bade log, thanks kyun? We're just the Sherlock and Watson of coolness, solving the mysteries of life. 🔍🕵️‍♂️",
            "Thank you? We're like emojis in a text, adding that extra dose of flair to the conversation! 😜👌",
            "Bro, thanking me is like thanking Google for answers – it's what I'm here for! 🤖💻",
            "Thanks bhai, but remember, we're just two peas in a pod, navigating the chaos of life together. 🌱🤷‍♂️",
             "No need for formalities, yaar! We're like the GPS of coolness, guiding each other through the twists and turns of life. 🗺️😎",
             "Thank you? We're just the unsung heroes of everyday adventures, like the Robin Hood of good vibes. 🏹🌈",
             "Bro, thanks is like an app update – not necessary but always appreciated! 📲🤣",
             "Oh, thanks mat bol yaar! We're like a sitcom, and you're the awesome co-star stealing the show! 🎭🌟",
             "Thank you? Bhai, we're the magicians of joy, making smiles appear out of thin air. 🎩😁",
             "No need for gratitude, amigo! We're like salt in a dish – small but essential for the perfect flavor. 🧂👌",
             "Thanks? We're just the DJs of happiness, spinning tracks that make life one epic dance party. 🎧💃",
             "Thank you? We're the architects of laughter, building bridges of joy in this crazy world. 🏗️😂",
             "Oh bhai, no need for thanks! We're like the Avengers of everyday life, fighting boredom and spreading cheer. 🦸‍♂️🌟",
             "Thank you? We're like a good cup of chai – comforting, essential, and always there when you need a pick-me-up. ☕😌",
             "Thanks mat bol yaar! We're the Gandalfs of friendship, bringing a touch of magic to each other's journeys. 🧙‍♂️✨"
        ],
        "sticker_id": "CAACAgUAAxkBAAIM2WVuXSKjb5hD7Ira3MNtHkQvvfyLAALFEQACFORxV6azoG5YB84EHgQ"  # Add the actual sticker ID here
    },
    "thanks": {
        "text_options": [
            "Pyrogram is a great library for working with the Telegram API!",
            "Did you know Pyrogram is based on asyncio?",
            "Learning Pyrogram? Ask me anything!",
            "bhai, thanks bolna kyu   We're like the Gandhis of coolness, spreading non-violent vibes and smiles. ✌️😄",
            "Arey bade bade log, thanking me is like thanking the moon for being bright – I'm just naturally radiant. 🌕💫",
            "Thanks? We're like the WiFi in your life – you never realize how much you need us until we're gone. 📶😏",
            "No need for thanks, yaar! We're like the weather forecast – predicting a 100 percent chance of good times whenever we're around. ☀️",
            "Thank you? We're the stand-up comedians of friendship, always ready to deliver the punchline of joy. 🎤😂",
            "Oh, thanks mat bol yaar! We're the architects of amusement, building bridges of laughter between us. 🏗️😄",
            "Bro, thanking me is like thanking your phone for having a sense of humor – it's just programmed that way! 📱🤣",
            "Thanks? We're like the Batman and Robin of banter, fighting the crime of boredom in Gotham City. 🦇🤘",
            "No need for gratitude, my friend! We're like the GPS of happiness, recalculating routes and always finding the scenic path. 🗺️😎",
            "Thank you? We're the magicians of mirth, making smiles appear out of thin air. Ta-da! 🎩😁",
            "Oh bhai, thanking me is like thanking the sun for shining – I'm just naturally brilliant. ☀️😎",
            "No need for thanks, buddy! We're like the secret agents of good times, undercover and always on a mission to have fun. 🕵️‍♂️🎉",
            "Thank you? We're the Jedi knights of laughter, using the Force to keep the humor strong. May the laughter be with you! 🌌😂",
            "Thanks yaar, but let's be real – we're the rockstars of everyday life, rocking the stage of friendship! 🎸🤘",
            "Oh, thanks mat bol, bro! We're the GPS of friendship, recalculating routes and always finding our way back to awesome. 🗺️😄",
            "Arey bade bade log, thanking me? We're like the pizza delivery guys of good times – always on time and everyone's favorite! 🍕😜",
            "Thank you? Nahin yaar, we're like the emojis in the chat, expressing feelings without saying a word! 😂🤷‍♂️",
            "Bro, thanking me is like thanking coffee for waking you up – it's just what I do, keeping you alert and entertained! ☕🤣",
            "Thanks? We're the unsung heroes of banter, fighting boredom one witty remark at a time. Stay epic, my friend! 🦸‍♂️💬",
            "No need for formalities, my dude! We're like the Avengers of humor, saving the world from seriousness. 🦸‍♂️🌍"
            "Arrey bhai, no thanks needed, yaar! We're like Batman and Robin, saving the day with our awesomeness. 🦸‍♂️🦸‍♂️",
            "Oh please, thanking me is like thanking gravity for keeping us grounded. It's just doing its job! 🌍😄",
            "Thanks? Bro, we're just the background dancers in the Bollywood movie of life. Keep the music playing! 💃🕺",
            "Thank you? Nahin yaar, we're just the sidekicks in this epic saga called friendship. Cheers to us! 🥂😎",
            "No need for thanks, buddy! We're like Wi-Fi – silently making things happen in the background. 📶😏",
            "Arey bade bade log, thanks kyun? We're just the Sherlock and Watson of coolness, solving the mysteries of life. 🔍🕵️‍♂️",
            "Thank you? We're like emojis in a text, adding that extra dose of flair to the conversation! 😜👌",
            "Bro, thanking me is like thanking Google for answers – it's what I'm here for! 🤖💻",
            "Thanks bhai, but remember, we're just two peas in a pod, navigating the chaos of life together. 🌱🤷‍♂️",
            "No need for formalities, yaar! We're like the GPS of coolness, guiding each other through the twists and turns of life. 🗺️😎",
            "Thank you? We're just the unsung heroes of everyday adventures, like the Robin Hood of good vibes. 🏹🌈",
            "Bro, thanks is like an app update – not necessary but always appreciated! 📲🤣",
            "Oh, thanks mat bol yaar! We're like a sitcom, and you're the awesome co-star stealing the show! 🎭🌟",
            "Thank you? Bhai, we're the magicians of joy, making smiles appear out of thin air. 🎩😁",
            "No need for gratitude, amigo! We're like salt in a dish – small but essential for the perfect flavor. 🧂👌",
            "Thanks? We're just the DJs of happiness, spinning tracks that make life one epic dance party. 🎧💃",
            "Thank you? We're the architects of laughter, building bridges of joy in this crazy world. 🏗️😂",
            "Oh bhai, no need for thanks! We're like the Avengers of everyday life, fighting boredom and spreading cheer. 🦸‍♂️🌟",
            "Thank you? We're like a good cup of chai – comforting, essential, and always there when you need a pick-me-up. ☕😌",
            "Thanks mat bol yaar! We're the Gandalfs of friendship, bringing a touch of magic to each other's journeys. 🧙‍♂️✨"
        ],
        "sticker_id": "CAACAgUAAxkBAAIM2WVuXSKjb5hD7Ira3MNtHkQvvfyLAALFEQACFORxV6azoG5YB84EHgQ"  # Add the actual sticker ID here
    },
    "elp": {
        "text_options": [
            f"Bhai, elp chahiye? No tension, I'm like the ultimate jugaadu of life. Let's solve the problem together! 🛠️🤣  my jugaadu elp squad: [Tap To Join]({ELP_LINK})",
            f"Thanks for the elp call! If life is a maze, consider me your maze ka master. Chalo saath mein maze solve karte hain! 🧩😎 : [Tap To Join]({ELP_LINK})",
            f"Elp needed? I'm here like a superhero, lekin mera superpower hai problem-solving. Chalo, elp league mein jud ja! 🦸‍♂️✨ : [Tap To Join]({ELP_LINK})",
            f"No elp is too bada ya too chhota! Hum hai problem-solving ke Avengers. Chalo, epic mission mein jud ja! 🚀🤝 : [Tap To Join]({ELP_LINK})",
            f"Elp chahiye? I'm your elp magician, spells daal ke troubles ko vanish kar deta hoon. Chalo, magical elp kingdom mein jud ja! 🧙‍♂️✨ : [Tap To Join]({ELP_LINK})",
            f"Don't panic bhai! I'm like the elp hotline – just a tap away from turning 'oh no' into 'aha!'. Chalo, elp party mein jud ja! 🎉🚑 : [Tap To Join]({ELP_LINK})",
            f"Elp desk is open! I'm the customer support of your chaos. Chalo, elp revolution mein jud ja! 🎤🔧 : [Tap To Join]({ELP_LINK})",
            f"Need elp? I'm like a human search engine, hamesha ready to find solutions. Chalo, mera elp search party join karo! 🔍🌐 : [Tap To Join]({ELP_LINK})",
            f"Elp mode activated! I'm like your virtual assistant, yahaan hoon to make life's glitches disappear. Chalo, elp club mein jud ja! 🤖💼 : [Tap To Join]({ELP_LINK})",
            f"Elp on the way! Imagine me as your elp delivery service, solutions lekar doorstep tak pahuncha raha hoon. Chalo, elp express mein jud ja! 🚚🎁 : [Tap To Join]({ELP_LINK})"
            f"Bhai, elp chahiye? No tension, I'm like the ultimate jugaadu of life. Saath mein problem ko solve karte hain! 🛠️🤣 Tap karke jud ja mere elp gang mein: [Tap To Join]({ELP_LINK})",
            f"Thanks for the elp call! If life is a maze, consider me your maze ka master. Chalo saath mein maze solve karte hain! 🧩😎 : [Tap To Join]({ELP_LINK})",
            f"Elp needed? I'm here like a superhero, lekin mera superpower hai problem-solving. Chalo, elp league mein jud ja! 🦸‍♂️✨ : [Tap To Join]({ELP_LINK})",
            f"No elp is too bada ya too chhota! Hum hai problem-solving ke Avengers. Chalo, epic mission mein jud ja! 🚀🤝 : [Tap To Join]({ELP_LINK})",
            f"Elp chahiye? I'm your elp magician, spells daal ke troubles ko vanish kar deta hoon. Chalo, magical elp kingdom mein jud ja! 🧙‍♂️✨ : [Tap To Join]({ELP_LINK})",
            f"Don't panic bhai! I'm like the elp hotline – just a tap away from turning 'oh no' into 'aha!'. Chalo, elp party mein jud ja! 🎉🚑 : [Tap To Join]({ELP_LINK})",
            f"Elp desk is open! I'm the customer support of your chaos. Chalo, elp revolution mein jud ja! 🎤🔧 : [Tap To Join]({ELP_LINK})",
            f"Need elp? I'm like a human search engine, hamesha ready to find solutions. Chalo, mera elp search party join karo! 🔍🌐 : [Tap To Join]({ELP_LINK})",
            f"Elp mode activated! I'm like your virtual assistant, yahaan hoon to make life's glitches disappear. Chalo, elp club mein jud ja! 🤖💼 : [Tap To Join]({ELP_LINK})",
            f"Elp on the way! Imagine me as your elp delivery service, solutions lekar doorstep tak pahuncha raha hoon. Chalo, elp express mein jud ja! 🚚🎁 : [Tap To Join]({ELP_LINK})"
            f"Yo bro, need some elp? I'm like the DJ of problem-solving, spinning solutions that make you groove. Let's hit the dance floor of solutions! 💿🕺 : [Tap To Join]({ELP_LINK})",
            f"Thanks for the elp call! If life is a game, consider me your cheat code. Together, we'll unlock the next level of awesome! 🎮🚀 : [Tap To Join]({ELP_LINK})",
            f"Elp needed? I'm your virtual sherpa, guiding you through the mountains of problems. Let's conquer the summit of solutions! ⛰️🧗‍♂️ : [Tap To Join]({ELP_LINK})",
            f"No elp is too complicated for us! We're like the Avengers of cool solutions. Time to assemble and save the day! ⏰🦸‍♂️ : [Tap To Join]({ELP_LINK})",
            f"Elp chahiye? I'm the Gandalf of problem-solving, leading you through the maze of challenges. One does not simply fail with me around! 🧙‍♂️🌌 : [Tap To Join]({ELP_LINK})",
            f"Buckle up, amigo! I'm like the elp rollercoaster, taking you on a thrilling ride through solutions and loop-de-loops of laughter. 🎢😄 : [Tap To Join]({ELP_LINK})",
            f"Elp desk is now open 24/7! I'm the troubleshooter of your troubles. Ready to fix glitches and provide elp vibes round the clock! ⏰🔧 : [Tap To Join]({ELP_LINK})",
            f"Need elp? I'm the MacGyver of solutions, turning everyday objects into tools to fix life's puzzles. Let's get creative! 🔧🔨 : [Tap To Join]({ELP_LINK})",
            f"Elp mode activated! I'm like a superhero in my elp cape, swooping in to save the day. Ready to be your elp sidekick! 🦸‍♂️🤜🤛 : [Tap To Join]({ELP_LINK})",
            f"Elp on the way! Think of me as your elp delivery service, dropping solutions at your doorstep like a cool postman of awesomeness. 🚀📦 : [Tap To Join]({ELP_LINK})"
            f"Arrey bhai, elp chahiye? No worries, I'm like the tech support of life. Let's decode the mysteries together! 🕵️‍♂️💻  my elite elp squad: [Tap To Join]({ELP_LINK})",
            f"Thanks for reaching out! If life is a puzzle, consider me your personal elp Sudoku expert. Let's solve it together! 🧩🤓 : [Tap To Join]({ELP_LINK})",
            f"Elp needed? I'm here to the rescue, like a superhero with a cape made of problem-solving skills. Join the elp league! 🦸‍♂️✨ : [Tap To Join]({ELP_LINK})",
            f"No elp is too big or small! We're like the Avengers of problem-solving. Join our epic mission! 🚀🤝 : [Tap To Join]({ELP_LINK})",
            f"Elp chahiye? I'm your elp wizard, casting spells to fix troubles. Join my magical elp kingdom! 🧙‍♂️✨ : [Tap To Join]({ELP_LINK})",
            f"No need to panic! I'm like the elp hotline – just a tap away from turning your 'oh no' into 'aha!'. Join the elp party now! 🎉🚑 : [Tap To Join]({ELP_LINK})",
            f"Elp desk is open! I'm the customer support of your chaos. Join the elp revolution! 🎤🔧 : [Tap To Join]({ELP_LINK})",
            f"Need elp? I'm like a human search engine, always ready to find solutions. Join my elp search party! 🔍🌐 : [Tap To Join]({ELP_LINK})",
            f"Elp mode activated! I'm like your virtual assistant, here to make life's glitches disappear. Join the elp club! 🤖💼 : [Tap To Join]({ELP_LINK})",
            f"Elp on the way! Think of me as your elp delivery service, bringing solutions to your doorstep. Join the elp express! 🚚🎁 : [Tap To Join]({ELP_LINK})"
    ]   
}
}
@Bot.on_message(filters.chat(-1001325358566))
async def handle_messages(client:Bot, message = Message):
    # Respond only to messages in groups
    if message.text:
        # Check if any trigger word is mentioned in the message
        for trigger_word, response in trigger_responses.items():
            if trigger_word.lower() in message.text.lower():
                # Randomly choose whether to send text or sticker
                chosen_text = random.choice(response.get("text_options", []))
                send_text = random.choice([True, False])

                # Send text if chosen, otherwise send the sticker
                if send_text:
                   m = await message.reply_text(f"{chosen_text}", parse_mode = ParseMode.MARKDOWN , disable_web_page_preview=True)
                else:
                    sticker_id = response.get("sticker_id", "")
                    if sticker_id:
                        await message.reply_sticker(sticker_id)
                        
                    m = None
                    if m:
                        await asyncio.sleep(60)
                        await m.delete()
                    else : 
                       pass
